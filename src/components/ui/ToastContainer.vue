<script setup>
/**
 * Toasts — bottom-right, compact, never obscure content.
 * Appear in ~100ms, auto-dismiss. No decorative drop shadows, just border + bg.
 */
import { useUiStore } from '@/stores/ui'
const ui = useUiStore()

const styles = {
  success: { bar: 'bg-green-500',  bg: 'bg-white border-l-2 border-green-500', icon: 'text-green-600', path: 'M5 13l4 4L19 7' },
  error:   { bar: 'bg-red-500',    bg: 'bg-white border-l-2 border-red-500',   icon: 'text-red-600',   path: 'M6 18L18 6M6 6l12 12' },
  warning: { bar: 'bg-amber-400',  bg: 'bg-white border-l-2 border-amber-400', icon: 'text-amber-600', path: 'M12 9v4m0 4h.01' },
  info:    { bar: 'bg-blue-500',   bg: 'bg-white border-l-2 border-blue-500',  icon: 'text-blue-600',  path: 'M13 16h-1v-4h-1m1-4h.01' },
}
</script>

<template>
  <Teleport to="body">
    <div
      aria-live="polite"
      aria-atomic="false"
      class="fixed bottom-3 right-3 z-[100] flex flex-col gap-1.5 w-72 pointer-events-none"
    >
      <TransitionGroup
        enter-active-class="transition duration-100 ease-out"
        enter-from-class="opacity-0 translate-x-2"
        enter-to-class="opacity-100 translate-x-0"
        leave-active-class="transition duration-75 ease-in absolute w-full"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-for="toast in ui.toasts"
          :key="toast.id"
          :class="styles[toast.type]?.bg ?? 'bg-white border-l-2 border-gray-300'"
          class="pointer-events-auto flex items-start gap-2.5 px-3 py-2 border border-gray-200 rounded"
          style="box-shadow:0 2px 8px rgba(0,0,0,.1)"
          role="alert"
        >
          <svg
            class="w-3.5 h-3.5 mt-0.5 shrink-0"
            :class="styles[toast.type]?.icon"
            fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path stroke-linecap="round" stroke-linejoin="round" :d="styles[toast.type]?.path" />
          </svg>
          <p class="text-xs text-gray-800 flex-1 leading-snug">{{ toast.message }}</p>
          <button
            class="text-gray-400 hover:text-gray-600 mt-0.5 shrink-0"
            aria-label="Dismiss"
            @click="ui.dismissToast(toast.id)"
          >
            <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>
