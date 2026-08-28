<script setup>
import { ref, onMounted } from 'vue'
import { settingsApi } from '@/api/settings'
import { useUiStore } from '@/stores/ui'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'

const ui     = useUiStore()
const form   = ref({})
const saving = ref(false)
const loading= ref(true)

onMounted(async () => {
  const res    = await settingsApi.getCompany()
  form.value   = res.data
  loading.value= false
})

async function handleSave() {
  saving.value = true
  try {
    await settingsApi.updateCompany(form.value)
    ui.toastSuccess('Company settings saved')
  } catch (e) {
    ui.toastError(e.displayMessage || 'Save failed')
  } finally { saving.value = false }
}
</script>

<template>
  <div v-if="!loading" class="max-w-xl">
    <form class="card p-6 space-y-4" @submit.prevent="handleSave">
      <AppInput v-model="form.name"    label="Company Name"    required />
      <AppInput v-model="form.address" label="Address" />
      <AppInput v-model="form.phone"   label="Phone" />
      <AppInput v-model="form.email"   label="Email"  type="email" />
      <AppInput v-model="form.ntn"     label="NTN / Tax ID" />
      <AppInput v-model="form.website" label="Website" />
      <div class="flex justify-end pt-2">
        <AppButton type="submit" variant="primary" :loading="saving">Save Changes</AppButton>
      </div>
    </form>
  </div>
</template>
