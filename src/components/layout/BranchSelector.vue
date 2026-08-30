<script setup>
/**
 * BranchSelector — dropdown in top bar to switch active branch.
 */
import { useBranchStore } from '@/stores/branch'

const branch = useBranchStore()
</script>

<template>
  <div class="relative group">
    <button
      class="flex items-center gap-1 text-xs text-gray-600 hover:text-gray-900 px-2 py-1 rounded hover:bg-gray-100 whitespace-nowrap"
      title="Switch branch"
    >
      <svg class="w-3 h-3 text-gray-400 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
      </svg>
      <span class="max-w-[7rem] truncate font-medium">{{ branch.activeBranch?.name || 'Branch' }}</span>
      <svg class="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
      </svg>
    </button>

    <div
      class="absolute left-0 top-full mt-0.5 hidden group-hover:block group-focus-within:block z-50 w-48 card py-1"
      style="box-shadow:0 4px 12px rgba(0,0,0,.12)"
    >
      <p class="px-3 py-1 text-[10px] font-bold text-gray-400 uppercase tracking-wider">Select Branch</p>
      <button
        v-for="b in branch.branchList"
        :key="b.id"
        class="w-full text-left px-3 py-1.5 text-xs hover:bg-gray-50 flex items-center justify-between"
        :class="branch.activeBranchId === b.id ? 'text-blue-700 font-semibold' : 'text-gray-700'"
        @click="branch.switchBranch(b.id)"
      >
        <span>{{ b.name }}</span>
        <span v-if="branch.activeBranchId === b.id" class="text-blue-500 text-[10px]">✓</span>
      </button>
    </div>
  </div>
</template>
