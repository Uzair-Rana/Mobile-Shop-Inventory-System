<script setup>
import { ref, onMounted } from 'vue'
import { reportsApi } from '@/api/reports'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import AppButton from '@/components/ui/AppButton.vue'

const data    = ref(null)
const loading = ref(false)
const filters = ref({
  date_from: new Date(new Date().setDate(1)).toISOString().slice(0, 10),
  date_to:   new Date().toISOString().slice(0, 10),
})

async function load() {
  loading.value = true
  try {
    const res = await reportsApi.repairsSummary(filters.value)
    data.value  = res.data
  } finally { loading.value = false }
}

onMounted(load)
</script>

<template>
  <div class="space-y-5">
    <div class="card p-4 flex flex-wrap items-end gap-4">
      <div><label class="label">From</label><input v-model="filters.date_from" type="date" class="input w-36" /></div>
      <div><label class="label">To</label><input v-model="filters.date_to" type="date" class="input w-36" /></div>
      <AppButton variant="primary" :loading="loading" @click="load">Run</AppButton>
    </div>

    <div v-if="data" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="card p-4"><p class="text-xs text-gray-500 uppercase">Jobs</p><p class="text-xl font-bold text-gray-900 mt-1">{{ data.total_jobs }}</p></div>
      <div class="card p-4"><p class="text-xs text-gray-500 uppercase">Completed</p><p class="text-xl font-bold text-green-700 mt-1">{{ data.completed }}</p></div>
      <div class="card p-4"><p class="text-xs text-gray-500 uppercase">Revenue</p><MoneyDisplay :value="data.revenue" class="text-xl font-bold text-gray-900 block mt-1" /></div>
      <div class="card p-4"><p class="text-xs text-gray-500 uppercase">Pending</p><p class="text-xl font-bold text-orange-600 mt-1">{{ data.pending }}</p></div>
    </div>
  </div>
</template>
