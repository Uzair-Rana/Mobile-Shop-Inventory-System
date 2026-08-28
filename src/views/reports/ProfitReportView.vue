<script setup>
import { ref, onMounted } from 'vue'
import { reportsApi } from '@/api/reports'
import { usePermissions } from '@/composables/usePermissions'
import { useUiStore } from '@/stores/ui'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import AppButton from '@/components/ui/AppButton.vue'

const ui    = useUiStore()
const perms = usePermissions()
const data  = ref(null)
const loading = ref(false)
const filters = ref({
  date_from: new Date(new Date().setDate(1)).toISOString().slice(0, 10),
  date_to:   new Date().toISOString().slice(0, 10),
})

async function load() {
  loading.value = true
  try {
    const res = await reportsApi.profitLoss(filters.value)
    data.value  = res.data
  } catch (e) {
    ui.toastError(e.displayMessage || 'Failed to load P&L')
  } finally { loading.value = false }
}

onMounted(load)
</script>

<template>
  <!-- Permission gate: even if route guard is set, double-check here -->
  <div v-if="!perms.canViewProfit.value" class="card p-12 text-center text-gray-400">
    <svg class="w-12 h-12 mx-auto mb-3 opacity-30" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z"/>
    </svg>
    <p class="font-semibold text-gray-600">Access Restricted</p>
    <p class="text-sm mt-1">You don't have permission to view profit data.</p>
  </div>

  <div v-else class="space-y-5">
    <div class="card p-4 flex flex-wrap items-end gap-4">
      <div><label class="label">From</label><input v-model="filters.date_from" type="date" class="input w-36" /></div>
      <div><label class="label">To</label><input v-model="filters.date_to" type="date" class="input w-36" /></div>
      <AppButton variant="primary" :loading="loading" @click="load">Run Report</AppButton>
    </div>

    <div v-if="data" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="card p-4"><p class="text-xs text-gray-500 uppercase">Revenue</p><MoneyDisplay :value="data.revenue" class="text-xl font-bold text-gray-900 block mt-1" /></div>
      <div class="card p-4"><p class="text-xs text-gray-500 uppercase">COGS</p><MoneyDisplay :value="data.cost_of_goods" class="text-xl font-bold text-gray-900 block mt-1" /></div>
      <div class="card p-4"><p class="text-xs text-gray-500 uppercase">Gross Profit</p><MoneyDisplay :value="data.gross_profit" class="text-xl font-bold text-green-700 block mt-1" /></div>
      <div class="card p-4">
        <p class="text-xs text-gray-500 uppercase">Margin</p>
        <p class="text-xl font-bold mt-1" :class="data.gross_margin >= 0 ? 'text-green-700' : 'text-red-600'">
          {{ data.gross_margin?.toFixed(1) }}%
        </p>
      </div>
    </div>

    <div v-if="data?.breakdown" class="card overflow-hidden">
      <div class="px-4 py-3 border-b border-gray-100 font-semibold text-sm">Category Breakdown</div>
      <table class="table-base">
        <thead><tr><th>Category</th><th class="text-right">Revenue</th><th class="text-right">COGS</th><th class="text-right">GP</th><th class="text-right">Margin</th></tr></thead>
        <tbody>
          <tr v-for="row in data.breakdown" :key="row.category">
            <td class="px-3 py-2">{{ row.category }}</td>
            <td class="px-3 py-2 text-right"><MoneyDisplay :value="row.revenue" /></td>
            <td class="px-3 py-2 text-right"><MoneyDisplay :value="row.cogs" /></td>
            <td class="px-3 py-2 text-right font-semibold text-green-700"><MoneyDisplay :value="row.gross_profit" /></td>
            <td class="px-3 py-2 text-right">{{ row.margin?.toFixed(1) }}%</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
