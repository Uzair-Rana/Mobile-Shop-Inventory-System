<script setup>
import { computed } from 'vue'
import { formatMoney } from '@/utils/money'
import { useCartStore } from '@/stores/cart'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'

const cart = useCartStore()

const change = computed(() =>
  Math.max(0, (cart.amountReceived || 0) - cart.grandTotal)
)
</script>

<template>
  <div class="space-y-2 text-sm">
    <!-- Subtotal -->
    <div class="flex justify-between text-gray-600">
      <span>Subtotal ({{ cart.itemCount }} item{{ cart.itemCount !== 1 ? 's' : '' }})</span>
      <MoneyDisplay :value="cart.subtotal" />
    </div>

    <!-- Discount -->
    <div v-if="cart.invoiceDiscount > 0" class="flex justify-between text-green-700">
      <span>Invoice Discount</span>
      <span class="money">− {{ formatMoney(cart.invoiceDiscount) }}</span>
    </div>

    <!-- Tax -->
    <div v-if="cart.taxRate > 0" class="flex justify-between text-gray-600">
      <span>Tax ({{ cart.taxRate }}%)</span>
      <MoneyDisplay :value="cart.taxAmount" />
    </div>

    <hr class="border-gray-200" />

    <!-- Grand total -->
    <div class="flex justify-between font-bold text-base text-gray-900">
      <span>Total</span>
      <MoneyDisplay :value="cart.grandTotal" class="text-blue-700" />
    </div>

    <!-- Amount received + change -->
    <div class="pt-1 space-y-1.5">
      <div class="flex items-center gap-2">
        <label class="text-gray-600 whitespace-nowrap">Received</label>
        <input
          v-model.number="cart.amountReceived"
          type="number"
          min="0"
          step="100"
          class="input text-right money"
          placeholder="0.00"
          data-no-scanner-refocus
        />
      </div>
      <div
        v-if="cart.amountReceived > 0"
        class="flex justify-between font-semibold"
        :class="change >= 0 ? 'text-green-700' : 'text-red-600'"
      >
        <span>{{ change >= 0 ? 'Change' : 'Balance Due' }}</span>
        <MoneyDisplay :value="Math.abs(change)" />
      </div>
    </div>
  </div>
</template>
