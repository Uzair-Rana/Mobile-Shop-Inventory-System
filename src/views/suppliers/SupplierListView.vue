<script setup>
import { ref, onMounted, watch } from 'vue'
import { suppliersApi } from '@/api/suppliers'
import { usePagination } from '@/composables/usePagination'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import AppTable from '@/components/ui/AppTable.vue'
import AppPagination from '@/components/ui/AppPagination.vue'
import AppButton from '@/components/ui/AppButton.vue'

const pg        = usePagination({ pageSize: 25 })
const suppliers = ref([])
const loading   = ref(false)
const search    = ref('')

const columns = [
  { key: 'name',    label: 'Supplier',   sortable: true },
  { key: 'phone',   label: 'Phone' },
  { key: 'email',   label: 'Email' },
  { key: 'balance', label: 'Payable',    align: 'right' },
  { key: 'action',  label: '' },
]

async function load() {
  loading.value = true
  try {
    const res = await suppliersApi.listSuppliers({ search: search.value || undefined, ...pg.queryParams.value })
    suppliers.value = res.data.results ?? res.data
    pg.setFromResponse({ count: res.data.count ?? suppliers.value.length })
  } finally { loading.value = false }
}

watch([search, () => pg.currentPage.value], load)
onMounted(load)
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-3">
      <input v-model="search" type="search" class="input max-w-xs" placeholder="Search suppliers…" />
      <div class="flex-1" />
      <AppButton variant="primary">+ Add Supplier</AppButton>
    </div>
    <AppTable :columns="columns" :loading="loading" empty-message="No suppliers found">
      <tr v-for="s in suppliers" :key="s.id">
        <td class="px-3 py-2.5">
          <RouterLink :to="`/suppliers/${s.id}`" class="font-medium text-blue-700 hover:underline">{{ s.name }}</RouterLink>
        </td>
        <td class="px-3 py-2.5 text-sm">{{ s.phone }}</td>
        <td class="px-3 py-2.5 text-sm text-gray-500">{{ s.email || '—' }}</td>
        <td class="px-3 py-2.5 text-right">
          <MoneyDisplay :value="s.payable_balance" :class="s.payable_balance > 0 ? 'text-red-600 font-semibold' : ''" />
        </td>
        <td class="px-3 py-2.5 text-right">
          <RouterLink :to="`/suppliers/${s.id}`" class="text-xs text-blue-600 hover:underline">View</RouterLink>
        </td>
      </tr>
    </AppTable>
    <AppPagination v-bind="{ currentPage: pg.currentPage.value, totalPages: pg.totalPages.value, totalCount: pg.totalCount.value, pageSize: pg.pageSize.value }" @page="pg.goTo" />
  </div>
</template>
