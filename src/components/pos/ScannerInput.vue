<script setup>
/**
 * ScannerInput — the primary POS barcode/IMEI scanner field.
 *
 * Keyboard-first design:
 * - Auto-focuses on mount and re-focuses after each scan
 * - Rapid keystrokes (scanner) are buffered and committed on Enter
 * - Emits 'scan' with the raw barcode/IMEI string
 * - Never requires a mouse click to regain focus
 */
import { ref, onMounted, onUnmounted } from 'vue'

const emit = defineEmits(['scan'])
const props = defineProps({
  placeholder: { type: String, default: 'Scan barcode / IMEI or type SKU…' },
  disabled:    { type: Boolean, default: false },
})

const inputRef   = ref(null)
const inputValue = ref('')
const scanning   = ref(false)

// Scanner parameters
const SPEED_THRESHOLD = 50   // ms between keystrokes to classify as scanner
const MIN_LENGTH      = 4

let lastKeyTime  = 0
let scanBuffer   = ''
let scanTimer    = null
let lastScanTime = 0

function handleKeydown(e) {
  if (props.disabled) return
  const now     = Date.now()
  const elapsed = now - lastKeyTime
  lastKeyTime   = now

  if (e.key === 'Enter') {
    e.preventDefault()
    const val = (scanBuffer || inputValue.value).trim()
    if (val.length >= MIN_LENGTH) {
      // Debounce duplicate scans (scanner sometimes fires twice)
      if (now - lastScanTime < 300) { scanBuffer = ''; inputValue.value = ''; return }
      lastScanTime = now
      scanning.value = true
      emit('scan', val)
      setTimeout(() => {
        scanning.value = false
        inputRef.value?.focus()
      }, 200)
    }
    scanBuffer = ''
    inputValue.value = ''
    clearTimeout(scanTimer)
    return
  }

  if (elapsed < SPEED_THRESHOLD && e.key.length === 1) {
    scanBuffer += e.key
  } else {
    scanBuffer = ''
  }

  clearTimeout(scanTimer)
  scanTimer = setTimeout(() => { scanBuffer = '' }, 600)
}

function handleInput(e) {
  inputValue.value = e.target.value
}

// Re-focus if user clicks anywhere on the POS page body
function handleBodyClick(e) {
  if (!props.disabled && !e.target.closest('[data-no-scanner-refocus]')) {
    inputRef.value?.focus()
  }
}

onMounted(() => {
  inputRef.value?.focus()
  document.addEventListener('click', handleBodyClick)
})
onUnmounted(() => {
  document.removeEventListener('click', handleBodyClick)
  clearTimeout(scanTimer)
})

defineExpose({ focus: () => inputRef.value?.focus() })
</script>

<template>
  <div class="relative">
    <svg
      class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none"
      :class="scanning ? 'text-blue-500 animate-pulse' : 'text-gray-400'"
      fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5a7.5 7.5 0 100 15 7.5 7.5 0 000-15zm0 0V3M21 21l-4.35-4.35"/>
    </svg>
    <input
      ref="inputRef"
      :value="inputValue"
      :placeholder="placeholder"
      :disabled="disabled"
      autocomplete="off"
      autocorrect="off"
      autocapitalize="off"
      spellcheck="false"
      class="scanner-input w-full pl-9 pr-4 py-3 text-sm rounded-lg border-2 border-gray-200 focus:border-blue-500 bg-white transition-colors"
      :class="scanning ? 'border-blue-400 bg-blue-50' : ''"
      aria-label="Product scanner / search"
      @keydown="handleKeydown"
      @input="handleInput"
    />
    <span
      v-if="scanning"
      class="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-blue-500 font-medium animate-pulse"
    >Scanning…</span>
  </div>
</template>
