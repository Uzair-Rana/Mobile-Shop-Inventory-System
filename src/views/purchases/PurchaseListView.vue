<script setup>
import { ref, onMounted, watch } from 'vue'
import { purchasesApi } from '@/api/purchases'
import { usePagination } from '@/composables/usePagination'
import { formatDate } from '@/utils/date'
import { PO_STATUS } from '@/utils/constants'
import AppTable from '@/components/ui/AppTable.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppPagination from '@/components/ui/AppPagination.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'

const pg      = usePagination({ pageSize: 25 })
const orders  = ref([])
const loading = ref(false)
const search  = ref('')
const status  = ref('')

const STATUS_OPTIONS = [
  { value: '', label: 'All' },
  ...Object.values(PO_STATUS).map(s => ({ value: s.value, label: s.label }))
]

const columns = [
  { key: 'po_number', label: 'PO #' },
  { key: 'supplier',  label: 'Supplier' },
  { key: 'date',      label: 'Date' },
  { key: 'status',    label: 'Status' },
  { key: 'items',     label: 'Items',  align: 'right' },
  { key: 'total',     label: 'Total',  align: 'right' },
  { key: 'paid',      label: 'Paid',   align: 'right' },
]

async function load() {
  loading.value = true
  try {
    const res = await purchasesApi.listOrders({ search: search.value || undefined, status: status.value || undefined, ...pg.queryParams.value })
    orders.value = res.data.results ?? res.data
    pg.setFromResponse({ count: res.data.count ?? orders.value.length })
  } finally { loading.value = false }
}

watch([search, status, () => pg.currentPage.value], load)
onMounted(load)

function statusObj(val) {
  return Object.values(PO_STATUS).find(s => s.value === val) || { label: val, badge: 'badge-gray' }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-3">
      <input v-model="search" type="search" class="input max-w-xs" placeholder="PO #, supplier…" />
      <select v-model="status" class="input w-40">
        <option v-for="s in STATUS_OPTIONS" :key="s.value" :value="s.value">{{ s.label }}</option>
      </select>
      <div class="flex-1" />
      <RouterLink to="/purchases/orders/new" class="btn btn-primary">+ New PO</RouterLink>
    </div>
    <AppTable :columns="columns" :loading="loading" empty-message="No purchase orders">
      <tr v-for="o in orders" :key="o.id">
        <td class="px-3 py-2.5">
          <RouterLink :to="`/purchases/orders/${o.id}`" class="font-medium text-blue-700 hover:underline">#{{ o.po_number }}</RouterLink>
        </td>
        <td class="px-3 py-2.5 text-sm">{{ o.supplier_name }}</td>
        <td class="px-3 py-2.5 text-sm text-gray-500">{{ formatDate(o.created_at) }}</td>
        <td class="px-3 py-2.5"><AppBadge :status="statusObj(o.status)" /></td>
        <td class="px-3 py-2.5 text-right text-sm">{{ o.line_count }}</td>
        <td class="px-3 py-2.5 text-right"><MoneyDisplay :value="o.total_amount" /></td>
        <td class="px-3 py-2.5 text-right"><MoneyDisplay :value="o.amount_paid" /></td>
      </tr>
    </AppTable>
    <AppPagination v-bind="{ currentPage: pg.currentPage.value, totalPages: pg.totalPages.value, totalCount: pg.totalCount.value, pageSize: pg.pageSize.value }" @page="pg.goTo" />
  </div>
</template>
