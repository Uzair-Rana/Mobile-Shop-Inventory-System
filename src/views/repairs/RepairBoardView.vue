<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useRepairBoardStore } from '@/stores/repairBoard'
import { formatDate } from '@/utils/date'
import AppKanban from '@/components/ui/AppKanban.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'

const board  = useRepairBoardStore()
const router = useRouter()

function handleMove({ itemId, fromCol, toCol }) {
  board.moveJob(itemId, fromCol, toCol)
}

function daysOpen(createdAt) {
  if (!createdAt) return 0
  return Math.floor((Date.now() - new Date(createdAt).getTime()) / (1000 * 60 * 60 * 24))
}
</script>

<template>
  <div class="flex flex-col h-full overflow-hidden space-y-2">
    <div class="flex items-center justify-between flex-shrink-0">
      <h2 class="text-lg font-bold text-gray-900">Repair Board</h2>
      <div class="flex gap-2">
        <AppButton variant="secondary" size="sm" @click="router.push('/repairs/jobs')">List View</AppButton>
        <AppButton variant="primary" size="sm" @click="router.push('/repairs/jobs/new')">+ New Job</AppButton>
      </div>
    </div>

    <div class="flex-1 overflow-hidden">
      <AppKanban :columns="board.columnList" @move="handleMove">
        <template #default="{ item }">
          <div
            class="card p-2 space-y-1 hover:shadow-sm transition-shadow cursor-pointer text-xs"
            @click="router.push(`/repairs/jobs/${item.id}`)"
          >
            <div class="flex items-center justify-between">
              <span class="font-semibold text-blue-700">#{{ item.job_number }}</span>
              <span
                class="text-[10px] font-medium px-1 rounded"
                :class="daysOpen(item.created_at) > 7 ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-500'"
              >
                {{ daysOpen(item.created_at) }}d
              </span>
            </div>
            <p class="font-medium text-gray-800 truncate">{{ item.device_model }}</p>
            <p class="text-gray-500 truncate">{{ item.customer_name }}</p>
          </div>
        </template>
      </AppKanban>
    </div>
  </div>
</template>
