<script setup>
/**
 * SyncIndicator — always visible in the top bar, never buried.
 * Compact by default: shows dot + text label in a tight pill.
 * Expands slightly on error to show error message on hover/focus.
 */
import { useSyncStore } from '@/stores/sync'
const sync = useSyncStore()
</script>

<template>
  <div
    class="flex items-center gap-1 text-[11px] font-semibold px-1.5 py-0.5 rounded tabular-nums select-none"
    :class="{
      'text-green-700 bg-green-50':  sync.status.value === 'online',
      'text-red-700   bg-red-50':    sync.status.value === 'offline' || sync.status.value === 'error',
      'text-blue-700  bg-blue-50':   sync.status.value === 'syncing',
      'text-amber-700 bg-amber-50':  sync.status.value === 'pending',
    }"
    :title="sync.hasError ? sync.errorMessage : sync.status.label"
    role="status"
    :aria-label="`Network: ${sync.status.label}`"
  >
    <span
      class="h-1.5 w-1.5 rounded-full shrink-0"
      :class="{
        'bg-green-500':                   sync.status.value === 'online',
        'bg-red-500':                     sync.status.value === 'offline' || sync.status.value === 'error',
        'bg-blue-500 animate-pulse':      sync.status.value === 'syncing',
        'bg-amber-500 animate-pulse':     sync.status.value === 'pending',
      }"
      aria-hidden="true"
    />
    {{ sync.status.label }}
    <span v-if="sync.pendingRequests > 1" class="opacity-60">({{ sync.pendingRequests }})</span>
  </div>
</template>
