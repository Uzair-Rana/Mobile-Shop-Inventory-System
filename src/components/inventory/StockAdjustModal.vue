<script setup>
/**
 * StockAdjustModal
 * ─────────────────────────────────────────────────────────────────────────────
 * Unified manual stock-adjustment dialog for:
 *   mode='accessory'  → qty-change + reason → POST /accessories/:id/adjust_stock/
 *   mode='device'     → new lifecycle state + reason → POST /devices/:id/adjust_lifecycle/
 *
 * Every submission is atomic on the backend: StockMovement + AuditTrail row.
 *
 * Props:
 *   open    — show/hide
 *   mode    — 'accessory' | 'device'
 *   item    — the product or unit object being adjusted
 *
 * Emits:
 *   close   — close without change
 *   saved   — adjustment committed; parent should reload
 */
import { ref, computed, watch, onMounted } from 'vue'
import { inventoryApi } from '@/api/inventory'
import { useUiStore } from '@/stores/ui'
import AppModal from '@/components/ui/AppModal.vue'
import AppButton from '@/components/ui/AppButton.vue'

const props = defineProps({
  open: { type: Boolean, required: true },
  mode: { type: String,  default: 'accessory' }, // 'accessory' | 'device'
  item: { type: Object,  default: null },
})
const emit = defineEmits(['close', 'saved'])

const ui = useUiStore()

// ── Reason codes (loaded from backend once) ───────────────────────────────────
const reasonOptions  = ref([])
const deviceStates   = ref([])
const loadingReasons = ref(false)

async function loadReasons() {
  if (reasonOptions.value.length) return // already loaded
  loadingReasons.value = true
  try {
    const { data } = await inventoryApi.getAdjustmentReasons()
    reasonOptions.value = props.mode === 'device' ? data.device    : data.accessory
    deviceStates.value  = data.device_states || []
  } catch { /* use fallback below */ } finally { loadingReasons.value = false }
}

// ── Form state ────────────────────────────────────────────────────────────────
const qtyChange   = ref(0)
const newState    = ref('')
const reasonCode  = ref('')
const reasonNote  = ref('')
const submitting  = ref(false)
const errors      = ref({})

function reset() {
  qtyChange.value  = 0
  newState.value   = ''
  reasonCode.value = ''
  reasonNote.value = ''
  errors.value     = {}
}

watch(() => props.open, (val) => {
  if (val) { reset(); loadReasons() }
})

// ── Derived helpers ───────────────────────────────────────────────────────────
const isAccessory = computed(() => props.mode === 'accessory')
const isDevice    = computed(() => props.mode === 'device')

const currentQty = computed(() => props.item?.stock_qty ?? 0)
const newQty     = computed(() => currentQty.value + Number(qtyChange.value || 0))
const qtyDelta   = computed(() => Number(qtyChange.value || 0))

const selectedReasonLabel = computed(() =>
  reasonOptions.value.find(r => r.code === reasonCode.value)?.label ?? ''
)
const needsNote = computed(() => reasonCode.value === 'other')

const previewLabel = computed(() => {
  if (!reasonCode.value) return ''
  const base = selectedReasonLabel.value
  return reasonNote.value ? `${base}: ${reasonNote.value}` : base
})

const modalTitle = computed(() =>
  isAccessory.value
    ? `Adjust Stock — ${props.item?.name ?? ''}`
    : `Adjust Device State — ${props.item?.brand ?? ''} ${props.item?.model ?? ''}`
)

// ── Validation ────────────────────────────────────────────────────────────────
function validate() {
  const e = {}
  if (!reasonCode.value)         e.reasonCode = 'Select a reason.'
  if (needsNote.value && !reasonNote.value.trim()) e.reasonNote = 'Describe the reason.'

  if (isAccessory.value) {
    if (qtyDelta.value === 0) e.qty = 'Quantity change cannot be zero.'
    if (newQty.value < 0)     e.qty = `Cannot reduce below zero (current: ${currentQty.value}).`
  }
  if (isDevice.value) {
    if (!newState.value) e.newState = 'Select a new state.'
    if (newState.value === props.item?.lifecycle_state)
      e.newState = 'Device is already in this state.'
  }
  errors.value = e
  return Object.keys(e).length === 0
}

