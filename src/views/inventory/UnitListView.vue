<script setup>
import { ref, onMounted, watch } from 'vue'
import { useInventoryStore } from '@/stores/inventory'
import { usePagination } from '@/composables/usePagination'
import { formatDate } from '@/utils/date'
import { DEVICE_STATUS } from '@/utils/constants'
import AppTable from '@/components/ui/AppTable.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppPagination from '@/components/ui/AppPagination.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import { usePermissions } from '@/composables/usePermissions'

const inv   = useInventoryStore()
const pg    = usePagination({ pageSize: 30 })
const perms = usePermissions()
const search = ref('')
const statusFilter = ref('')

const STATUS_OPTIONS = [{ value: '', label: 'All Statuses' }, ...Object.values(DEVICE_STATUS).map(s => ({ value: s.value, label: s.label }))]

const columns = [
  { key: 'imei',     label: 'IMEI / Serial' },
  { key: 'product',  label: 'Product' },
  { key: 'status',   label: 'Status' },
  { key: 'cost',     label: 'Cost', align: 'right' },
  { key: 'price',    label: 'Sell Price', align: 'right' },
  { key: 'received', label: 'Received' },
]

async function load() {
  await inv.fetchUnits({
    search: search.value,
    status: statusFilter.value || undefined,
    ...pg.queryParams.value,
  })
}

watch([search, statusFilter, () => pg.currentPage.value], load)
onMounted(load)

function statusObj(val) {
  return Object.values(DEVICE_STATUS).find(s => s.value === val) || { label: val, badge: 'badge-gray' }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-3">
      <input v-model="search" type="search" class="input max-w-xs" placeholder="Search IMEI, SKU…" />
      <select v-model="statusFilter" class="input w-44">
        <option v-for="s in STATUS_OPTIONS" :key="s.value" :value="s.value">{{ s.label }}</option>
      </select>
      <div class="flex-1" />
      <span class="text-xs text-gray-500">{{ pg.totalCount.value.toLocaleString() }} units</span>
    </div>

    <AppTable :columns="columns" :loading="inv.loading" empty-message="No units found">
      <tr v-for="u in inv.units" :key="u.id">
        <td class="font-mono text-xs px-3 py-2.5">{{ u.imei }}</td>
        <td class="px-3 py-2.5">
          <RouterLink :to="`/inventory/products/${u.product_id}`" class="text-blue-700 hover:underline text-sm">
            {{ u.product_name }}
          </RouterLink>
        </td>
        <td class="px-3 py-2.5"><AppBadge :status="statusObj(u.status)" /></td>
        <td class="px-3 py-2.5 text-right"><MoneyDisplay :value="u.cost_price" :mask="!perms.canViewCost.value" /></td>
        <td class="px-3 py-2.5 text-right"><MoneyDisplay :value="u.sell_price" /></td>
        <td class="px-3 py-2.5 text-sm text-gray-500">{{ formatDate(u.received_at) }}</td>
      </tr>
    </AppTable>

    <AppPagination v-bind="{ currentPage: pg.currentPage.value, totalPages: pg.totalPages.value, totalCount: pg.totalCount.value, pageSize: pg.pageSize.value }" @page="pg.goTo" />
  </div>
</template>
