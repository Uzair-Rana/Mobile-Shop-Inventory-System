<script setup>
import { computed } from 'vue'
import { formatMoney } from '@/utils/money'
import { useCartStore } from '@/stores/cart'
import { usePermissions } from '@/composables/usePermissions'

const props = defineProps({
  item: { type: Object, required: true },
})

const cart  = useCartStore()
const perms = usePermissions()

const lineTotal = computed(() => {
  const gross = props.item.price * props.item.qty
  const disc  = props.item.discount_abs > 0
    ? props.item.discount_abs
    : gross * (props.item.discount_pct / 100)
  return gross - disc
})

function onQtyChange(e) {
  cart.updateQty(props.item.id, e.target.value)
}
function onPriceChange(e) {
  cart.updatePrice(props.item.id, e.target.value)
}
function onDiscountChange(e) {
  cart.updateDiscount(props.item.id, { abs: parseFloat(e.target.value) || 0 })
}
</script>

<template>
  <div class="flex items-start gap-2 py-2 border-b border-gray-100 last:border-0 group">
    <!-- Item info -->
    <div class="flex-1 min-w-0">
      <p class="text-sm font-medium text-gray-900 truncate">{{ item.name }}</p>
      <div class="flex items-center gap-2 mt-0.5">
        <span class="text-xs text-gray-400">{{ item.sku }}</span>
        <span v-if="item.imei" class="text-xs font-mono text-gray-500">{{ item.imei }}</span>
      </div>
    </div>

    <!-- Price (editable, requires discount permission) -->
    <div class="flex flex-col items-end gap-1 shrink-0">
      <div class="flex items-center gap-1">
        <!-- Unit price — editable if canManageDiscounts -->
        <input
          v-if="perms.canManageDiscounts.value"
          :value="item.price"
          type="number"
          min="0"
          step="1"
          class="w-24 text-right text-sm border border-gray-200 rounded px-1.5 py-0.5 focus:outline-none focus:border-blue-400"
          title="Unit price"
          data-no-scanner-refocus
          @change="onPriceChange"
        />
        <span v-else class="text-sm text-gray-700 w-24 text-right money">{{ formatMoney(item.price) }}</span>

        <!-- Qty (serialised units are locked at 1) -->
        <input
          v-if="item.type !== 'unit'"
          :value="item.qty"
          type="number"
          min="1"
          class="w-12 text-center text-sm border border-gray-200 rounded px-1 py-0.5 focus:outline-none focus:border-blue-400"
          title="Quantity"
          data-no-scanner-refocus
          @change="onQtyChange"
        />
        <span v-else class="text-sm text-gray-500 w-12 text-center">×1</span>
      </div>

      <!-- Discount field -->
      <div v-if="perms.canManageDiscounts.value" class="flex items-center gap-1">
        <span class="text-xs text-gray-400">Disc</span>
        <input
          :value="item.discount_abs"
          type="number"
          min="0"
          step="1"
          class="w-20 text-right text-xs border border-gray-200 rounded px-1.5 py-0.5 focus:outline-none focus:border-blue-400"
          placeholder="0"
          title="Discount amount"
          data-no-scanner-refocus
          @change="onDiscountChange"
        />
      </div>

      <!-- Line total -->
      <span class="text-sm font-semibold text-gray-900 money">{{ formatMoney(lineTotal) }}</span>
    </div>

    <!-- Remove button -->
    <button
      class="opacity-0 group-hover:opacity-100 transition-opacity text-gray-400 hover:text-red-500 mt-1"
      title="Remove item"
      aria-label="Remove item from cart"
      data-no-scanner-refocus
      @click="cart.removeItem(item.id)"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
      </svg>
    </button>
  </div>
</template>
