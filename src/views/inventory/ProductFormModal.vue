<script setup>
import { watch } from 'vue'
import { inventoryApi } from '@/api/inventory'
import { useUiStore } from '@/stores/ui'
import { useForm } from '@/composables/useForm'
import AppModal from '@/components/ui/AppModal.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'

const props = defineProps({
  open:    { type: Boolean, required: true },
  product: { type: Object, default: null },
})
const emit = defineEmits(['close', 'saved'])
const ui   = useUiStore()

const { fields, errors, validate, reset, setValues } = useForm({
  name:         { value: '', required: true },
  sku:          { value: '', required: true },
  brand:        { value: '' },
  category:     { value: '' },
  sell_price:   { value: '', required: true, min: 0 },
  cost_price:   { value: '', required: true, min: 0 },
  reorder_level:{ value: 5, min: 0 },
  description:  { value: '' },
})

watch(() => props.product, (p) => {
  if (p) setValues(p)
  else reset()
}, { immediate: true })

const saving = ref(false)
import { ref } from 'vue'

async function handleSubmit() {
  if (!validate()) return
  saving.value = true
  try {
    if (props.product?.id) {
      await inventoryApi.updateProduct(props.product.id, fields)
      ui.toastSuccess('Product updated')
    } else {
      await inventoryApi.createProduct(fields)
      ui.toastSuccess('Product created')
    }
    emit('saved')
  } catch (e) {
    ui.toastError(e.displayMessage || 'Save failed')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <AppModal
    :open="open"
    :title="product ? 'Edit Product' : 'New Product'"
    size="lg"
    @close="emit('close')"
  >
    <form class="grid grid-cols-2 gap-4" @submit.prevent="handleSubmit">
      <AppInput
        v-model="fields.name"
        label="Product Name"
        :error="errors.name"
        required
        class="col-span-2"
      />
      <AppInput v-model="fields.sku"      label="SKU"       :error="errors.sku"       required />
      <AppInput v-model="fields.brand"    label="Brand"     :error="errors.brand" />
      <AppInput v-model="fields.category" label="Category"  :error="errors.category" />
      <AppInput v-model="fields.reorder_level" label="Reorder Level" type="number" min="0" />
      <AppInput v-model="fields.sell_price" label="Sell Price" type="number" step="1" prefix="Rs." :error="errors.sell_price" required />
      <AppInput v-model="fields.cost_price" label="Cost Price" type="number" step="1" prefix="Rs." :error="errors.cost_price" required />
      <div class="col-span-2">
        <label class="label">Description</label>
        <textarea v-model="fields.description" class="input" rows="2" />
      </div>
    </form>

    <template #footer>
      <AppButton variant="secondary" @click="emit('close')">Cancel</AppButton>
      <AppButton variant="primary" :loading="saving" @click="handleSubmit">
        {{ product ? 'Save Changes' : 'Create Product' }}
      </AppButton>
    </template>
  </AppModal>
</template>
