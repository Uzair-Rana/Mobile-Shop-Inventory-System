<script setup>
import { RouterView, RouterLink, useRoute } from 'vue-router'
import { usePermissions } from '@/composables/usePermissions'
const route = useRoute()
const perms = usePermissions()

const tabs = [
  { to: '/settings/company', label: 'Company'  },
  { to: '/settings/tax',     label: 'Tax'      },
  { to: '/settings/users',   label: 'Users',   requiresPermission: true },
  { to: '/settings/roles',   label: 'Roles',   requiresPermission: true },
]
</script>
<template>
  <div class="space-y-4">
    <h2 class="text-lg font-semibold text-gray-900">Settings</h2>
    <div class="flex items-center gap-1 border-b border-gray-200 -mb-4">
      <template v-for="tab in tabs" :key="tab.to">
        <RouterLink
          v-if="!tab.requiresPermission || perms.canManageUsers.value"
          :to="tab.to"
          :class="route.path.startsWith(tab.to) ? 'border-blue-600 text-blue-700 font-semibold' : 'border-transparent text-gray-500 hover:text-gray-700'"
          class="px-4 py-2 text-sm border-b-2 transition-colors"
        >{{ tab.label }}</RouterLink>
      </template>
    </div>
    <RouterView />
  </div>
</template>
