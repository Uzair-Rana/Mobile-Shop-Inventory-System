<script setup>
import { onMounted, onUnmounted } from 'vue'

const props = defineProps({
  open:  { type: Boolean, required: true },
  title: { type: String, default: '' },
  size:  { type: String, default: 'md' }, // sm | md | lg | xl | full
})
const emit = defineEmits(['close'])

const sizeMap = {
  sm:   'max-w-sm',
  md:   'max-w-lg',
  lg:   'max-w-2xl',
  xl:   'max-w-4xl',
  full: 'max-w-7xl',
}

function handleKey(e) {
  if (e.key === 'Escape' && props.open) emit('close')
}
onMounted(()  => document.addEventListener('keydown', handleKey))
onUnmounted(() => document.removeEventListener('keydown', handleKey))
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-100 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-75 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="open"
        class="fixed inset-0 z-50 flex items-start justify-center pt-16 px-4 pb-4"
        style="background:rgba(0,0,0,0.45)"
        @click.self="emit('close')"
        role="dialog"
        :aria-modal="true"
        :aria-label="title"
      >
        <Transition
          enter-active-class="transition duration-100 ease-out"
          enter-from-class="opacity-0 -translate-y-2"
          enter-to-class="opacity-100 translate-y-0"
        >
          <div
            v-if="open"
            :class="sizeMap[size]"
            class="card w-full flex flex-col max-h-[80vh]"
            style="box-shadow:0 8px 32px rgba(0,0,0,.18)"
          >
            <!-- Header — tight, no decorative padding -->
            <div
              v-if="title || $slots.header"
              class="flex items-center justify-between px-4 py-2.5 border-b border-gray-200 bg-gray-50 shrink-0"
            >
              <slot name="header">
                <h2 class="text-sm font-semibold text-gray-900">{{ title }}</h2>
              </slot>
              <button
                class="btn btn-ghost btn-xs p-0.5 -mr-0.5 text-gray-400 hover:text-gray-600"
                aria-label="Close"
                @click="emit('close')"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>

            <!-- Body -->
            <div class="flex-1 overflow-y-auto px-4 py-3">
              <slot />
            </div>

            <!-- Footer -->
            <div
              v-if="$slots.footer"
              class="shrink-0 border-t border-gray-200 px-4 py-2.5 flex justify-end gap-2 bg-gray-50"
            >
              <slot name="footer" />
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>
