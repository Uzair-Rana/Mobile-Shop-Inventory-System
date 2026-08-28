<script setup>
/**
 * AppPagination — compact row-count + page buttons.
 * Designed to sit flush below a table with no vertical breathing room wasted.
 */
defineProps({
  currentPage: { type: Number, required: true },
  totalPages:  { type: Number, required: true },
  totalCount:  { type: Number, default: 0 },
  pageSize:    { type: Number, default: 25 },
})
const emit = defineEmits(['page'])

function pages(current, total) {
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)
  const range = []
  for (let i = Math.max(2, current - 1); i <= Math.min(total - 1, current + 1); i++) range.push(i)
  if (current - 1 > 2) range.unshift('…')
  if (current + 1 < total - 1) range.push('…')
  return [1, ...range, total]
}
</script>

<template>
  <div class="flex items-center justify-between text-[11px] text-gray-500 py-1.5 px-1 border-t border-gray-100">
    <span class="tabular-nums">
      {{ ((currentPage - 1) * pageSize) + 1 }}–{{ Math.min(currentPage * pageSize, totalCount) }}
      of {{ totalCount.toLocaleString() }}
    </span>
    <div class="flex items-center gap-0.5">
      <button
        class="btn btn-ghost btn-xs"
        :disabled="currentPage === 1"
        aria-label="Previous page"
        @click="emit('page', currentPage - 1)"
      >‹</button>
      <button
        v-for="p in pages(currentPage, totalPages)"
        :key="p"
        :disabled="p === '…'"
        :class="p === currentPage ? 'bg-blue-600 text-white' : 'btn-ghost'"
        class="btn btn-xs min-w-[1.5rem] tabular-nums"
        @click="p !== '…' && emit('page', p)"
      >{{ p }}</button>
      <button
        class="btn btn-ghost btn-xs"
        :disabled="currentPage === totalPages"
        aria-label="Next page"
        @click="emit('page', currentPage + 1)"
      >›</button>
    </div>
  </div>
</template>
