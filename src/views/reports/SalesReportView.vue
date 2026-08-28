<script setup>
import { ref, onMounted } from 'vue'
import { reportsApi } from '@/api/reports'
import { useUiStore } from '@/stores/ui'
import { formatDate } from '@/utils/date'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import AppButton from '@/components/ui/AppButton.vue'

const ui      = useUiStore()
const loading = ref(false)
const data    = ref(null)
const filters = ref({
  date_from: new Date(new Date().setDate(1)).toISOString().slice(0, 10),
  date_to:   new Date().toISOString().slice(0, 10),
  group_by:  'day',
})

async function load() {
  loading.value = true
  try {
    const res = await reportsApi.salesSummary(filters.value)
    data.value  = res.data
  } catch (e) {
    ui.toastError(e.displayMessage || 'Failed to load report')
  } finally { loading.value = false }
}

async function exportCsv() {
  try {
    const res = await reportsApi.exportCsv('sales-summary', filters.value)
    const url = URL.createObjectURL(res.data)
    const a   = document.createElement('a'); a.href = url; a.download = 'sales-report.csv'; a.click()
    URL.revokeObjectURL(url)
  } catch { ui.toastError('Export failed') }
}

onMounted(load)
</script>

<template>
  <div class="space-y-5">
    <!-- Filters -->
    <div class="card p-4 flex flex-wrap items-end gap-4">
      <div>
        <label class="label">From</label>
        <input v-model="filters.date_from" type="date" class="input w-36" />
      </div>
      <div>
        <label class="label">To</label>
        <input v-model="filters.date_to" type="date" class="input w-36" />
      </div>
      <div>
        <label class="label">Group By</label>
        <select v-model="filters.group_by" class="input">
          <option value="day">Day</option>
          <option value="week">Week</option>
          <option value="month">Month</option>
        </select>
      </div>
      <AppButton variant="primary" :loading="loading" @click="load">Run Report</AppButton>
      <AppButton variant="secondary" @click="exportCsv">Export CSV</AppButton>
    </div>

    <!-- Summary KPIs -->
    <div v-if="data" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="card p-4"><p class="text-xs text-gray-500 uppercase">Total Sales</p><MoneyDisplay :value="data.total_sales" class="text-xl font-bold text-gray-900 block mt-1" /></div>
      <div class="card p-4"><p class="text-xs text-gray-500 uppercase">Invoices</p><p class="text-xl font-bold text-gray-900 mt-1">{{ data.invoice_count }}</p></div>
      <div class="card p-4"><p class="text-xs text-gray-500 uppercase">Avg Invoice</p><MoneyDisplay :value="data.avg_invoice" class="text-xl font-bold text-gray-900 block mt-1" /></div>
      <div class="card p-4"><p class="text-xs text-gray-500 uppercase">Cash Collected</p><MoneyDisplay :value="data.cash_collected" class="text-xl font-bold text-green-700 block mt-1" /></div>
    </div>

    <!-- Period breakdown -->
    <div v-if="data?.periods" class="card overflow-hidden">
      <div class="px-4 py-3 border-b border-gray-100 font-semibold text-sm">Period Breakdown</div>
      <table class="table-base">
        <thead><tr><th>Period</th><th class="text-right">Invoices</th><th class="text-right">Sales</th><th class="text-right">Discounts</th></tr></thead>
        <tbody>
          <tr v-for="row in data.periods" :key="row.period">
            <td class="px-3 py-2 text-sm">{{ row.period }}</td>
            <td class="px-3 py-2 text-right text-sm">{{ row.invoice_count }}</td>
            <td class="px-3 py-2 text-right"><MoneyDisplay :value="row.total_sales" /></td>
            <td class="px-3 py-2 text-right"><MoneyDisplay :value="row.total_discounts" /></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
