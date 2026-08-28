<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { repairsApi } from '@/api/repairs'
import { useUiStore } from '@/stores/ui'
import { useConfirm } from '@/composables/useConfirm'
import { usePermissions } from '@/composables/usePermissions'
import { formatDate, formatDateTime } from '@/utils/date'
import { formatMoney } from '@/utils/money'
import { REPAIR_STATUS } from '@/utils/constants'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppSelect from '@/components/ui/AppSelect.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'

const route  = useRoute()
const router = useRouter()
const ui     = useUiStore()
const { confirm } = useConfirm()
const perms  = usePermissions()

const job     = ref(null)
const loading = ref(true)

// Status update
const showStatusModal  = ref(false)
const newStatus        = ref('')
const statusNote       = ref('')
const updatingStatus   = ref(false)

// Delivery modal
const showDeliveryModal = ref(false)
const deliveryPayment   = ref(0)
const delivering        = ref(false)

const isDelivered  = computed(() => ['delivered', 'cancelled'].includes(job.value?.status))
const balanceDue   = computed(() => {
  if (!job.value) return 0
  return Math.max(0, (job.value.final_cost || job.value.estimated_cost || 0) - (job.value.advance_payment || 0))
})

const NEXT_STATUSES = computed(() => {
  const all = Object.values(REPAIR_STATUS)
  return all.filter(s => s.value !== job.value?.status)
    .map(s => ({ value: s.value, label: s.label }))
})

onMounted(async () => {
  const res = await repairsApi.getJob(route.params.id)
  job.value = res.data
  loading.value = false
})

function statusObj(val) {
  return Object.values(REPAIR_STATUS).find(s => s.value === val) || { label: val, badge: 'badge-gray' }
}

async function handleStatusUpdate() {
  if (!newStatus.value) return
  updatingStatus.value = true
  try {
    await repairsApi.updateStatus(job.value.id, { status: newStatus.value, note: statusNote.value })
    ui.toastSuccess(`Status updated to: ${statusObj(newStatus.value).label}`)
    showStatusModal.value = false
    const res = await repairsApi.getJob(job.value.id)
    job.value = res.data
  } catch (e) {
    ui.toastError(e.displayMessage || 'Update failed')
  } finally { updatingStatus.value = false }
}

async function handleDeliver() {
  const bal = balanceDue.value
  const effect = bal > 0
    ? `Collects ${formatMoney(deliveryPayment.value)} balance payment and marks job as Delivered.`
    : 'Marks repair job as Delivered.'

  const ok = await confirm({
    title:  'Deliver Device',
    message: `Confirm delivery to ${job.value.customer_name}`,
    effect,
    confirmLabel: 'Deliver',
    confirmClass: 'btn-primary',
  })
  if (!ok) return
  delivering.value = true
  try {
    await repairsApi.deliver(job.value.id, { payment: deliveryPayment.value })
    ui.toastSuccess('Device delivered')
    showDeliveryModal.value = false
    const res = await repairsApi.getJob(job.value.id)
    job.value = res.data
  } catch (e) {
    ui.toastError(e.displayMessage || 'Delivery failed')
  } finally { delivering.value = false }
}
</script>

