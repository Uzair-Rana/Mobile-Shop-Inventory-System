<script setup>
/**
 * SparePartFormModal — create or edit a SparePart master record.
 * Props:
 *   open       — show/hide
 *   part       — existing part object (null = create mode)
 *   categories — array of { value, label } from API
 * Emits:
 *   close
 *   saved
 */
import { ref, watch, computed } from 'vue'
import { sparePartsApi } from '@/api/spareParts'
import { useUiStore } from '@/stores/ui'
import AppModal from '@/components/ui/AppModal.vue'
import AppButton from '@/components/ui/AppButton.vue'

const props = defineProps({
  open:       { type: Boolean, required: true },
  part:       { type: Object,  default: null  },
  categories: { type: Array,   default: () => [] },
})
const emit = defineEmits(['close', 'saved'])
const ui   = useUiStore()

// ── Form state ────────────────────────────────────────────────────────────────
const form = ref({})
const submitting = ref(false)
const errors     = ref({})

const isEdit = computed(() => !!props.part?.id)

function reset() {
  form.value = props.part
    ? { ...props.part }
    : {
        sku: '', name: '', category: '', brand_compat: '', model_compat: '',
        description: '', display_type: 'N/A', with_frame: false,
        camera_position: 'N/A', battery_capacity: null,
        cost_price: 0, sell_price: 0, reorder_level: 3,
        is_active: true,
      }
  errors.value = {}
}

watch(() => props.open, v => { if (v) reset() })

// ── Category-specific extras ──────────────────────────────────────────────────
const showDisplayType    = computed(() => form.value.category === 'display_panel')
const showWithFrame      = computed(() => form.value.category === 'display_panel')
const showCameraPosition = computed(() => form.value.category === 'camera_module')
const showBatteryCapacity= computed(() => form.value.category === 'battery')

const displayTypes = [
  { value: 'LCD',    label: 'LCD'    },
  { value: 'OLED',   label: 'OLED'   },
  { value: 'AMOLED', label: 'AMOLED' },
  { value: 'N/A',    label: 'N/A'    },
]
const cameraPositions = [
  { value: 'front', label: 'Front'       },
  { value: 'rear',  label: 'Rear'        },
  { value: 'both',  label: 'Front & Rear'},
  { value: 'N/A',   label: 'N/A'         },
]

// ── Submit ────────────────────────────────────────────────────────────────────
function validate() {
  const e = {}
  if (!form.value.sku?.trim())      e.sku      = 'SKU is required.'
  if (!form.value.name?.trim())     e.name     = 'Name is required.'
  if (!form.value.category)         e.category = 'Select a category.'
  if (form.value.cost_price < 0)    e.cost_price = 'Cannot be negative.'
  if (form.value.sell_price < 0)    e.sell_price = 'Cannot be negative.'
  if (form.value.reorder_level < 0) e.reorder_level = 'Cannot be negative.'
  errors.value = e
  return Object.keys(e).length === 0
}

async function submit() {
  if (!validate()) return
  submitting.value = true
  try {
    if (isEdit.value) {
      await sparePartsApi.update(props.part.id, form.value)
    } else {
      await sparePartsApi.create(form.value)
    }
    ui.toastSuccess?.(isEdit.value ? 'Part updated.' : 'Part created.')
    emit('saved')
  } catch (e) {
    // Map field errors from DRF
    const d = e.response?.data || {}
    Object.entries(d).forEach(([k, v]) => {
      errors.value[k] = Array.isArray(v) ? v[0] : String(v)
    })
    ui.toastError?.(e.displayMessage || 'Save failed.')
  } finally { submitting.value = false }
}
</script>

