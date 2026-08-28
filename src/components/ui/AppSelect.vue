<script setup>
defineProps({
  modelValue: { default: '' },
  options:    { type: Array, default: () => [] },  // [{ value, label }] or strings
  label:      { type: String, default: '' },
  error:      { type: String, default: '' },
  placeholder:{ type: String, default: 'Select…' },
  required:   { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <div class="flex flex-col gap-1">
    <label v-if="label" class="label">
      {{ label }}<span v-if="required" class="text-red-500 ml-0.5">*</span>
    </label>
    <select
      :value="modelValue"
      :class="error ? 'input-error' : ''"
      class="input appearance-none pr-8 select-arrow"
      @change="emit('update:modelValue', $event.target.value)"
    >
      <option value="" disabled>{{ placeholder }}</option>
      <option
        v-for="opt in options"
        :key="typeof opt === 'object' ? opt.value : opt"
        :value="typeof opt === 'object' ? opt.value : opt"
      >
        {{ typeof opt === 'object' ? opt.label : opt }}
      </option>
    </select>
    <p v-if="error" class="text-xs text-red-600">{{ error }}</p>
  </div>
</template>
