<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMockDataStore } from '@/stores/mockData'
import { formatMoney } from '@/utils/money'
import { usePrint } from '@/composables/usePrint'
import { settingsApi } from '@/api/settings'
import AppButton from '@/components/ui/AppButton.vue'

const mock = useMockDataStore()
const { printDocument } = usePrint()

const showFields = ref({ imei: true, model: true, price: true, pta: false, brand: true })
const selectedIds = ref(new Set())
const search = ref('')
const shopName = ref('DEVNEST Mobile Shop')

onMounted(async () => {
  try {
    const { data } = await settingsApi.getCompany()
    if (data?.name) shopName.value = data.name
  } catch { /* keep default */ }
})

const devices = computed(() => {
  const q = search.value.toLowerCase()
  return mock.devices.filter(d =>
    d.lifecycle_state === 'in_stock' &&
    (!q || `${d.brand} ${d.model} ${d.imei1}`.toLowerCase().includes(q))
  )
})

function toggleDevice(id) {
  if (selectedIds.value.has(id)) selectedIds.value.delete(id)
  else selectedIds.value.add(id)
}

function selectAll() {
  devices.value.forEach(d => selectedIds.value.add(d.id))
}
function clearAll() {
  selectedIds.value.clear()
}

const selectedDevices = computed(() =>
  mock.devices.filter(d => selectedIds.value.has(d.id))
)

function printLabels() {
  // Print ONLY the isolated label sheet (with shop name) — not the whole app page.
  printDocument('barcode-print-area', `${shopName.value} — Barcode Labels`)
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-bold text-gray-900">Barcode Labels</h2>
      <AppButton variant="primary" :disabled="selectedIds.size === 0" @click="printLabels">
        Print {{ selectedIds.size || '' }} Labels
      </AppButton>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-3 gap-4">
      <!-- Left: selection + config -->
      <div class="xl:col-span-1 space-y-3">
        <div class="card p-3 space-y-2">
          <p class="label">Label Fields</p>
          <label v-for="(val, key) in showFields" :key="key" class="flex items-center gap-2 text-sm cursor-pointer">
            <input type="checkbox" v-model="showFields[key]" class="rounded border-gray-300 text-blue-600" />
            {{ { imei: 'IMEI', model: 'Model', price: 'Price', pta: 'PTA Status', brand: 'Brand' }[key] }}
          </label>
        </div>

        <div class="card p-3 space-y-2">
          <div class="flex items-center justify-between">
            <p class="label">Devices</p>
            <div class="flex gap-2">
              <button class="text-xs text-blue-600 hover:underline" @click="selectAll">All</button>
              <button class="text-xs text-gray-500 hover:underline" @click="clearAll">None</button>
            </div>
          </div>
          <input v-model="search" type="search" class="input input-sm" placeholder="Filter…" data-no-scanner-refocus />
          <div class="max-h-64 overflow-y-auto space-y-0.5">
            <label
              v-for="d in devices"
              :key="d.id"
              class="flex items-center gap-2 text-xs p-1.5 hover:bg-gray-50 rounded cursor-pointer"
            >
              <input
                type="checkbox"
                :checked="selectedIds.has(d.id)"
                class="rounded border-gray-300 text-blue-600"
                @change="toggleDevice(d.id)"
              />
              <span class="truncate">{{ d.brand }} {{ d.model }}</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Right: label preview -->
      <div class="xl:col-span-2">
        <div class="card p-3">
          <p class="label mb-3">Preview (4-per-row)</p>
          <div class="grid grid-cols-2 gap-2 print-labels">
            <div
              v-for="d in selectedDevices"
              :key="d.id"
              class="border border-gray-300 rounded p-2 text-xs space-y-0.5 bg-white"
            >
              <p v-if="showFields.brand" class="font-bold text-gray-900">{{ d.brand }}</p>
              <p v-if="showFields.model" class="text-gray-800">{{ d.model }}</p>
              <p v-if="showFields.imei" class="font-mono text-gray-600 text-[10px]">{{ d.imei1 }}</p>
              <p v-if="showFields.pta" class="text-[10px]" :class="d.pta_status === 'PTA Approved' ? 'text-green-600' : 'text-red-500'">
                {{ d.pta_status }}
              </p>
              <p v-if="showFields.price" class="font-bold text-gray-900">{{ formatMoney(d.sell_price) }}</p>
            </div>
          </div>
          <p v-if="selectedDevices.length === 0" class="text-center text-sm text-gray-400 py-8">Select devices to preview labels</p>
        </div>
      </div>
    </div>

    <!-- Hidden isolated print area — only this is sent to the printer -->
    <div id="barcode-print-area" style="display:none">
      <div style="text-align:center; margin-bottom:14px; border-bottom:2px solid #111; padding-bottom:8px">
        <div style="font-size:18px; font-weight:800">{{ shopName }}</div>
        <div style="font-size:11px; color:#666">Product Labels</div>
      </div>
      <div style="display:flex; flex-wrap:wrap; gap:8px">
        <div
          v-for="d in selectedDevices"
          :key="'p-' + d.id"
          style="width:31%; border:1px solid #999; border-radius:6px; padding:8px; box-sizing:border-box"
        >
          <div v-if="showFields.brand" style="font-weight:700; font-size:13px">{{ d.brand }}</div>
          <div v-if="showFields.model" style="font-size:12px">{{ d.model }}</div>
          <div v-if="showFields.imei" style="font-family:monospace; font-size:10px; color:#444">{{ d.imei1 }}</div>
          <div v-if="showFields.pta" style="font-size:10px">{{ d.pta_status }}</div>
          <div v-if="showFields.price" style="font-weight:700; font-size:13px">{{ formatMoney(d.sell_price) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>
