<script setup>
/**
 * AppTabs — horizontal tab bar.
 * tabs: [{ key, label }]
 * v-model: active tab key
 */
defineProps({
  tabs:       { type: Array,  required: true }, // [{ key, label, badge? }]
  modelValue: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue'])
</script>

<script>
export default { inheritAttrs: false }
</script>

<template>
  <div class="border-b border-gray-200 flex gap-0.5 overflow-x-auto" v-bind="$attrs">
    <button
      v-for="tab in tabs"
      :key="tab.key"
      type="button"
      :class="[
        'px-3 py-2 text-xs font-semibold whitespace-nowrap transition-colors shrink-0',
        modelValue === tab.key
          ? 'border-b-2 border-blue-600 text-blue-700 -mb-px bg-white'
          : 'text-gray-500 hover:text-gray-800 hover:bg-gray-50 border-b-2 border-transparent -mb-px',
      ]"
      :aria-selected="modelValue === tab.key"
      role="tab"
      @click="$emit('update:modelValue', tab.key)"
    >
      {{ tab.label }}
      <span v-if="tab.badge" class="ml-1.5 badge badge-gray text-[10px] px-1">{{ tab.badge }}</span>
    </button>
  </div>
</template>
