<script setup>
/**
 * AppKanban — HTML5 drag-and-drop kanban board.
 * columns: [{ key, label, badge?, items[] }]
 * Emits: ('move', { itemId, fromCol, toCol })
 */
defineProps({
  columns: { type: Array, required: true },
})
const emit = defineEmits(['move'])

let dragItem = null
let dragFromCol = null

function onDragStart(item, colKey) {
  dragItem = item
  dragFromCol = colKey
}

function onDragOver(e) {
  e.preventDefault()
}

function onDrop(e, toColKey) {
  e.preventDefault()
  if (!dragItem || dragFromCol === toColKey) return
  emit('move', { itemId: dragItem.id, fromCol: dragFromCol, toCol: toColKey })
  dragItem = null
  dragFromCol = null
}
</script>

<template>
  <div class="flex gap-2 overflow-x-auto pb-2 h-full" style="min-height:0">
    <div
      v-for="col in columns"
      :key="col.key"
      class="flex flex-col shrink-0 w-52"
    >
      <!-- Column header -->
      <div class="flex items-center justify-between px-2 py-1.5 bg-gray-100 border border-gray-200 rounded-t text-xs font-semibold text-gray-700 mb-1 sticky top-0 z-10">
        <span>{{ col.label }}</span>
        <span class="badge badge-gray text-[10px]">{{ col.items?.length || 0 }}</span>
      </div>

      <!-- Drop zone -->
      <div
        class="flex-1 flex flex-col gap-1.5 p-1 rounded-b border border-t-0 border-gray-200 bg-gray-50 overflow-y-auto"
        style="min-height:120px"
        @dragover="onDragOver"
        @drop="onDrop($event, col.key)"
      >
        <div
          v-for="item in col.items"
          :key="item.id"
          class="cursor-grab active:cursor-grabbing"
          draggable="true"
          @dragstart="onDragStart(item, col.key)"
        >
          <slot :item="item" :col="col.key">
            <!-- Default card if no slot provided -->
            <div class="card p-2 text-xs hover:shadow-sm transition-shadow">
              <p class="font-medium text-gray-800 truncate">{{ item.job_number || item.id }}</p>
            </div>
          </slot>
        </div>
        <div v-if="!col.items?.length" class="text-center text-[10px] text-gray-400 py-4 select-none">
          Drop here
        </div>
      </div>
    </div>
  </div>
</template>
