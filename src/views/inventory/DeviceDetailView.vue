<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMockDataStore } from '@/stores/mockData'
import { useUiStore } from '@/stores/ui'
import { useStepUpAuth } from '@/composables/useStepUpAuth'
import { formatDate, formatDateTime } from '@/utils/date'
import { formatMoney } from '@/utils/money'
import { DEVICE_STATUS } from '@/utils/constants'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppTabs from '@/components/ui/AppTabs.vue'
import AppTimeline from '@/components/ui/AppTimeline.vue'
import AppModal from '@/components/ui/AppModal.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import PermGate from '@/components/ui/PermGate.vue'

const route  = useRoute()
const router = useRouter()
const mock   = useMockDataStore()
const ui     = useUiStore()
const { requireStepUp } = useStepUpAuth()

const device   = ref(null)
const timeline = ref([])
const activeTab = ref('identity')

const tabs = [
  { key: 'identity',   label: 'Identity' },
  { key: 'condition',  label: 'Condition' },
  { key: 'commercial', label: 'Commercial' },
  { key: 'timeline',   label: 'Timeline' },
]

onMounted(() => {
  device.value  = mock.getDevice(route.params.id)
  timeline.value = mock.getDeviceTimeline(route.params.id)
  if (!device.value) router.replace('/inventory/devices')
})

function statusObj(val) {
  return Object.values(DEVICE_STATUS).find(s => s.value === val) || { label: val, badge: 'badge-gray' }
}

// Cost adjustment
const showCostModal = ref(false)
const newCostPrice  = ref(0)
const costReason    = ref('')
const adjusting     = ref(false)

async function openCostAdjust() {
  const ok = await requireStepUp('Adjust device cost price')
  if (!ok) return
  newCostPrice.value = device.value.cost_price
  costReason.value   = ''
  showCostModal.value = true
}

function saveCostAdjust() {
  if (!newCostPrice.value) { ui.toastWarn('Enter a valid cost price'); return }
  adjusting.value = true
  const oldCost = device.value.cost_price
  mock.updateDevice(device.value.id, { cost_price: Number(newCostPrice.value) })
  mock.addAuditLog({
    actor: 'admin',
    action: 'update',
    entity_type: 'Device',
    entity_id: String(device.value.id),
    changes: { cost_price: { before: oldCost, after: Number(newCostPrice.value) }, reason: costReason.value },
  })
  device.value = mock.getDevice(route.params.id)
  ui.toastSuccess('Cost price updated')
  showCostModal.value = false
  adjusting.value = false
}
</script>

<template>
  <div v-if="device" class="space-y-3 max-w-4xl">
    <!-- Header -->
    <div class="flex items-start justify-between flex-wrap gap-3">
      <div>
        <div class="flex items-center gap-3">
          <h2 class="text-xl font-bold text-gray-900">{{ device.brand }} {{ device.model }}</h2>
          <AppBadge :status="statusObj(device.lifecycle_state)" />
        </div>
        <p class="text-sm text-gray-500 font-mono mt-1">{{ device.imei1 }}</p>
      </div>
      <div class="flex gap-2">
        <AppButton variant="ghost" @click="router.back()">← Back</AppButton>
      </div>
    </div>

    <!-- Tabs -->
    <AppTabs :tabs="tabs" v-model="activeTab" />

    <!-- Tab: Identity -->
    <div v-show="activeTab === 'identity'" class="card p-4">
      <div class="grid grid-cols-2 gap-4 text-sm">
        <div><p class="label">IMEI 1</p><p class="font-mono">{{ device.imei1 || '—' }}</p></div>
        <div><p class="label">IMEI 2</p><p class="font-mono">{{ device.imei2 || '—' }}</p></div>
        <div><p class="label">Serial</p><p class="font-mono">{{ device.serial || '—' }}</p></div>
        <div><p class="label">Brand</p><p>{{ device.brand }}</p></div>
        <div><p class="label">Model</p><p>{{ device.model }}</p></div>
        <div><p class="label">Branch</p><p>Branch #{{ device.branch_id }}</p></div>
        <div><p class="label">Added</p><p>{{ formatDate(device.created_at) }}</p></div>
        <div><p class="label">PTA Status</p>
          <span :class="device.pta_status === 'PTA Approved' ? 'badge badge-green' : 'badge badge-red'">
            <span class="h-1.5 w-1.5 rounded-full bg-current opacity-60 shrink-0" />
            {{ device.pta_status }}
          </span>
        </div>
      </div>
    </div>

    <!-- Tab: Condition -->
    <div v-show="activeTab === 'condition'" class="card p-4">
      <div class="grid grid-cols-2 gap-4 text-sm">
        <div><p class="label">Condition Grade</p><p class="font-semibold">{{ device.condition }}</p></div>
        <div><p class="label">Lifecycle State</p><AppBadge :status="statusObj(device.lifecycle_state)" /></div>
      </div>
    </div>

    <!-- Tab: Commercial (PermGate) -->
    <div v-show="activeTab === 'commercial'">
      <PermGate perm="view_cost">
        <div class="card p-4 space-y-4">
          <div class="grid grid-cols-3 gap-4">
            <div class="stat-cell">
              <span class="stat-label">Cost Price</span>
              <MoneyDisplay :value="device.cost_price" class="stat-value" />
            </div>
            <div class="stat-cell">
              <span class="stat-label">Sell Price</span>
              <MoneyDisplay :value="device.sell_price" class="stat-value text-blue-700" />
            </div>
            <div class="stat-cell">
              <span class="stat-label">Margin</span>
              <p class="stat-value text-green-700">
                {{ device.cost_price > 0 ? (((device.sell_price - device.cost_price) / device.sell_price) * 100).toFixed(1) : '—' }}%
              </p>
            </div>
          </div>

          <div class="flex gap-2">
            <AppButton variant="secondary" @click="openCostAdjust">Adjust Cost Price</AppButton>
          </div>
        </div>
      </PermGate>
      <div v-if="!$perms" class="card p-4 text-center text-sm text-gray-400">
        You do not have permission to view commercial data.
      </div>
    </div>

    <!-- Tab: Timeline -->
    <div v-show="activeTab === 'timeline'" class="card p-4">
      <AppTimeline :events="timeline" />
      <p v-if="!timeline.length" class="text-sm text-gray-400 text-center py-4">No history recorded for this device</p>
    </div>

    <!-- Cost adjustment modal -->
    <AppModal :open="showCostModal" title="Adjust Cost Price" size="sm" @close="showCostModal = false">
      <div class="space-y-3">
        <div>
          <label class="label">New Cost Price (Rs.)</label>
          <input v-model.number="newCostPrice" type="number" min="0" step="100" class="input" />
        </div>
        <div>
          <label class="label">Reason</label>
          <input v-model="costReason" type="text" class="input" placeholder="e.g. Supplier price correction" />
        </div>
      </div>
      <template #footer>
        <AppButton variant="secondary" @click="showCostModal = false">Cancel</AppButton>
        <AppButton variant="primary" :loading="adjusting" @click="saveCostAdjust">Save</AppButton>
      </template>
    </AppModal>
  </div>
  <div v-else class="text-center py-20 text-gray-400">Loading…</div>
</template>
