<script setup>
/**
 * WhatsAppShare — modal that lets the user share a product/device
 * to a WhatsApp chat or group via the wa.me deep link.
 *
 * Props:
 *   open       — show/hide
 *   product    — object with product details to share
 *   type       — 'accessory' | 'device'
 */
import { ref, computed, watch } from 'vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppButton from '@/components/ui/AppButton.vue'

const props = defineProps({
  open:    { type: Boolean, required: true },
  product: { type: Object,  default: null  },
  type:    { type: String,  default: 'accessory' }, // 'accessory' | 'device'
})
const emit = defineEmits(['close'])

// ── Editable message text ──────────────────────────────────────────────────────
const message = ref('')
const phone   = ref('') // optional: direct to a specific number

// Re-generate message whenever product changes
watch(
  () => [props.product, props.open],
  () => {
    if (props.product && props.open) {
      message.value = buildMessage(props.product, props.type)
    }
  },
  { immediate: true }
)

function buildMessage(p, type) {
  const divider = '─────────────────────'
  if (type === 'device') {
    return [
      `📱 *New Stock Available!*`,
      divider,
      `*${p.brand} ${p.model}*`,
      ``,
      `✅ Condition: ${p.condition || 'N/A'}`,
      `📋 PTA Status: ${p.pta_status || 'N/A'}`,
      p.imei1 ? `🔢 IMEI: ${p.imei1}` : null,
      p.serial ? `🔖 Serial: ${p.serial}` : null,
      ``,
      `💰 *Price: Rs. ${Number(p.sell_price || 0).toLocaleString()}*`,
      ``,
      divider,
      `📞 Contact us for more info!`,
    ].filter(Boolean).join('\n')
  }

  // Accessory / product
  return [
    `🛍️ *New Product Available!*`,
    divider,
    `*${p.name}*`,
    p.brand    ? `🏷️ Brand: ${p.brand}`       : null,
    p.category ? `📦 Category: ${p.category}` : null,
    p.sku      ? `🔖 SKU: ${p.sku}`           : null,
    ``,
    `💰 *Price: Rs. ${Number(p.sell_price || 0).toLocaleString()}*`,
    p.description ? `\n📝 ${p.description}` : null,
    ``,
    divider,
    `📞 Contact us for more info!`,
  ].filter(Boolean).join('\n')
}

// ── Share actions ──────────────────────────────────────────────────────────────
const encodedMessage = computed(() => encodeURIComponent(message.value))

const waLink = computed(() => {
  const num = phone.value.replace(/\D/g, '')
  if (num) return `https://wa.me/${num}?text=${encodedMessage.value}`
  return `https://wa.me/?text=${encodedMessage.value}`
})

function shareToWhatsApp() {
  window.open(waLink.value, '_blank', 'noopener,noreferrer')
}

// ── Copy to clipboard ──────────────────────────────────────────────────────────
const copied = ref(false)
async function copyMessage() {
  try {
    await navigator.clipboard.writeText(message.value)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch {
    // fallback
    const ta = document.createElement('textarea')
    ta.value = message.value
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  }
}

// Character count
const charCount = computed(() => message.value.length)
</script>

<template>
  <AppModal
    :open="open"
    title="Share on WhatsApp"
    size="md"
    @close="emit('close')"
  >
    <!-- Header icon -->
    <div class="flex items-center gap-3 mb-4 p-3 rounded-xl bg-green-50 border border-green-100">
      <div class="wa-icon">
        <svg viewBox="0 0 24 24" fill="currentColor" class="w-6 h-6 text-white">
          <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
        </svg>
      </div>
      <div>
        <p class="text-sm font-semibold text-green-800">Share via WhatsApp</p>
        <p class="text-xs text-green-600 mt-0.5">Send product details to a chat or group</p>
      </div>
    </div>

    <div class="space-y-4">
      <!-- Optional phone number -->
      <div>
        <label class="label">Phone Number <span class="text-gray-400 normal-case font-normal">(optional — leave blank to pick a chat)</span></label>
        <div class="flex gap-2">
          <div class="flex items-center px-3 bg-gray-50 border border-r-0 border-gray-300 rounded-l-md text-sm text-gray-500 font-medium select-none">
            🇵🇰 +92
          </div>
          <input
            v-model="phone"
            type="tel"
            placeholder="3001234567"
            class="input rounded-l-none flex-1"
            maxlength="15"
          />
        </div>
        <p class="text-xs text-gray-400 mt-1">Include country code without +. E.g. 923001234567</p>
      </div>

      <!-- Message editor -->
      <div>
        <div class="flex items-center justify-between mb-1.5">
          <label class="label">Message</label>
          <span class="text-xs text-gray-400">{{ charCount }} chars</span>
        </div>
        <textarea
          v-model="message"
          class="input font-mono text-xs leading-relaxed resize-none"
          rows="12"
          style="font-family: 'Courier New', monospace; font-size: 11px;"
        />
        <p class="text-xs text-gray-400 mt-1">
          You can edit the message before sending. *Bold* formatting works in WhatsApp.
        </p>
      </div>

      <!-- Preview card -->
      <div class="rounded-xl overflow-hidden border border-gray-100">
        <div class="bg-gray-100 px-3 py-1.5 flex items-center gap-2">
          <div class="w-2 h-2 rounded-full bg-green-500" />
          <span class="text-xs text-gray-500 font-medium">Message Preview</span>
        </div>
        <div class="bg-[#e5ddd5] p-3">
          <div class="wa-bubble">
            <pre class="text-xs whitespace-pre-wrap break-words leading-relaxed">{{ message }}</pre>
            <div class="wa-bubble-time">{{ new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'}) }} ✓✓</div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <!-- Copy button -->
      <AppButton variant="secondary" @click="copyMessage">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path v-if="!copied" stroke-linecap="round" stroke-linejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
          <path v-else stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
        </svg>
        {{ copied ? 'Copied!' : 'Copy Text' }}
      </AppButton>

      <AppButton variant="secondary" @click="emit('close')">Cancel</AppButton>

      <!-- WhatsApp button -->
      <button class="wa-send-btn" @click="shareToWhatsApp">
        <svg viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4">
          <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
        </svg>
        Share on WhatsApp
      </button>
    </template>
  </AppModal>
</template>

<style scoped>
.wa-icon {
  width: 44px; height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #25d366, #128c7e);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(37,211,102,0.3);
}

.wa-bubble {
  background: white;
  border-radius: 0 10px 10px 10px;
  padding: 8px 10px 6px;
  max-width: 90%;
  box-shadow: 0 1px 2px rgba(0,0,0,0.12);
  position: relative;
}
.wa-bubble::before {
  content: '';
  position: absolute;
  top: 0; left: -7px;
  border-style: solid;
  border-width: 0 8px 8px 0;
  border-color: transparent white transparent transparent;
}
.wa-bubble-time {
  text-align: right;
  font-size: 10px;
  color: #999;
  margin-top: 4px;
}

.wa-send-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4375rem 1rem;
  border-radius: 8px;
  background: linear-gradient(135deg, #25d366, #128c7e);
  color: white;
  font-size: 0.8125rem;
  font-weight: 700;
  border: none;
  cursor: pointer;
  transition: all 150ms;
  box-shadow: 0 2px 8px rgba(37,211,102,0.3);
}
.wa-send-btn:hover {
  background: linear-gradient(135deg, #20bc5a, #0e7a6e);
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(37,211,102,0.4);
}
</style>
