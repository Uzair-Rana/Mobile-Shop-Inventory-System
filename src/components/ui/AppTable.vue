<script setup>
/**
 * AppTable — sticky-header, sortable data table shell.
 * Dense by default: uses .table-base from main.css (13px, 5px cell padding).
 */
defineProps({
  columns:      { type: Array, required: true },
  loading:      { type: Boolean, default: false },
  emptyMessage: { type: String, default: 'No records found' },
  sortKey:      { type: String, default: '' },
  sortDir:      { type: String, default: 'asc' },
})
const emit = defineEmits(['sort'])
</script>

<template>
  <div class="card overflow-hidden">
    <div class="overflow-x-auto">
      <table class="table-base">
        <thead>
          <tr>
            <th
              v-for="col in columns"
              :key="col.key"
              :class="[
                col.align === 'right'  ? 'text-right'  : '',
                col.align === 'center' ? 'text-center' : '',
                col.sortable ? 'cursor-pointer select-none hover:text-gray-800' : '',
              ]"
              @click="col.sortable && emit('sort', col.key)"
            >
              <span class="inline-flex items-center gap-1">
                {{ col.label }}
                <template v-if="col.sortable">
                  <svg v-if="sortKey === col.key" class="w-2.5 h-2.5" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                    <path v-if="sortDir === 'asc'"  d="M10 4l6 6H4z"/>
                    <path v-else                    d="M10 16l-6-6h12z"/>
                  </svg>
                  <svg v-else class="w-2.5 h-2.5 opacity-25" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                    <path d="M10 4l6 6H4zM10 16l-6-6h12z"/>
                  </svg>
                </template>
              </span>
            </th>
          </tr>
        </thead>
        <tbody>
          <!-- Loading: tight skeleton rows -->
          <template v-if="loading">
            <tr v-for="n in 6" :key="n">
              <td v-for="col in columns" :key="col.key">
                <div class="h-3 rounded bg-gray-100 animate-pulse" :style="`width:${40 + (n * 13) % 50}%`" />
              </td>
            </tr>
          </template>
          <!-- Rows -->
          <template v-else-if="$slots.default">
            <slot />
          </template>
          <!-- Empty -->
          <tr v-else>
            <td :colspan="columns.length" class="py-8 text-center text-xs text-gray-400">
              {{ emptyMessage }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
