<script setup>
defineProps({
  variant:  { type: String, default: 'primary' }, // primary | secondary | danger | ghost
  size:     { type: String, default: 'md' },       // sm | md | lg
  loading:  { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  type:     { type: String, default: 'button' },
})

const variantMap = {
  primary:   'btn-primary',
  secondary: 'btn-secondary',
  danger:    'btn-danger',
  ghost:     'btn-ghost',
}
const sizeMap = {
  sm: 'btn-sm',
  md: '',
  lg: 'btn-lg',
}
</script>

<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="[variantMap[variant], sizeMap[size]]"
    class="btn"
  >
    <!-- Spinner -->
    <svg v-if="loading" class="animate-spin h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
    </svg>
    <slot />
  </button>
</template>
