<script setup>
import { useAttrs } from 'vue'

const props = defineProps({
  modelValue: { default: '' },
  label:      { type: String, default: '' },
  error:      { type: String, default: '' },
  hint:       { type: String, default: '' },
  prefix:     { type: String, default: '' },
  suffix:     { type: String, default: '' },
  required:   { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue', 'blur', 'focus'])
const attrs = useAttrs()
</script>

<template>
  <div class="flex flex-col gap-0.5">
    <label v-if="label" class="label">
      {{ label }}<span v-if="required" class="text-red-500 ml-0.5" aria-hidden="true">*</span>
    </label>
    <div class="relative flex items-center">
      <span
        v-if="prefix"
        class="absolute left-2.5 text-xs text-gray-500 pointer-events-none select-none"
        aria-hidden="true"
      >{{ prefix }}</span>
      <input
        v-bind="attrs"
        :value="modelValue"
        :class="[error ? 'input-error' : '', prefix ? 'pl-7' : '', suffix ? 'pr-7' : '']"
        class="input"
        @input="emit('update:modelValue', $event.target.value)"
        @blur="emit('blur', $event)"
        @focus="emit('focus', $event)"
      />
      <span
        v-if="suffix"
        class="absolute right-2.5 text-xs text-gray-500 pointer-events-none select-none"
        aria-hidden="true"
      >{{ suffix }}</span>
    </div>
    <p v-if="error" class="text-[11px] text-red-600 leading-tight">{{ error }}</p>
    <p v-else-if="hint" class="text-[11px] text-gray-400 leading-tight">{{ hint }}</p>
  </div>
</template>
