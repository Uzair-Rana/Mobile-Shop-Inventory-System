<script setup>
import { ref, onMounted } from 'vue'
import { reportsApi } from '@/api/reports'
import { usePermissions } from '@/composables/usePermissions'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import AppButton from '@/components/ui/AppButton.vue'

const perms   = usePermissions()
const data    = ref(null)
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const res = await reportsApi.inventoryValuation()
    data.value  = res.data
  } finally { loading.value = false }
}

onMounted(load)
</script>

<template>
  <div class="space-y-5">
    <div class="flex justify-end gap-2">
      <AppButton variant="secondary" :loading="loading" @click="load">Refresh</AppButton>
    </div>

    <div v-if="data" class="grid grid-cols-2 md:grid-cols-3 gap-4">
      <div class="card p-4"><p class="text-xs text-gray-500 uppercase">Stock Items</p><p class="text-xl font-bold text-gray-900 mt-1">{{ data.total_units }}</p></div>
      <div class="card p-4"><p class="text-xs text-gray-500 uppercase">Retail Value</p><MoneyDisplay :value="data.retail_value" class="text-xl font-bold text-gray-900 block mt-1" /></div>
      <div class="card p-4"><p class="text-xs text-gray-500 uppercase">Cost Value</p><MoneyDisplay :value="data.cost_value" :mask="!perms.canViewCost.value" class="text-xl font-bold text-gray-900 block mt-1" /></div>
    </div>

    <div v-if="data?.by_category" class="card overflow-hidden">
      <div class="px-4 py-3 border-b border-gray-100 font-semibold text-sm">By Category</div>
      <table class="table-base">
        <thead><tr><th>Category</th><th class="text-right">Units</th><th class="text-right">Retail</th><th class="text-right">Cost</th></tr></thead>
        <tbody>
          <tr v-for="row in data.by_category" :key="row.category">
            <td class="px-3 py-2">{{ row.category }}</td>
            <td class="px-3 py-2 text-right">{{ row.units }}</td>
            <td class="px-3 py-2 text-right"><MoneyDisplay :value="row.retail_value" /></td>
            <td class="px-3 py-2 text-right"><MoneyDisplay :value="row.cost_value" :mask="!perms.canViewCost.value" /></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
