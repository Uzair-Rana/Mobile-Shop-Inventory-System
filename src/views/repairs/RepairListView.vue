<script setup>
import { ref, onMounted, watch } from 'vue'
import { repairsApi } from '@/api/repairs'
import { usePagination } from '@/composables/usePagination'
import { formatDate } from '@/utils/date'
import { REPAIR_STATUS } from '@/utils/constants'
import AppTable from '@/components/ui/AppTable.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppPagination from '@/components/ui/AppPagination.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'

const pg     = usePagination({ pageSize: 25 })
const jobs   = ref([])
const loading= ref(false)
const search = ref('')
const status = ref('')

const STATUS_OPTIONS = [
  { value: '', label: 'All' },
  ...Object.values(REPAIR_STATUS).map(s => ({ value: s.value, label: s.label }))
]

const columns = [
  { key: 'job_number', label: 'Job #' },
  { key: 'device',     label: 'Device' },
  { key: 'customer',   label: 'Customer' },
  { key: 'technician', label: 'Technician' },
  { key: 'status',     label: 'Status' },
  { key: 'received',   label: 'Received' },
  { key: 'estimate',   label: 'Estimate', align: 'right' },
]

async function load() {
  loading.value = true
  try {
    const res = await repairsApi.listJobs({
      search: search.value || undefined,
      status: status.value || undefined,
      ...pg.queryParams.value,
    })
    jobs.value = res.data.results ?? res.data
    pg.setFromResponse({ count: res.data.count ?? jobs.value.length })
  } finally { loading.value = false }
}

watch([search, status, () => pg.currentPage.value], load)
onMounted(load)

function statusObj(val) {
  return Object.values(REPAIR_STATUS).find(s => s.value === val) || { label: val, badge: 'badge-gray' }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-3 flex-wrap">
      <input v-model="search" type="search" class="input w-48" placeholder="Job #, device, customer…" />
      <select v-model="status" class="input w-44">
        <option v-for="s in STATUS_OPTIONS" :key="s.value" :value="s.value">{{ s.label }}</option>
      </select>
      <div class="flex-1" />
      <RouterLink to="/repairs/jobs/new" class="btn btn-primary">+ New Repair Job</RouterLink>
    </div>

    <AppTable :columns="columns" :loading="loading" empty-message="No repair jobs found">
      <tr v-for="job in jobs" :key="job.id">
        <td class="px-3 py-2.5">
          <RouterLink :to="`/repairs/jobs/${job.id}`" class="font-medium text-blue-700 hover:underline">
            #{{ job.job_number }}
          </RouterLink>
        </td>
        <td class="px-3 py-2.5">
          <p class="text-sm font-medium">{{ job.device_model }}</p>
          <p class="text-xs text-gray-400 font-mono">{{ job.imei }}</p>
        </td>
        <td class="px-3 py-2.5">
          <p class="text-sm">{{ job.customer_name }}</p>
          <p class="text-xs text-gray-400">{{ job.customer_phone }}</p>
        </td>
        <td class="px-3 py-2.5 text-sm text-gray-600">{{ job.technician_name || '—' }}</td>
        <td class="px-3 py-2.5"><AppBadge :status="statusObj(job.status)" /></td>
        <td class="px-3 py-2.5 text-sm text-gray-500">{{ formatDate(job.received_at) }}</td>
        <td class="px-3 py-2.5 text-right"><MoneyDisplay :value="job.estimated_cost" /></td>
      </tr>
    </AppTable>

    <AppPagination v-bind="{ currentPage: pg.currentPage.value, totalPages: pg.totalPages.value, totalCount: pg.totalCount.value, pageSize: pg.pageSize.value }" @page="pg.goTo" />
  </div>
</template>
