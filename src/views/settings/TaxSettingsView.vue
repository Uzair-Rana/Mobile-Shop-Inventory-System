<script setup>
import { ref, onMounted } from 'vue'
import { settingsApi } from '@/api/settings'
import { useUiStore } from '@/stores/ui'
import AppButton from '@/components/ui/AppButton.vue'

const ui   = useUiStore()
const taxes = ref([])
const saving = ref(null)

onMounted(async () => {
  const res = await settingsApi.listTaxes()
  taxes.value = res.data.results ?? res.data
})

async function handleSave(tax) {
  saving.value = tax.id
  try {
    await settingsApi.updateTax(tax.id, tax)
    ui.toastSuccess('Tax updated')
  } catch (e) {
    ui.toastError(e.displayMessage || 'Update failed')
  } finally { saving.value = null }
}
</script>

<template>
  <div class="max-w-xl space-y-4">
    <div v-for="tax in taxes" :key="tax.id" class="card p-4 flex items-center gap-4">
      <div class="flex-1">
        <p class="font-medium text-gray-900">{{ tax.name }}</p>
        <p class="text-xs text-gray-400">Applied to: {{ tax.applies_to || 'All' }}</p>
      </div>
      <div class="flex items-center gap-2">
        <input v-model.number="tax.rate" type="number" step="0.1" min="0" max="100" class="input w-24 text-right" />
        <span class="text-gray-500">%</span>
        <AppButton variant="primary" size="sm" :loading="saving === tax.id" @click="handleSave(tax)">Save</AppButton>
      </div>
    </div>
    <p v-if="taxes.length === 0" class="text-sm text-gray-400">No tax configurations found</p>
  </div>
</template>