<template>
  <AppModal
    :open="open"
    :title="isEdit ? `Edit — ${part?.name}` : 'Add Spare Part'"
    size="lg"
    @close="emit('close')"
  >
    <div class="form-grid">

      <!-- ── Identification ── -->
      <div class="section-heading">Identification</div>

      <div class="field-row">
        <div class="field">
          <label class="label">SKU <span class="req">*</span></label>
          <input v-model="form.sku" type="text" class="input" :class="{ 'input-error': errors.sku }" placeholder="e.g. DSP-SAM-A54-LCD" />
          <p v-if="errors.sku" class="err">{{ errors.sku }}</p>
        </div>
        <div class="field">
          <label class="label">Category <span class="req">*</span></label>
          <select v-model="form.category" class="input select-arrow" :class="{ 'input-error': errors.category }">
            <option value="">— Select —</option>
            <option v-for="c in categories" :key="c.value" :value="c.value">{{ c.label }}</option>
          </select>
          <p v-if="errors.category" class="err">{{ errors.category }}</p>
        </div>
      </div>

      <div class="field">
        <label class="label">Part Name <span class="req">*</span></label>
        <input v-model="form.name" type="text" class="input" :class="{ 'input-error': errors.name }" placeholder="e.g. Samsung A54 LCD Display Assembly" />
        <p v-if="errors.name" class="err">{{ errors.name }}</p>
      </div>

      <div class="field-row">
        <div class="field">
          <label class="label">Compatible Brand(s)</label>
          <input v-model="form.brand_compat" type="text" class="input" placeholder="e.g. Samsung, Oppo" />
        </div>
        <div class="field">
          <label class="label">Compatible Model(s)</label>
          <input v-model="form.model_compat" type="text" class="input" placeholder="e.g. A54, A53, A52" />
        </div>
      </div>

      <div class="field">
        <label class="label">Description</label>
        <textarea v-model="form.description" rows="2" class="input" placeholder="Optional details…" />
      </div>

      <!-- ── Category-specific attributes ── -->
      <template v-if="showDisplayType || showWithFrame">
        <div class="section-heading">Display Attributes</div>
        <div class="field-row">
          <div v-if="showDisplayType" class="field">
            <label class="label">Display Type</label>
            <select v-model="form.display_type" class="input select-arrow">
              <option v-for="d in displayTypes" :key="d.value" :value="d.value">{{ d.label }}</option>
            </select>
          </div>
          <div v-if="showWithFrame" class="field flex items-center gap-3 pt-6">
            <input v-model="form.with_frame" type="checkbox" id="with_frame" class="w-4 h-4 accent-red-600" />
            <label for="with_frame" class="text-sm font-medium text-gray-700 cursor-pointer">
              Includes frame / chassis
            </label>
          </div>
        </div>
      </template>

      <template v-if="showCameraPosition">
        <div class="section-heading">Camera Attributes</div>
        <div class="field">
          <label class="label">Camera Position</label>
          <select v-model="form.camera_position" class="input select-arrow">
            <option v-for="c in cameraPositions" :key="c.value" :value="c.value">{{ c.label }}</option>
          </select>
        </div>
      </template>

      <template v-if="showBatteryCapacity">
        <div class="section-heading">Battery Attributes</div>
        <div class="field" style="max-width:220px">
          <label class="label">Battery Capacity (mAh)</label>
          <input v-model.number="form.battery_capacity" type="number" min="0" class="input" placeholder="e.g. 4500" />
        </div>
      </template>

      <!-- ── Pricing ── -->
      <div class="section-heading">Pricing & Thresholds</div>

      <div class="field-row-3">
        <div class="field">
          <label class="label">Cost Price (Rs.)</label>
          <input v-model.number="form.cost_price" type="number" min="0" step="10" class="input" :class="{ 'input-error': errors.cost_price }" />
          <p v-if="errors.cost_price" class="err">{{ errors.cost_price }}</p>
        </div>
        <div class="field">
          <label class="label">Sell Price (Rs.)</label>
          <input v-model.number="form.sell_price" type="number" min="0" step="10" class="input" :class="{ 'input-error': errors.sell_price }" />
          <p v-if="errors.sell_price" class="err">{{ errors.sell_price }}</p>
        </div>
        <div class="field">
          <label class="label">Reorder Level</label>
          <input v-model.number="form.reorder_level" type="number" min="0" class="input" :class="{ 'input-error': errors.reorder_level }" />
          <p v-if="errors.reorder_level" class="err">{{ errors.reorder_level }}</p>
        </div>
      </div>

      <!-- Active toggle -->
      <div class="flex items-center gap-3">
        <input v-model="form.is_active" type="checkbox" id="is_active" class="w-4 h-4 accent-red-600" />
        <label for="is_active" class="text-sm font-medium text-gray-700 cursor-pointer">Active (visible in catalog)</label>
      </div>

    </div>

    <template #footer>
      <AppButton variant="secondary" @click="emit('close')">Cancel</AppButton>
      <AppButton variant="primary" :loading="submitting" @click="submit">
        {{ isEdit ? 'Save Changes' : 'Create Part' }}
      </AppButton>
    </template>
  </AppModal>
</template>

<style scoped>
.form-grid     { display: flex; flex-direction: column; gap: .875rem; }
.section-heading {
  font-size: .75rem; font-weight: 800; text-transform: uppercase;
  letter-spacing: .08em; color: #9ca3af;
  padding-top: .5rem; border-top: 1px solid #f3f4f6; margin-top: .25rem;
}
.section-heading:first-child { border-top: none; padding-top: 0; margin-top: 0; }
.field      { display: flex; flex-direction: column; gap: .3rem; flex: 1; min-width: 0; }
.field-row  { display: grid; grid-template-columns: 1fr 1fr; gap: .875rem; }
.field-row-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: .875rem; }
.req        { color: #e11d48; }
.err        { font-size: .8125rem; color: #dc2626; font-weight: 500; }
</style>
