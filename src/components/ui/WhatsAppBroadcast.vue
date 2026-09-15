<script setup>
/**
 * WhatsAppBroadcast — share MULTIPLE items at once as a single catalog
 * ("sheet") message, with an editable intro line. Also exports the same
 * selection as a CSV sheet for broadcasting outside WhatsApp.
 *
 * Props:
 *   open      — show/hide
 *   items     — array of products/devices to broadcast
 *   shopName  — header line (shop name)
 */
import { ref, computed, watch } from 'vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppButton from '@/components/ui/AppButton.vue'

const props = defineProps({
  open:     { type: Boolean, required: true },
  items:    { type: Array,   default: () => [] },
  shopName: { type: String,  default: 'DEVNEST Mobile Shop' },
})
const emit = defineEmits(['close'])

// The "specific line" the client wants — editable, remembered per open.
const introLine = ref('📢 Latest stock available now! Prices below 👇')
const phone     = ref('')

function itemName(it) {
  return it.name || `${it.brand || ''} ${it.model || it.model_name || ''}`.trim()
}
function itemPrice(it) {
  return Number(it.sell_price ?? it.price ?? it.selling_price ?? 0)
}
function itemLine(it) {
  const bits = [`• *${itemName(it)}*`]
  if (it.imei1 || it.imei) bits.push(`(IMEI: ${it.imei1 || it.imei})`)
  bits.push(`— Rs. ${itemPrice(it).toLocaleString()}`)
  return bits.join(' ')
}

const message = computed(() => {
  const divider = '─────────────────────'
  return [
    `*${props.shopName}*`,
    introLine.value,
    divider,
    ...props.items.map(itemLine),
    divider,
    `📞 Contact us to order!`,
  ].join('\n')
})

const encoded = computed(() => encodeURIComponent(message.value))
const waLink = computed(() => {
  const num = phone.value.replace(/\D/g, '')
  return num ? `https://wa.me/${num}?text=${encoded.value}` : `https://wa.me/?text=${encoded.value}`
})

function shareToWhatsApp() {
  window.open(waLink.value, '_blank', 'noopener,noreferrer')
}

const copied = ref(false)
async function copyMessage() {
  try {
    await navigator.clipboard.writeText(message.value)
  } catch {
    const ta = document.createElement('textarea')
    ta.value = message.value
    document.body.appendChild(ta); ta.select(); document.execCommand('copy'); document.body.removeChild(ta)
  }
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}

// Download the selection as a CSV "sheet"
function downloadSheet() {
  const rows = [['Item', 'IMEI', 'Price (PKR)']]
  props.items.forEach(it => rows.push([itemName(it), it.imei1 || it.imei || '', itemPrice(it)]))
  const csv = rows.map(r => r.map(c => `"${String(c).replace(/"/g, '""')}"`).join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `stock-broadcast-${new Date().toISOString().slice(0, 10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <AppModal :open="open" title="WhatsApp Broadcast" size="md" @close="emit('close')">
    <div class="space-y-4">
      <p class="text-sm text-gray-600">
        Broadcasting <b>{{ items.length }}</b> item(s) as one message.
      </p>

      <div>
        <label class="label">Intro line</label>
        <input v-model="introLine" type="text" class="input" placeholder="Your broadcast headline…" />
      </div>

      <div>
        <label class="label">Phone <span class="text-gray-400 normal-case font-normal">(optional)</span></label>
        <input v-model="phone" type="tel" class="input" placeholder="923001234567" maxlength="15" />
      </div>

      <div>
        <label class="label">Preview</label>
        <textarea :value="message" readonly class="input font-mono text-xs leading-relaxed resize-none" rows="10" />
      </div>
    </div>

    <template #footer>
      <AppButton variant="secondary" @click="downloadSheet">⬇ Download Sheet (CSV)</AppButton>
      <AppButton variant="secondary" @click="copyMessage">{{ copied ? '✓ Copied' : 'Copy' }}</AppButton>
      <AppButton variant="primary" :disabled="items.length === 0" @click="shareToWhatsApp">Share on WhatsApp</AppButton>
    </template>
  </AppModal>
</template>
