<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { suppliersApi } from '@/api/suppliers'
import { formatDate } from '@/utils/date'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import AppButton from '@/components/ui/AppButton.vue'

const route    = useRoute()
const router   = useRouter()
const supplier = ref(null)
const ledger   = ref([])
const loading  = ref(true)

onMounted(async () => {
  const [sRes, lRes] = await Promise.all([
    suppliersApi.getSupplier(route.params.id),
    suppliersApi.getLedger(route.params.id),
  ])
  supplier.value = sRes.data
  ledger.value   = lRes.data.results ?? lRes.data
  loading.value  = false
})
</script>

<template>
  <div v-if="!loading && supplier" class="space-y-6 max-w-3xl">
    <div class="flex items-start justify-between">
      <div>
        <h2 class="text-xl font-bold text-gray-900">{{ supplier.name }}</h2>
        <p class="text-sm text-gray-500">{{ supplier.phone }} &nbsp;·&nbsp; {{ supplier.email }}</p>
      </div>
      <AppButton variant="ghost" @click="router.back()">← Back</AppButton>
    </div>

    <div class="grid grid-cols-3 gap-4">
      <div class="card p-4"><p class="text-xs text-gray-500 uppercase">Total Purchased</p><MoneyDisplay :value="supplier.total_purchased" class="text-xl font-bold text-gray-900 block mt-1" /></div>
      <div class="card p-4"><p class="text-xs text-gray-500 uppercase">Total Paid</p><MoneyDisplay :value="supplier.total_paid" class="text-xl font-bold text-green-700 block mt-1" /></div>
      <div class="card p-4"><p class="text-xs text-gray-500 uppercase">Payable</p><MoneyDisplay :value="supplier.payable_balance" class="text-xl font-bold block mt-1" :class="supplier.payable_balance > 0 ? 'text-red-600' : 'text-gray-900'" /></div>
    </div>

    <div class="card">
      <div class="px-4 py-3 border-b border-gray-100 font-semibold text-sm">Ledger</div>
      <table class="table-base">
        <thead><tr><th>Date</th><th>Description</th><th class="text-right">Debit</th><th class="text-right">Credit</th><th class="text-right">Balance</th></tr></thead>
        <tbody>
          <tr v-for="entry in ledger" :key="entry.id">
            <td class="px-3 py-2 text-sm text-gray-500">{{ formatDate(entry.date) }}</td>
            <td class="px-3 py-2 text-sm">{{ entry.description }}</td>
            <td class="px-3 py-2 text-right"><MoneyDisplay v-if="entry.debit" :value="entry.debit" /></td>
            <td class="px-3 py-2 text-right text-green-700"><MoneyDisplay v-if="entry.credit" :value="entry.credit" /></td>
            <td class="px-3 py-2 text-right font-medium"><MoneyDisplay :value="entry.running_balance" /></td>
          </tr>
          <tr v-if="!ledger.length"><td colspan="5" class="text-center text-gray-400 py-6 text-sm">No ledger entries</td></tr>
        </tbody>
      </table>
    </div>
  </div>
  <div v-else class="text-center py-20 text-gray-400">Loading…</div>
</template>
