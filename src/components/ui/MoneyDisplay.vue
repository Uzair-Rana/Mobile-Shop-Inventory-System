<script setup>
/**
 * MoneyDisplay — always renders with fixed decimal, no raw float artifacts.
 * Pass mask=true to show "••••" when the current user lacks cost/profit visibility.
 */
import { computed } from 'vue'
import { formatMoney } from '@/utils/money'

const props = defineProps({
  value:    { default: null },
  symbol:   { type: Boolean, default: true },
  mask:     { type: Boolean, default: false },
  maskText: { type: String, default: '••••' },
  class:    { type: String, default: '' },
})

const display = computed(() =>
  props.mask ? props.maskText : formatMoney(props.value, { symbol: props.symbol })
)
</script>

<template>
  <span class="money" :class="props.class" :aria-hidden="mask" :title="mask ? 'Hidden — insufficient permissions' : undefined">
    {{ display }}
  </span>
</template>
