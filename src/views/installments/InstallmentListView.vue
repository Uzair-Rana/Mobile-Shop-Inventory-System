<script setup>
import { ref, onMounted, watch } from 'vue'
import { installmentsApi } from '@/api/installments'
import { usePagination } from '@/composables/usePagination'
import { formatDate, daysUntil } from '@/utils/date'
import { INSTALLMENT_STATUS } from '@/utils/constants'
import AppTable from '@/components/ui/AppTable.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppPagination from '@/components/ui/AppPagination.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'

const pg     = usePagination({ pageSize: 25 })
const plans  = ref([])
const loading= ref(false)
const search = ref('')
const status = ref('')

const STATUS_OPTIONS = [
  { value: '', label: 'All' },
  ...Object.values(INSTALLMENT_STATUS).map(s => ({ value: s.value, label: s.label }))
]

const columns = [
  { key: 'plan',      label: 'Plan #' },
  { key: 'customer',  label: 'Customer' },
  { key: 'device',    label: 'Device' },
  { key: 'status',    label: 'Status' },
  { key: 'next_due',  label: 'Next Due' },
  { key: 'remaining', label: 'Remaining', align: 'right' },
  { key: 'total',     label: 'Total',     align: 'right' },
]

async function load() {
  loading.value = true
  try {
    const res = await installmentsApi.listPlans({ search: search.value || undefined, status: status.value || undefined, ...pg.queryParams.value })
    plans.value = res.data.results ?? res.data
    pg.setFromResponse({ count: res.data.count ?? plans.value.length })
  } finally { loading.value = false }
}

watch([search, status, () => pg.currentPage.value], load)
onMounted(load)

function statusObj(val) {
  return Object.values(INSTALLMENT_STATUS).find(s => s.value === val) || { label: val, badge: 'badge-gray' }
}

function dueDaysClass(date) {
  const d = daysUntil(date)
  if (d < 0)  return 'text-red-600 font-semibold'
  if (d <= 3) return 'text-orange-600 font-semibold'
  return 'text-gray-700'
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-3">
      <input v-model="search" type="search" class="input max-w-xs" placeholder="Customer, device…" />
      <select v-model="status" class="input w-44">
        <option v-for="s in STATUS_OPTIONS" :key="s.value" :value="s.value">{{ s.label }}</option>
      </select>
      <div class="flex-1" />
    </div>

    <AppTable :columns="columns" :loading="loading" empty-message="No installment plans">
      <tr v-for="plan in plans" :key="plan.id">
        <td class="px-3 py-2.5">
          <RouterLink :to="`/installments/${plan.id}`" class="font-medium text-blue-700 hover:underline">#{{ plan.plan_number }}</RouterLink>
        </td>
        <td class="px-3 py-2.5">
          <p class="text-sm">{{ plan.customer_name }}</p>
          <p class="text-xs text-gray-400">{{ plan.customer_phone }}</p>
        </td>
        <td class="px-3 py-2.5 text-sm">{{ plan.product_name }}</td>
        <td class="px-3 py-2.5"><AppBadge :status="statusObj(plan.status)" /></td>
        <td class="px-3 py-2.5 text-sm" :class="dueDaysClass(plan.next_due_date)">
          {{ formatDate(plan.next_due_date) }}
          <span v-if="plan.next_due_date" class="text-xs ml-1 opacity-70">
            ({{ daysUntil(plan.next_due_date) }}d)
          </span>
        </td>
        <td class="px-3 py-2.5 text-right"><MoneyDisplay :value="plan.remaining_amount" /></td>
        <td class="px-3 py-2.5 text-right"><MoneyDisplay :value="plan.total_amount" /></td>
      </tr>
    </AppTable>

    <AppPagination v-bind="{ currentPage: pg.currentPage.value, totalPages: pg.totalPages.value, totalCount: pg.totalCount.value, pageSize: pg.pageSize.value }" @page="pg.goTo" />
  </div>
</template>