// ── Submit ────────────────────────────────────────────────────────────────────
async function submit() {
  if (!validate()) return
  submitting.value = true
  try {
    if (isAccessory.value) {
      await inventoryApi.adjustStock(props.item.id, {
        qty_change:  qtyDelta.value,
        reason_code: reasonCode.value,
        reason_note: reasonNote.value,
      })
    } else {
      await inventoryApi.adjustLifecycle(props.item.id, {
        new_state:   newState.value,
        reason_code: reasonCode.value,
        reason_note: reasonNote.value,
      })
    }
    ui.toastSuccess?.('Adjustment saved and audit recorded.')
    emit('saved')
  } catch (e) {
    const msg = e.displayMessage || e.response?.data?.detail || 'Adjustment failed.'
    ui.toastError?.(msg)
    // Map field errors back
    if (e.response?.data) {
      const d = e.response.data
      if (d.reason_note) errors.value.reasonNote = Array.isArray(d.reason_note) ? d.reason_note[0] : d.reason_note
      if (d.qty_change)  errors.value.qty        = Array.isArray(d.qty_change)  ? d.qty_change[0]  : d.qty_change
    }
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <AppModal :open="open" :title="modalTitle" size="md" @close="emit('close')">

    <div class="adj-body">

      <!-- ── Context strip ──────────────────────────────────────────────── -->
      <div class="context-strip">
        <div v-if="isAccessory" class="context-item">
          <span class="ctx-label">Current stock</span>
          <span class="ctx-value">{{ currentQty }} units</span>
        </div>
        <div v-if="isDevice" class="context-item">
          <span class="ctx-label">Current state</span>
          <span class="ctx-value ctx-state">{{ item?.lifecycle_state?.replace('_', ' ') ?? '—' }}</span>
        </div>
        <div v-if="isAccessory && item" class="context-item">
          <span class="ctx-label">SKU</span>
          <span class="ctx-value font-mono">{{ item.sku }}</span>
        </div>
        <div v-if="isDevice && item" class="context-item">
          <span class="ctx-label">IMEI</span>
          <span class="ctx-value font-mono">{{ item.imei1 }}</span>
        </div>
      </div>

      <!-- ── Accessory: qty change ──────────────────────────────────────── -->
      <div v-if="isAccessory" class="field-group">
        <label class="field-label">Quantity Change</label>
        <p class="field-hint">Positive to add stock, negative to remove.</p>
        <div class="qty-row">
          <button class="qty-btn" :disabled="qtyDelta <= -currentQty" @click="qtyChange--">−</button>
          <input
            v-model.number="qtyChange"
            type="number"
            class="input qty-input"
            :class="{ 'input-error': errors.qty }"
            placeholder="0"
          />
          <button class="qty-btn" @click="qtyChange++">+</button>
        </div>
        <p v-if="errors.qty" class="field-error">{{ errors.qty }}</p>

        <!-- Live preview -->
        <div v-if="qtyDelta !== 0" class="qty-preview" :class="qtyDelta > 0 ? 'preview-add' : 'preview-remove'">
          <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
            <path v-if="qtyDelta > 0" stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
            <path v-else              stroke-linecap="round" stroke-linejoin="round" d="M20 12H4"/>
          </svg>
          <span>
            {{ currentQty }} → <strong>{{ newQty }}</strong>
            ({{ qtyDelta > 0 ? '+' : '' }}{{ qtyDelta }})
          </span>
        </div>
      </div>

      <!-- ── Device: new lifecycle state ───────────────────────────────── -->
      <div v-if="isDevice" class="field-group">
        <label class="field-label">New State</label>
        <p class="field-hint">Select the state this device should be moved to.</p>
        <div v-if="loadingReasons" class="skeleton h-10 rounded-lg" />
        <div v-else class="state-grid">
          <button
            v-for="s in deviceStates"
            :key="s.value"
            class="state-pill"
            :class="{
              'state-active':    newState === s.value,
              'state-current':   item?.lifecycle_state === s.value,
              'state-disabled':  item?.lifecycle_state === s.value,
            }"
            :disabled="item?.lifecycle_state === s.value"
            @click="newState = s.value"
          >
            <span class="state-dot" :class="`dot-${s.value}`" />
            {{ s.label }}
            <span v-if="item?.lifecycle_state === s.value" class="state-current-tag">current</span>
          </button>
        </div>
        <p v-if="errors.newState" class="field-error">{{ errors.newState }}</p>
      </div>

      <!-- ── Reason code (both modes) ──────────────────────────────────── -->
      <div class="field-group">
        <label class="field-label">Reason <span class="required">*</span></label>
        <p class="field-hint">Select the authorized reason for this adjustment.</p>

        <div v-if="loadingReasons" class="skeleton h-28 rounded-lg" />
        <div v-else class="reason-grid">
          <button
            v-for="r in reasonOptions"
            :key="r.code"
            class="reason-pill"
            :class="{ 'reason-active': reasonCode === r.code }"
            @click="reasonCode = r.code"
          >
            <span class="reason-check">
              <svg v-if="reasonCode === r.code" class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
            </span>
            {{ r.label }}
          </button>
        </div>
        <p v-if="errors.reasonCode" class="field-error">{{ errors.reasonCode }}</p>
      </div>

      <!-- ── Free-text note ─────────────────────────────────────────────── -->
      <div class="field-group">
        <label class="field-label">
          Note / Details
          <span v-if="needsNote" class="required">* required</span>
          <span v-else class="optional">(optional)</span>
        </label>
        <textarea
          v-model="reasonNote"
          rows="3"
          class="input"
          :class="{ 'input-error': errors.reasonNote }"
          placeholder="Additional details about this adjustment…"
        />
        <p v-if="errors.reasonNote" class="field-error">{{ errors.reasonNote }}</p>
      </div>

      <!-- ── Audit notice ───────────────────────────────────────────────── -->
      <div v-if="previewLabel" class="audit-notice">
        <svg class="w-4 h-4 shrink-0 text-amber-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
        </svg>
        <div class="min-w-0">
          <p class="audit-title">This action creates an immutable audit record.</p>
          <p class="audit-reason">Reason: <strong>{{ previewLabel }}</strong></p>
        </div>
      </div>

    </div>

    <template #footer>
      <AppButton variant="secondary" @click="emit('close')">Cancel</AppButton>
      <AppButton
        variant="primary"
        :loading="submitting"
        :disabled="submitting"
        @click="submit"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
        </svg>
        Confirm Adjustment
      </AppButton>
    </template>
  </AppModal>
</template>

<style scoped>
.adj-body { display: flex; flex-direction: column; gap: 1.25rem; }

/* ── Context strip ── */
.context-strip {
  display: flex; gap: 1.5rem; flex-wrap: wrap;
  background: #f9fafb; border: 1px solid #e5e7eb;
  border-radius: 10px; padding: .875rem 1rem;
}
.context-item { display: flex; flex-direction: column; gap: .15rem; }
.ctx-label    { font-size: .75rem; font-weight: 700; text-transform: uppercase; letter-spacing: .06em; color: #9ca3af; }
.ctx-value    { font-size: 1rem; font-weight: 700; color: #111827; }
.ctx-state    { text-transform: capitalize; color: #e11d48; }

/* ── Field group ── */
.field-group  { display: flex; flex-direction: column; gap: .5rem; }
.field-label  { font-size: .9375rem; font-weight: 700; color: #111827; }
.field-hint   { font-size: .875rem; color: #6b7280; margin-top: -.25rem; }
.field-error  { font-size: .875rem; color: #dc2626; font-weight: 500; }
.required     { color: #e11d48; margin-left: .2rem; }
.optional     { font-size: .8125rem; color: #9ca3af; font-weight: 400; margin-left: .25rem; }

/* ── Qty controls ── */
.qty-row {
  display: flex; align-items: center; gap: .5rem; max-width: 220px;
}
.qty-btn {
  width: 40px; height: 40px; border-radius: 10px;
  border: 1.5px solid #e5e7eb; background: white;
  font-size: 1.25rem; font-weight: 700; color: #374151;
  cursor: pointer; transition: all 120ms;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.qty-btn:hover:not(:disabled) { border-color: #e11d48; color: #e11d48; background: #fff1f2; }
.qty-btn:disabled { opacity: .35; cursor: not-allowed; }
.qty-input { text-align: center; font-size: 1.125rem; font-weight: 700; width: 100px; flex-shrink: 0; }

.qty-preview {
  display: inline-flex; align-items: center; gap: .5rem;
  border-radius: 8px; padding: .5rem .875rem;
  font-size: .9375rem; font-weight: 500;
}
.preview-add    { background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }
.preview-remove { background: #fff1f2; color: #be123c; border: 1px solid #fecdd3; }

/* ── Device states ── */
.state-grid { display: flex; flex-wrap: wrap; gap: .5rem; }
.state-pill {
  display: inline-flex; align-items: center; gap: .5rem;
  padding: .5rem .875rem; border-radius: 99px;
  border: 1.5px solid #e5e7eb; background: white;
  font-size: .9rem; font-weight: 500; color: #374151;
  cursor: pointer; transition: all 120ms;
}
.state-pill:hover:not(:disabled) { border-color: #e11d48; color: #be123c; background: #fff1f2; }
.state-active   { border-color: #e11d48 !important; background: #fff1f2 !important; color: #be123c !important; font-weight: 700; }
.state-disabled { opacity: .55; cursor: not-allowed; }
.state-current-tag { font-size: .7rem; background: #e5e7eb; color: #6b7280; padding: .1rem .4rem; border-radius: 99px; margin-left: .25rem; }

.state-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.dot-in_stock  { background: #22c55e; }
.dot-defective { background: #ef4444; }
.dot-in_repair { background: #f97316; }
.dot-reserved  { background: #3b82f6; }
.dot-returned  { background: #8b5cf6; }

/* ── Reason grid ── */
.reason-grid { display: flex; flex-wrap: wrap; gap: .5rem; }
.reason-pill {
  display: inline-flex; align-items: center; gap: .4rem;
  padding: .4375rem .875rem; border-radius: 99px;
  border: 1.5px solid #e5e7eb; background: white;
  font-size: .875rem; font-weight: 500; color: #374151;
  cursor: pointer; transition: all 120ms;
}
.reason-pill:hover   { border-color: #d1d5db; background: #f9fafb; }
.reason-active       { border-color: #e11d48 !important; background: #fff1f2 !important; color: #be123c !important; font-weight: 700; }
.reason-check {
  width: 16px; height: 16px; border-radius: 50%; flex-shrink: 0;
  border: 1.5px solid currentColor;
  display: flex; align-items: center; justify-content: center;
}

/* ── Audit notice ── */
.audit-notice {
  display: flex; align-items: flex-start; gap: .75rem;
  background: #fffbeb; border: 1px solid #fde68a;
  border-radius: 10px; padding: .875rem 1rem;
}
.audit-title  { font-size: .875rem; font-weight: 600; color: #92400e; }
.audit-reason { font-size: .875rem; color: #78350f; margin-top: .15rem; }
</style>
