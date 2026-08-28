<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { repairsApi } from '@/api/repairs'
import { customersApi } from '@/api/customers'
import { useUiStore } from '@/stores/ui'
import { useForm } from '@/composables/useForm'
import AppInput from '@/components/ui/AppInput.vue'
import AppSelect from '@/components/ui/AppSelect.vue'
import AppButton from '@/components/ui/AppButton.vue'

const router   = useRouter()
const ui       = useUiStore()
const saving   = ref(false)
const technicians = ref([])
const customerSearch  = ref('')
const customerResults = ref([])
const selectedCustomer = ref(null)

const { fields, errors, validate } = useForm({
  device_model:      { value: '', required: true },
  imei:              { value: '' },
  issue_description: { value: '', required: true },
  technician:        { value: '' },
  estimated_cost:    { value: '', min: 0 },
  advance_payment:   { value: 0, min: 0 },
  accessories_received:{ value: '' },
  notes:             { value: '' },
})

onMounted(async () => {
  const res = await repairsApi.listTechnicians()
  technicians.value = (res.data.results ?? res.data).map(t => ({ value: t.id, label: t.name }))
})

let customerTimer = null
async function searchCustomer() {
  if (customerSearch.value.length < 2) { customerResults.value = []; return }
  clearTimeout(customerTimer)
  customerTimer = setTimeout(async () => {
    const res = await customersApi.search(customerSearch.value)
    customerResults.value = res.data.results ?? res.data
  }, 250)
}
function selectCustomer(c) {
  selectedCustomer.value = c
  customerSearch.value   = c.name
  customerResults.value  = []
}

async function handleSubmit() {
  if (!validate()) return
  if (!selectedCustomer.value) { ui.toastWarn('Please select a customer'); return }
  saving.value = true
  try {
    const res = await repairsApi.createJob({
      ...fields,
      customer: selectedCustomer.value.id,
    })
    ui.toastSuccess('Repair job created')
    router.push(`/repairs/jobs/${res.data.id}`)
  } catch (e) {
    ui.toastError(e.displayMessage || 'Failed to create repair job')
  } finally { saving.value = false }
}
</script>

<template>
  <div class="max-w-2xl space-y-6">
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-semibold text-gray-900">New Repair Job</h2>
      <AppButton variant="ghost" @click="router.back()">← Back</AppButton>
    </div>

    <form class="card p-6 space-y-5" @submit.prevent="handleSubmit">
      <!-- Customer -->
      <div>
        <label class="label">Customer <span class="text-red-500">*</span></label>
        <div class="relative">
          <input
            v-model="customerSearch"
            type="text"
            class="input"
            placeholder="Search by name or phone…"
            @input="searchCustomer"
          />
          <div v-if="selectedCustomer" class="absolute inset-0 flex items-center px-3 bg-white rounded-md border border-blue-300">
            <span class="flex-1 text-sm text-blue-800 font-medium">{{ selectedCustomer.name }} &nbsp;·&nbsp; {{ selectedCustomer.phone }}</span>
            <button type="button" class="text-gray-400 hover:text-red-500" @click="selectedCustomer = null; customerSearch = ''">✕</button>
          </div>
          <div v-if="customerResults.length > 0" class="absolute z-10 left-0 right-0 top-full mt-1 card shadow-lg py-1 max-h-48 overflow-y-auto">
            <button
              v-for="c in customerResults"
              :key="c.id"
              type="button"
              class="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 flex items-center justify-between"
              @click="selectCustomer(c)"
            >
              <span>{{ c.name }}</span>
              <span class="text-gray-400 text-xs">{{ c.phone }}</span>
            </button>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <AppInput v-model="fields.device_model"   label="Device Model"        :error="errors.device_model"      required class="col-span-2" />
        <AppInput v-model="fields.imei"           label="IMEI / Serial"       hint="Optional but recommended" />
        <AppSelect v-model="fields.technician"    label="Assigned Technician" :options="[{ value: '', label: 'Unassigned' }, ...technicians]" />
        <AppInput v-model="fields.estimated_cost" label="Estimated Cost"      type="number" min="0" prefix="Rs." :error="errors.estimated_cost" />
        <AppInput v-model="fields.advance_payment" label="Advance Payment"   type="number" min="0" prefix="Rs." :error="errors.advance_payment" />
      </div>

      <div>
        <label class="label">Issue Description <span class="text-red-500">*</span></label>
        <textarea v-model="fields.issue_description" class="input" rows="3" :class="errors.issue_description ? 'input-error' : ''" />
        <p v-if="errors.issue_description" class="text-xs text-red-600 mt-1">{{ errors.issue_description }}</p>
      </div>

      <AppInput v-model="fields.accessories_received" label="Accessories Received" hint="e.g. Charger, box, SIM tray" />
      <AppInput v-model="fields.notes"               label="Internal Notes" />

      <div class="flex justify-end gap-3 pt-2">
        <AppButton type="button" variant="secondary" @click="router.back()">Cancel</AppButton>
        <AppButton type="submit" variant="primary" :loading="saving">Create Job</AppButton>
      </div>
    </form>
  </div>
</template>
