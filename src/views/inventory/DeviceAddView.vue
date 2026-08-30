<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMockDataStore } from '@/stores/mockData'
import { useUiStore } from '@/stores/ui'
import AppButton from '@/components/ui/AppButton.vue'
import AppInput from '@/components/ui/AppInput.vue'
import ScannerInput from '@/components/pos/ScannerInput.vue'
import WhatsAppShare from '@/components/ui/WhatsAppShare.vue'

const mock   = useMockDataStore()
const router = useRouter()
const ui     = useUiStore()

const scannedImei  = ref('')
const duplicate    = ref(null)
const saving       = ref(false)
const savedDevice  = ref(null)   // holds device after save for WhatsApp
const showWhatsApp = ref(false)

const form = ref({
  imei1:       '',
  imei2:       '',
  serial:      '',
  brand:       '',
  model:       '',
  condition:   'Grade A',
  pta_status:  'PTA Approved',
  cost_price:  '',
  sell_price:  '',
  branch_id:   1,
})

const conditions = ['Grade A', 'Grade B', 'Grade C', 'Refurbished', 'For Parts']
const ptaOptions = ['PTA Approved', 'Non-PTA', 'PTA Blocked']

function handleScan(imei) {
  scannedImei.value = imei
  form.value.imei1  = imei
  const found = mock.findDevice(imei)
  duplicate.value = found
}

const hasErrors = computed(() =>
  !form.value.imei1 || !form.value.brand || !form.value.model || !form.value.sell_price
)

async function handleSubmit() {
  if (hasErrors.value) { ui.toastWarn('Fill all required fields'); return }
  if (duplicate.value) { ui.toastWarn('This IMEI already exists in inventory'); return }

  saving.value = true
  await new Promise(r => setTimeout(r, 150))

  const device = mock.addDevice({
    imei1:       form.value.imei1,
    imei2:       form.value.imei2 || null,
    serial:      form.value.serial,
    brand:       form.value.brand,
    model:       form.value.model,
    condition:   form.value.condition,
    pta_status:  form.value.pta_status,
    cost_price:  Number(form.value.cost_price) || 0,
    sell_price:  Number(form.value.sell_price) || 0,
    branch_id:   form.value.branch_id,
  })

  savedDevice.value = device
  saving.value = false
  ui.toastSuccess(`Device added — ${form.value.brand} ${form.value.model}`)
}

function goToDevice() {
  if (savedDevice.value) {
    router.push(`/inventory/devices/${savedDevice.value.id}`)
  }
}
</script>

<template>
  <div class="space-y-4 max-w-2xl">
    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-gray-900">Add Device</h2>
      <AppButton variant="ghost" @click="router.back()">← Back</AppButton>
    </div>

    <!-- ── Success state after save ──────────────────────────────────────── -->
    <div v-if="savedDevice" class="card p-5 text-center space-y-4">
      <div class="flex items-center justify-center">
        <div class="w-14 h-14 rounded-full bg-green-100 flex items-center justify-center">
          <svg class="w-7 h-7 text-green-600" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
          </svg>
        </div>
      </div>
      <div>
        <p class="text-lg font-bold text-gray-900">Device Added Successfully!</p>
        <p class="text-sm text-gray-500 mt-1">
          {{ savedDevice.brand }} {{ savedDevice.model }} has been added to inventory.
        </p>
      </div>

      <!-- Action buttons -->
      <div class="flex items-center justify-center gap-3 flex-wrap">
        <!-- WhatsApp share button -->
        <button class="wa-success-btn" @click="showWhatsApp = true">
          <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4">
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
          </svg>
          Share on WhatsApp
        </button>

        <AppButton variant="primary" @click="goToDevice">View Device →</AppButton>
        <AppButton variant="secondary" @click="savedDevice = null; Object.keys(form).forEach(k => form[k] = k === 'condition' ? 'Grade A' : k === 'pta_status' ? 'PTA Approved' : k === 'branch_id' ? 1 : '')">Add Another</AppButton>
      </div>
    </div>

    <!-- ── Form (hidden after save) ───────────────────────────────────────── -->
    <template v-if="!savedDevice">
      <!-- Scanner -->
      <div class="card p-4 space-y-3">
        <p class="label">Scan IMEI</p>
        <ScannerInput placeholder="Scan IMEI barcode or type manually…" @scan="handleScan" />
        <div v-if="duplicate" class="flex items-center gap-2 px-3 py-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
          <svg class="w-4 h-4 shrink-0 text-red-500" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
          </svg>
          <span>Duplicate IMEI — <strong>{{ duplicate.brand }} {{ duplicate.model }}</strong> already in inventory</span>
        </div>
      </div>

      <!-- Form -->
      <div class="card p-4 space-y-4">
        <div class="grid grid-cols-2 gap-3">
          <AppInput v-model="form.imei1"      label="IMEI 1 *"          placeholder="15 digits" required data-no-scanner-refocus />
          <AppInput v-model="form.imei2"      label="IMEI 2"            placeholder="Optional"  data-no-scanner-refocus />
          <AppInput v-model="form.serial"     label="Serial Number"                             data-no-scanner-refocus />
          <AppInput v-model="form.brand"      label="Brand *"           placeholder="e.g. Samsung" required data-no-scanner-refocus />
          <AppInput v-model="form.model"      label="Model *"           placeholder="e.g. Galaxy A54" required data-no-scanner-refocus />
          <div>
            <label class="label">Condition *</label>
            <select v-model="form.condition" class="input" data-no-scanner-refocus>
              <option v-for="c in conditions" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>
          <div>
            <label class="label">PTA Status</label>
            <select v-model="form.pta_status" class="input" data-no-scanner-refocus>
              <option v-for="p in ptaOptions" :key="p" :value="p">{{ p }}</option>
            </select>
          </div>
          <AppInput v-model="form.cost_price" label="Cost Price (Rs.)"  type="number" min="0"  data-no-scanner-refocus />
          <AppInput v-model="form.sell_price" label="Sell Price (Rs.) *" type="number" min="0" required data-no-scanner-refocus />
        </div>

        <div class="flex gap-2 pt-2">
          <AppButton variant="secondary" @click="router.back()">Cancel</AppButton>
          <AppButton
            variant="primary"
            :loading="saving"
            :disabled="hasErrors || !!duplicate"
            @click="handleSubmit"
          >
            Add Device
          </AppButton>
        </div>
      </div>
    </template>

    <!-- WhatsApp share modal -->
    <WhatsAppShare
      :open="showWhatsApp"
      :product="savedDevice"
      type="device"
      @close="showWhatsApp = false"
    />
  </div>
</template>

<style scoped>
.wa-success-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1.125rem;
  border-radius: 9px;
  background: linear-gradient(135deg, #25d366, #128c7e);
  color: white;
  font-size: 0.8125rem;
  font-weight: 700;
  border: none;
  cursor: pointer;
  transition: all 150ms;
  box-shadow: 0 3px 10px rgba(37,211,102,0.3);
}
.wa-success-btn:hover {
  background: linear-gradient(135deg, #20bc5a, #0e7a6e);
  transform: translateY(-1px);
  box-shadow: 0 5px 16px rgba(37,211,102,0.4);
}
</style>
