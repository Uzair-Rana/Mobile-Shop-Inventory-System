<script setup>
import { ref, onMounted, watch } from 'vue'
import { salesApi } from '@/api/sales'
import { usePagination } from '@/composables/usePagination'
import { formatDate, formatDateTime } from '@/utils/date'
import { INVOICE_STATUS } from '@/utils/constants'
import AppTable from '@/components/ui/AppTable.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppPagination from '@/components/ui/AppPagination.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'

const pg       = usePagination({ pageSize: 25 })
const invoices = ref([])
const loading  = ref(false)
const search   = ref('')
const status   = ref('')
const dateFrom = ref('')
const dateTo   = ref('')

const STATUS_OPTIONS = [
  { value: '', label: 'All' },
  ...Object.values(INVOICE_STATUS).map(s => ({ value: s.value, label: s.label }))
]

const columns = [
  { key: 'inv',      label: 'Invoice #' },
  { key: 'date',     label: 'Date',     sortable: true },
  { key: 'customer', label: 'Customer' },
  { key: 'items',    label: 'Items',    align: 'right' },
  { key: 'total',    label: 'Total',    align: 'right' },
  { key: 'paid',     label: 'Paid',     align: 'right' },
  { key: 'status',   label: 'Status' },
]

async function load() {
  loading.value = true
  try {
    const res = await salesApi.listInvoices({
      search: search.value || undefined,
      status: status.value || undefined,
      date_from: dateFrom.value || undefined,
      date_to:   dateTo.value   || undefined,
      ...pg.queryParams.value,
    })
    invoices.value = res.data.results ?? res.data
    pg.setFromResponse({ count: res.data.count ?? invoices.value.length })
  } finally { loading.value = false }
}

watch([search, status, dateFrom, dateTo, () => pg.currentPage.value], load)
onMounted(load)

function statusObj(val) {
  return Object.values(INVOICE_STATUS).find(s => s.value === val) || { label: val, badge: 'badge-gray' }
}
</script>

<template>
  <div class="space-y-4">
    <!-- Filters -->
    <div class="flex flex-wrap items-center gap-3">
      <input v-model="search"   type="search" class="input w-48" placeholder="Invoice #, customer…" />
      <select v-model="status"  class="input w-40">
        <option v-for="s in STATUS_OPTIONS" :key="s.value" :value="s.value">{{ s.label }}</option>
      </select>
      <input v-model="dateFrom" type="date" class="input w-36" />
      <span class="text-gray-400 text-sm">to</span>
      <input v-model="dateTo"   type="date" class="input w-36" />
      <div class="flex-1" />
      <RouterLink to="/pos" class="btn btn-primary btn-sm">New Sale (POS)</RouterLink>
    </div>

    <AppTable :columns="columns" :loading="loading" empty-message="No invoices found">
      <tr v-for="inv in invoices" :key="inv.id" class="cursor-pointer">
        <td class="px-3 py-2.5">
          <RouterLink :to="`/sales/invoices/${inv.id}`" class="font-medium text-blue-700 hover:underline">
            #{{ inv.invoice_number }}
          </RouterLink>
        </td>
        <td class="px-3 py-2.5 text-sm text-gray-600">{{ formatDate(inv.created_at) }}</td>
        <td class="px-3 py-2.5 text-sm">{{ inv.customer_name || 'Walk-in' }}</td>
        <td class="px-3 py-2.5 text-right text-sm">{{ inv.line_count }}</td>
        <td class="px-3 py-2.5 text-right"><MoneyDisplay :value="inv.grand_total" /></td>
        <td class="px-3 py-2.5 text-right"><MoneyDisplay :value="inv.amount_paid" /></td>
        <td class="px-3 py-2.5"><AppBadge :status="statusObj(inv.status)" /></td>
      </tr>
    </AppTable>

    <AppPagination v-bind="{ currentPage: pg.currentPage.value, totalPages: pg.totalPages.value, totalCount: pg.totalCount.value, pageSize: pg.pageSize.value }" @page="pg.goTo" />
  </div>
</template>
