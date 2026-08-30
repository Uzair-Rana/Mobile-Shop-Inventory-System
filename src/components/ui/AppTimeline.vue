<script setup>
/**
 * AppTimeline — vertical event list.
 * events: [{ type, timestamp, actor, title, detail?, highlight?, cost? }]
 */
import { formatDateTime } from '@/utils/date'
import PermGate from './PermGate.vue'

defineProps({
  events: { type: Array, default: () => [] },
})

const typeColors = {
  acquisition:  { dot: 'bg-blue-500',  icon: '↓' },
  sale:         { dot: 'bg-green-500', icon: '✓' },
  inspection:   { dot: 'bg-yellow-400',icon: '🔍' },
  price_change: { dot: 'bg-orange-400',icon: '₨' },
  repair:       { dot: 'bg-red-400',   icon: '⚙' },
  transfer:     { dot: 'bg-purple-400',icon: '→' },
  status:       { dot: 'bg-gray-400',  icon: '·' },
  cost:         { dot: 'bg-orange-500',icon: '₨' },
  default:      { dot: 'bg-gray-400',  icon: '·' },
}

function getStyle(type) {
  return typeColors[type] || typeColors.default
}
</script>

<template>
  <div class="space-y-0">
    <div v-if="events.length === 0" class="text-sm text-gray-400 py-4 text-center">No events recorded</div>
    <div
      v-for="(evt, i) in events"
      :key="evt.id || i"
      class="flex gap-3 pb-3"
    >
      <!-- Timeline line + dot -->
      <div class="flex flex-col items-center shrink-0" style="width:1.25rem">
        <div :class="['h-3 w-3 rounded-full shrink-0 mt-1', getStyle(evt.type).dot]" />
        <div v-if="i < events.length - 1" class="flex-1 w-px bg-gray-200 my-1" />
      </div>

      <!-- Content -->
      <div class="flex-1 min-w-0 pb-1">
        <div class="flex items-start justify-between gap-2">
          <p class="text-xs font-semibold text-gray-800 leading-snug">{{ evt.title }}</p>
          <span class="text-[10px] text-gray-400 whitespace-nowrap shrink-0">{{ formatDateTime(evt.timestamp) }}</span>
        </div>
        <p v-if="evt.detail" class="text-xs text-gray-500 mt-0.5 leading-snug">{{ evt.detail }}</p>
        <!-- Cost events behind PermGate -->
        <template v-if="evt.type === 'cost' || evt.type === 'price_change'">
          <PermGate perm="view_cost">
            <p v-if="evt.cost_detail" class="text-xs text-orange-600 font-medium mt-0.5">{{ evt.cost_detail }}</p>
          </PermGate>
        </template>
        <p class="text-[10px] text-gray-400 mt-0.5">by {{ evt.actor }}</p>
      </div>
    </div>
  </div>
</template>
