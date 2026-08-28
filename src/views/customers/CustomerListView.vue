<script setup>
import { ref, onMounted, watch } from 'vue'
import { customersApi } from '@/api/customers'
import { usePagination } from '@/composables/usePagination'
import { formatDate } from '@/utils/date'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import AppTable from '@/components/ui/AppTable.vue'
import AppPagination from '@/components/ui/AppPagination.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppInput from '@/components/ui/AppInput.vue'
import { useUiStore } from '@/stores/ui'
import { useForm } from '@/composables/useForm'

const pg       = usePagination({ pageSize: 25 })
const ui       = useUiStore()
const customers = ref([])
const loading   = ref(false)
const search    = ref('')
const showForm  = ref(false)
const saving    = ref(false)

const { fields, errors, validate, reset } = useForm({
  name:    { value: '', required: true },
  phone:   { value: '', required: true },
  email:   { value: '' },
  address: { value: '' },
  cnic:    { value: '' },
})

const columns = [
  { key: 'name',       label: 'Name',     sortable: true },
  { key: 'phone',      label: 'Phone' },
  { key: 'email',      label: 'Email' },
  { key: 'balance',    label: 'Balance',  align: 'right' },
  { key: 'joined',     label: 'Joined' },
]

async function load() {
  loading.value = true
  try {
    const res = await customersApi.listCustomers({ search: search.value || undefined, ...pg.queryParams.value })
    customers.value = res.data.results ?? res.data
    pg.setFromResponse({ count: res.data.count ?? customers.value.length })
  } finally { loading.value = false }
}

watch([search, () => pg.currentPage.value], load)
onMounted(load)

async function handleSave() {
  if (!validate()) return
  saving.value = true
  try {
    await customersApi.createCustomer(fields)
    ui.toastSuccess('Customer added')
    showForm.value = false
    reset()
    load()
  } catch (e) {
    ui.toastError(e.displayMessage || 'Save failed')
  } finally { saving.value = false }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-3">
      <input v-model="search" type="search" class="input max-w-xs" placeholder="Search customers…" />
      <div class="flex-1" />
      <AppButton variant="primary" @click="showForm = true">+ Add Customer</AppButton>
    </div>

    <AppTable :columns="columns" :loading="loading" empty-message="No customers found">
      <tr v-for="c in customers" :key="c.id">
        <td class="px-3 py-2.5">
          <RouterLink :to="`/customers/${c.id}`" class="font-medium text-blue-700 hover:underline">{{ c.name }}</RouterLink>
        </td>
        <td class="px-3 py-2.5 text-sm">{{ c.phone }}</td>
        <td class="px-3 py-2.5 text-sm text-gray-500">{{ c.email || '—' }}</td>
        <td class="px-3 py-2.5 text-right">
          <span :class="c.balance < 0 ? 'text-red-600 font-semibold' : 'text-gray-700'">
            <MoneyDisplay :value="c.balance" />
          </span>
        </td>
        <td class="px-3 py-2.5 text-sm text-gray-500">{{ formatDate(c.created_at) }}</td>
      </tr>
    </AppTable>

    <AppPagination v-bind="{ currentPage: pg.currentPage.value, totalPages: pg.totalPages.value, totalCount: pg.totalCount.value, pageSize: pg.pageSize.value }" @page="pg.goTo" />

    <AppModal :open="showForm" title="New Customer" size="md" @close="showForm = false; reset()">
      <form class="space-y-4" @submit.prevent="handleSave">
        <AppInput v-model="fields.name"    label="Full Name" :error="errors.name"  required />
        <AppInput v-model="fields.phone"   label="Phone"     :error="errors.phone" required />
        <AppInput v-model="fields.email"   label="Email"     type="email" />
        <AppInput v-model="fields.cnic"    label="CNIC"      hint="Optional — 13 digits" />
        <AppInput v-model="fields.address" label="Address" />
      </form>
      <template #footer>
        <AppButton variant="secondary" @click="showForm = false; reset()">Cancel</AppButton>
        <AppButton variant="primary" :loading="saving" @click="handleSave">Save Customer</AppButton>
      </template>
    </AppModal>
  </div>
</template>
