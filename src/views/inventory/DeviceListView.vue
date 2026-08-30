<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMockDataStore } from '@/stores/mockData'
import { usePermissions } from '@/composables/usePermissions'
import { formatMoney } from '@/utils/money'
import { formatDate } from '@/utils/date'
import { DEVICE_STATUS } from '@/utils/constants'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import PermGate from '@/components/ui/PermGate.vue'

const mock   = useMockDataStore()
const router = useRouter()
const perms  = usePermissions()

const search     = ref('')
const filterBrand= ref('')
const filterState= ref('')

const brands = computed(() => [...new Set(mock.devices.map(d => d.brand))])

const filtered = computed(() => {
  let list = mock.devices
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(d =>
      d.imei1?.toLowerCase().includes(q) ||
      d.imei2?.toLowerCase().includes(q) ||
      d.brand?.toLowerCase().includes(q) ||
      d.model?.toLowerCase().includes(q) ||
      d.serial?.toLowerCase().includes(q)
    )
  }
  if (filterBrand.value) list = list.filter(d => d.brand === filterBrand.value)
  if (filterState.value) list = list.filter(d => d.lifecycle_state === filterState.value)
  return list
})

function statusObj(val) {
  return Object.values(DEVICE_STATUS).find(s => s.value === val) || { label: val, badge: 'badge-gray' }
}
</script>

<template>
  <div class="space-y-3">
    <!-- Toolbar -->
    <div class="flex flex-wrap items-center gap-2">
      <input v-model="search" type="search" class="input max-w-xs" placeholder="Search IMEI, model, brand…" data-no-scanner-refocus />
      <select v-model="filterBrand" class="input w-36" data-no-scanner-refocus>
        <option value="">All Brands</option>
        <option v-for="b in brands" :key="b" :value="b">{{ b }}</option>
      </select>
      <select v-model="filterState" class="input w-36" data-no-scanner-refocus>
        <option value="">All States</option>
        <option value="in_stock">In Stock</option>
        <option value="sold">Sold</option>
        <option value="in_repair">In Repair</option>
        <option value="reserved">Reserved</option>
        <option value="transferred">Transferred</option>
      </select>
      <div class="flex-1" />
      <AppButton variant="secondary" @click="router.push('/inventory/devices/new')">+ Add Device</AppButton>
    </div>

    <!-- Table -->
    <div class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="table-base">
          <thead>
            <tr>
              <th>IMEI1</th>
              <th>Brand / Model</th>
              <th>Condition</th>
              <th>PTA</th>
              <th>State</th>
              <PermGate perm="view_cost">
                <th class="text-right">Cost</th>
              </PermGate>
              <th class="text-right">Sell Price</th>
              <th>Added</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="d in filtered"
              :key="d.id"
              class="cursor-pointer"
              @click="router.push(`/inventory/devices/${d.id}`)"
            >
              <td class="font-mono text-xs text-gray-600">{{ d.imei1 }}</td>
              <td>
                <p class="font-medium text-gray-900">{{ d.brand }} {{ d.model }}</p>
                <p class="text-[10px] text-gray-400">S/N: {{ d.serial }}</p>
              </td>
              <td>
                <span class="badge badge-gray">{{ d.condition }}</span>
              </td>
              <td>
                <span :class="d.pta_status === 'PTA Approved' ? 'badge badge-green' : 'badge badge-red'">
                  <span class="h-1.5 w-1.5 rounded-full bg-current opacity-60 shrink-0" aria-hidden="true" />
                  {{ d.pta_status }}
                </span>
              </td>
              <td><AppBadge :status="statusObj(d.lifecycle_state)" /></td>
              <PermGate perm="view_cost">
                <td class="text-right"><MoneyDisplay :value="d.cost_price" /></td>
              </PermGate>
              <td class="text-right font-medium"><MoneyDisplay :value="d.sell_price" /></td>
              <td class="text-xs text-gray-500">{{ formatDate(d.created_at) }}</td>
              <td>
                <RouterLink
                  :to="`/inventory/devices/${d.id}`"
                  class="text-xs text-blue-600 hover:underline"
                  @click.stop
                >View</RouterLink>
              </td>
            </tr>
            <tr v-if="filtered.length === 0">
              <td colspan="10" class="py-8 text-center text-xs text-gray-400">No devices found</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <p class="text-xs text-gray-400">{{ filtered.length }} of {{ mock.devices.length }} devices</p>
  </div>
</template>
