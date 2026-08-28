<script setup>
/**
 * AppBadge — always text + indicator dot, never just a colored dot.
 * Square-ish corners (badge class), dense padding.
 *
 * Pass either:
 *  :status="REPAIR_STATUS.IN_PROGRESS"   (from constants.js)
 *  :label="'Custom label'" :variant="'badge-blue'"
 */
defineProps({
  status:  { type: Object, default: null },
  label:   { type: String, default: '' },
  variant: { type: String, default: '' },
})
</script>

<template>
  <span
    :class="status?.badge || variant || 'badge-gray'"
    class="badge"
  >
    <span
      class="h-1.5 w-1.5 rounded-full bg-current opacity-60 shrink-0"
      aria-hidden="true"
    />
    {{ label || status?.label || '—' }}
  </span>
</template>
