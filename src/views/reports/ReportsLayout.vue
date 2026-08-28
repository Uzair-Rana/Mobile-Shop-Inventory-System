<script setup>
import { RouterView, RouterLink, useRoute } from 'vue-router'
const route = useRoute()
const tabs = [
  { to: '/reports/sales',         label: 'Sales' },
  { to: '/reports/profit',        label: 'Profit & Loss' },
  { to: '/reports/inventory',     label: 'Inventory' },
  { to: '/reports/repairs',       label: 'Repairs' },
  { to: '/reports/installments',  label: 'Installments' },
]
</script>
<template>
  <div class="space-y-4">
    <div class="flex items-center gap-1 border-b border-gray-200 -mb-4">
      <RouterLink
        v-for="tab in tabs"
        :key="tab.to"
        :to="tab.to"
        :class="route.path.startsWith(tab.to) ? 'border-blue-600 text-blue-700 font-semibold' : 'border-transparent text-gray-500 hover:text-gray-700'"
        class="px-4 py-2 text-sm border-b-2 transition-colors"
      >{{ tab.label }}</RouterLink>
    </div>
    <RouterView />
  </div>
</template>