<template>
  <div v-if="!loading && job" class="space-y-6 max-w-4xl">
    <!-- Header -->
    <div class="flex items-start justify-between flex-wrap gap-3">
      <div>
        <div class="flex items-center gap-3">
          <h2 class="text-xl font-bold text-gray-900">Repair Job #{{ job.job_number }}</h2>
          <AppBadge :status="statusObj(job.status)" />
        </div>
        <p class="text-sm text-gray-500 mt-1">
          Received {{ formatDate(job.received_at) }} &nbsp;·&nbsp;
          {{ job.technician_name || 'Unassigned' }}
        </p>
      </div>
      <div class="flex gap-2 flex-wrap">
        <template v-if="!isDelivered">
          <AppButton variant="secondary" @click="showStatusModal = true">Update Status</AppButton>
          <AppButton variant="primary" @click="showDeliveryModal = true">Deliver Device</AppButton>
        </template>
        <AppButton variant="ghost" @click="router.back()">← Back</AppButton>
      </div>
    </div>

    <!-- Detail grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Customer + Device -->
      <div class="card p-4 space-y-3">
        <p class="text-xs font-semibold uppercase text-gray-500 tracking-wide">Customer</p>
        <p class="font-medium text-gray-900">{{ job.customer_name }}</p>
        <p class="text-sm text-gray-500">{{ job.customer_phone }}</p>
        <hr class="border-gray-100"/>
        <p class="text-xs font-semibold uppercase text-gray-500 tracking-wide">Device</p>
        <p class="font-medium text-gray-900">{{ job.device_model }}</p>
        <p class="font-mono text-xs text-gray-500">{{ job.imei || '—' }}</p>
      </div>

      <!-- Financials -->
      <div class="card p-4 space-y-3">
        <p class="text-xs font-semibold uppercase text-gray-500 tracking-wide">Financials</p>
        <div class="space-y-2 text-sm">
          <div class="flex justify-between"><span class="text-gray-600">Estimate</span><MoneyDisplay :value="job.estimated_cost" /></div>
          <div class="flex justify-between"><span class="text-gray-600">Final Cost</span><MoneyDisplay :value="job.final_cost" /></div>
          <div class="flex justify-between"><span class="text-gray-600">Advance</span><MoneyDisplay :value="job.advance_payment" /></div>
          <hr class="border-gray-100" />
          <div class="flex justify-between font-semibold" :class="balanceDue > 0 ? 'text-red-600' : 'text-green-700'">
            <span>Balance Due</span>
            <MoneyDisplay :value="balanceDue" />
          </div>
        </div>
      </div>
    </div>

    <!-- Issue + notes -->
    <div class="card p-4 space-y-2">
      <p class="text-xs font-semibold uppercase text-gray-500 tracking-wide">Issue Description</p>
      <p class="text-sm text-gray-800">{{ job.issue_description }}</p>
      <p v-if="job.accessories_received" class="text-xs text-gray-500 mt-2">
        <span class="font-medium">Accessories received:</span> {{ job.accessories_received }}
      </p>
    </div>

    <!-- Status timeline -->
    <div class="card p-4">
      <p class="text-xs font-semibold uppercase text-gray-500 tracking-wide mb-3">Status History</p>
      <div class="space-y-2">
        <div
          v-for="log in job.status_logs"
          :key="log.id"
          class="flex items-start gap-3 text-sm"
        >
          <AppBadge :status="statusObj(log.status)" class="shrink-0 mt-0.5" />
          <div class="flex-1">
            <span class="text-gray-700">{{ log.note || '—' }}</span>
            <span class="text-xs text-gray-400 ml-2">by {{ log.updated_by_name }}</span>
          </div>
          <span class="text-xs text-gray-400 whitespace-nowrap">{{ formatDateTime(log.created_at) }}</span>
        </div>
        <p v-if="!job.status_logs?.length" class="text-sm text-gray-400">No status updates yet</p>
      </div>
    </div>

    <!-- Update status modal -->
    <AppModal :open="showStatusModal" title="Update Repair Status" size="sm" @close="showStatusModal = false">
      <div class="space-y-3">
        <AppSelect v-model="newStatus" label="New Status" :options="NEXT_STATUSES" />
        <div>
          <label class="label">Note</label>
          <textarea v-model="statusNote" class="input" rows="2" placeholder="What was done / what's next…" />
        </div>
      </div>
      <template #footer>
        <AppButton variant="secondary" @click="showStatusModal = false">Cancel</AppButton>
        <AppButton variant="primary" :loading="updatingStatus" @click="handleStatusUpdate">Update Status</AppButton>
      </template>
    </AppModal>

    <!-- Delivery modal -->
    <AppModal :open="showDeliveryModal" title="Deliver Device" size="sm" @close="showDeliveryModal = false">
      <div class="space-y-4">
        <div class="bg-blue-50 border border-blue-200 rounded-md p-3 text-sm text-blue-800">
          Balance due: <strong><MoneyDisplay :value="balanceDue" /></strong>
        </div>
        <div v-if="balanceDue > 0">
          <label class="label">Collect Payment</label>
          <input v-model.number="deliveryPayment" type="number" :max="balanceDue" min="0" class="input" />
        </div>
      </div>
      <template #footer>
        <AppButton variant="secondary" @click="showDeliveryModal = false">Cancel</AppButton>
        <AppButton variant="primary" :loading="delivering" @click="handleDeliver">Confirm Delivery</AppButton>
      </template>
    </AppModal>
  </div>
  <div v-else class="text-center py-20 text-gray-400">Loading…</div>
</template>
