<script setup>
import { ref, onMounted } from 'vue'
import { reportsApi } from '@/api/reports'
import { INSTALLMENT_STATUS } from '@/utils/constants'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'

const data    = ref(null)
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const res = await reportsApi.installmentHealth()
    data.value  = res.data
  } finally { loading.value = false }
}

onMounted(load)

function statusObj(val) {
  return Object.values(INSTALLMENT_STATUS).find(s => s.value === val) || { label: val, badge: 'badge-gray' }
}
</script>

<template>
  <div class="space-y-5">
    <div class="flex justify-end"><AppButton variant="secondary" :loading="loading" @click="load">Refresh</AppButton></div>

    <div v-if="data" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="card p-4"><p class="text-xs text-gray-500 uppercase">Active</p><p class="text-xl font-bold text-green-700 mt-1">{{ data.active_count }}</p></div>
      <div class="card p-4"><p class="text-xs text-gray-500 uppercase">Overdue</p><p class="text-xl font-bold text-red-600 mt-1">{{ data.overdue_count }}</p></div>
      <div class="card p-4"><p class="text-xs text-gray-500 uppercase">Total Receivable</p><MoneyDisplay :value="data.total_receivable" class="text-xl font-bold text-gray-900 block mt-1" /></div>
      <div class="card p-4"><p class="text-xs text-gray-500 uppercase">Overdue Amount</p><MoneyDisplay :value="data.overdue_amount" class="text-xl font-bold text-red-600 block mt-1" /></div>
    </div>

    <div v-if="data?.overdue_plans?.length" class="card overflow-hidden">
      <div class="px-4 py-3 border-b border-gray-100 font-semibold text-sm text-red-700">Overdue Plans</div>
      <table class="table-base">
        <thead><tr><th>Plan #</th><th>Customer</th><th>Product</th><th class="text-right">Overdue</th></tr></thead>
        <tbody>
          <tr v-for="p in data.overdue_plans" :key="p.id" class="bg-red-50/30">
            <td class="px-3 py-2">
              <RouterLink :to="`/installments/${p.id}`" class="text-blue-700 hover:underline">#{{ p.plan_number }}</RouterLink>
            </td>
            <td class="px-3 py-2 text-sm">{{ p.customer_name }}</td>
            <td class="px-3 py-2 text-sm text-gray-600">{{ p.product_name }}</td>
            <td class="px-3 py-2 text-right"><MoneyDisplay :value="p.overdue_amount" class="text-red-600 font-semibold" /></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
