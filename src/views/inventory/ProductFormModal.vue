<script setup>
import { ref, watch } from 'vue'
import { inventoryApi } from '@/api/inventory'
import { useUiStore } from '@/stores/ui'
import { useForm } from '@/composables/useForm'
import AppModal from '@/components/ui/AppModal.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppButton from '@/components/ui/AppButton.vue'
import WhatsAppShare from '@/components/ui/WhatsAppShare.vue'

const props = defineProps({
  open:    { type: Boolean, required: true },
  product: { type: Object, default: null },
})
const emit = defineEmits(['close', 'saved'])
const ui   = useUiStore()

const { fields, errors, validate, reset, setValues } = useForm({
  name:          { value: '', required: true },
  sku:           { value: '', required: true },
  brand:         { value: '' },
  category:      { value: '' },
  sell_price:    { value: '', required: true, min: 0 },
  cost_price:    { value: '', required: true, min: 0 },
  reorder_level: { value: 5, min: 0 },
  description:   { value: '' },
})

watch(() => props.product, (p) => {
  if (p) setValues(p)
  else reset()
}, { immediate: true })

const saving        = ref(false)
const savedProduct  = ref(null)   // holds the saved product for WhatsApp share
const showWhatsApp  = ref(false)

async function handleSubmit() {
  if (!validate()) return
  saving.value = true
  try {
    let result
    if (props.product?.id) {
      result = await inventoryApi.updateProduct(props.product.id, fields)
      ui.toastSuccess('Product updated')
    } else {
      result = await inventoryApi.createProduct(fields)
      ui.toastSuccess('Product created')
    }
    // Store the saved product for WhatsApp sharing
    savedProduct.value = result?.data || { ...fields }
    emit('saved')
  } catch (e) {
    ui.toastError(e.displayMessage || 'Save failed')
  } finally {
    saving.value = false
  }
}

function openWhatsApp() {
  // Use current fields if no saved result yet
  savedProduct.value = savedProduct.value || { ...fields }
  showWhatsApp.value = true
}
</script>

<template>
  <!-- Main product form modal -->
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
      <AppInput v-model="fields.sku"           label="SKU"           :error="errors.sku"        required />
      <AppInput v-model="fields.brand"         label="Brand"         :error="errors.brand" />
      <AppInput v-model="fields.category"      label="Category"      :error="errors.category" />
      <AppInput v-model="fields.reorder_level" label="Reorder Level" type="number" min="0" />
      <AppInput v-model="fields.sell_price"    label="Sell Price"    type="number" step="1" prefix="Rs." :error="errors.sell_price" required />
      <AppInput v-model="fields.cost_price"    label="Cost Price"    type="number" step="1" prefix="Rs." :error="errors.cost_price" required />
      <div class="col-span-2">
        <label class="label">Description</label>
        <textarea v-model="fields.description" class="input" rows="2" />
      </div>
    </form>

    <template #footer>
      <!-- WhatsApp share button -->
      <button
        type="button"
        class="wa-footer-btn"
        :disabled="!fields.name || !fields.sell_price"
        :title="!fields.name || !fields.sell_price ? 'Fill product name and price first' : 'Share on WhatsApp'"
        @click="openWhatsApp"
      >
        <svg viewBox="0 0 24 24" fill="currentColor" class="w-3.5 h-3.5">
          <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
        </svg>
        Share
      </button>

      <div class="flex-1" />

      <AppButton variant="secondary" @click="emit('close')">Cancel</AppButton>
      <AppButton variant="primary" :loading="saving" @click="handleSubmit">
        {{ product ? 'Save Changes' : 'Create Product' }}
      </AppButton>
    </template>
  </AppModal>

  <!-- WhatsApp share modal (stacked) -->
  <WhatsAppShare
    :open="showWhatsApp"
    :product="savedProduct || fields"
    type="accessory"
    @close="showWhatsApp = false"
  />
</template>

<style scoped>
.wa-footer-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.4rem 0.75rem;
  border-radius: 7px;
  background: linear-gradient(135deg, #25d366, #128c7e);
  color: white;
  font-size: 0.75rem;
  font-weight: 700;
  border: none;
  cursor: pointer;
  transition: all 150ms;
  box-shadow: 0 2px 6px rgba(37,211,102,0.25);
}
.wa-footer-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #20bc5a, #0e7a6e);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37,211,102,0.35);
}
.wa-footer-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
}
</style>
