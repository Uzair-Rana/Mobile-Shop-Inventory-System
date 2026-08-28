<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { customersApi } from '@/api/customers'
import { formatDate } from '@/utils/date'
import { INVOICE_STATUS, INSTALLMENT_STATUS } from '@/utils/constants'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'

const route   = useRoute()
const router  = useRouter()
const customer= ref(null)
const history = ref({ invoices: [], repairs: [], installments: [] })
const loading = ref(true)

onMounted(async () => {
  const [cRes, hRes] = await Promise.all([
    customersApi.getCustomer(route.params.id),
    customersApi.getHistory(route.params.id),
  ])
  customer.value = cRes.data
  history.value  = hRes.data
  loading.value  = false
})

function invStatus(val) {
  return Object.values(INVOICE_STATUS).find(s => s.value === val) || { label: val, badge: 'badge-gray' }
}
</script>

<template>
  <div v-if="!loading && customer" class="space-y-6 max-w-4xl">
    <!-- Header -->
    <div class="flex items-start justify-between">
      <div>
        <h2 class="text-xl font-bold text-gray-900">{{ customer.name }}</h2>
        <p class="text-sm text-gray-500">{{ customer.phone }} &nbsp;·&nbsp; {{ customer.email || 'No email' }}</p>
      </div>
      <AppButton variant="ghost" @click="router.back()">← Back</AppButton>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="card p-4">
        <p class="text-xs text-gray-500 uppercase tracking-wide">Total Spent</p>
        <MoneyDisplay :value="customer.total_spent" class="text-xl font-bold text-gray-900 block mt-1" />
      </div>
      <div class="card p-4">
        <p class="text-xs text-gray-500 uppercase tracking-wide">Balance</p>
        <MoneyDisplay :value="customer.balance" class="text-xl font-bold block mt-1" :class="customer.balance < 0 ? 'text-red-600' : 'text-green-700'" />
      </div>
      <div class="card p-4">
        <p class="text-xs text-gray-500 uppercase tracking-wide">Invoices</p>
        <p class="text-xl font-bold text-gray-900 mt-1">{{ customer.invoice_count }}</p>
      </div>
      <div class="card p-4">
        <p class="text-xs text-gray-500 uppercase tracking-wide">Repairs</p>
        <p class="text-xl font-bold text-gray-900 mt-1">{{ customer.repair_count }}</p>
      </div>
    </div>

    <!-- Purchase history -->
    <div class="card">
      <div class="px-4 py-3 border-b border-gray-100 font-semibold text-sm">Purchase History</div>
      <table class="table-base">
        <thead><tr><th>Invoice</th><th>Date</th><th>Total</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="inv in history.invoices" :key="inv.id">
            <td class="px-3 py-2.5">
              <RouterLink :to="`/sales/invoices/${inv.id}`" class="text-blue-700 hover:underline">#{{ inv.invoice_number }}</RouterLink>
            </td>
            <td class="px-3 py-2.5 text-sm text-gray-500">{{ formatDate(inv.created_at) }}</td>
            <td class="px-3 py-2.5 text-right"><MoneyDisplay :value="inv.grand_total" /></td>
            <td class="px-3 py-2.5"><AppBadge :status="invStatus(inv.status)" /></td>
          </tr>
          <tr v-if="!history.invoices?.length"><td colspan="4" class="text-center text-gray-400 py-6 text-sm">No purchases</td></tr>
        </tbody>
      </table>
    </div>
  </div>
  <div v-else class="text-center py-20 text-gray-400">Loading…</div>
</template>
