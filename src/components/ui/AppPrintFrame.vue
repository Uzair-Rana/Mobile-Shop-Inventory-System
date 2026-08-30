<script setup>
/**
 * AppPrintFrame — hidden print container.
 * Usage: <AppPrintFrame ref="printRef"><receipt /></AppPrintFrame>
 * Then call printRef.print('80mm') or printRef.print('A4')
 */
import { ref } from 'vue'

const frameRef = ref(null)

function print(layout = '80mm') {
  if (!frameRef.value) return
  const el = frameRef.value
  el.dataset.layout = layout
  window.print()
}

defineExpose({ print })
</script>

<template>
  <div ref="frameRef" id="print-target">
    <slot />
  </div>
</template>
