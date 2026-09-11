<script setup>
import { RouterView, RouterLink, useRoute } from 'vue-router'
import { usePermissions } from '@/composables/usePermissions'
const route = useRoute()
const perms = usePermissions()

const tabs = [
  { to: '/settings/company', label: 'Company', icon: '🏢' },
  { to: '/settings/tax',     label: 'Tax',     icon: '📊' },
  { to: '/settings/users',   label: 'Users',   icon: '👥', requiresPermission: true },
  { to: '/settings/roles',   label: 'Roles',   icon: '🔐', requiresPermission: true },
]
</script>
<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="border-b border-gray-200 pb-4">
      <h1 class="text-2xl font-bold text-gray-900">Settings</h1>
      <p class="text-sm text-gray-500 mt-1">Manage your application settings and configurations</p>
    </div>

    <!-- Tabs Navigation -->
    <div class="flex items-center gap-8 border-b-2 border-gray-200 overflow-x-auto">
      <template v-for="tab in tabs" :key="tab.to">
        <RouterLink
          v-if="!tab.requiresPermission || perms.canManageUsers.value"
          :to="tab.to"
          :class="[
            'tab-link',
            route.path.startsWith(tab.to) && 'tab-link-active'
          ]"
        >
          <span class="tab-icon">{{ tab.icon }}</span>
          <span>{{ tab.label }}</span>
        </RouterLink>
      </template>
    </div>

    <!-- Tab Content -->
    <div class="pt-2">
      <RouterView />
    </div>
  </div>
</template>

<style scoped>
.tab-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 0;
  padding-bottom: 0.625rem;
  margin-bottom: -2px;
  font-size: 0.95rem;
  font-weight: 500;
  color: #6b7280;
  text-decoration: none;
  border-bottom: 2px solid transparent;
  transition: all 200ms ease;
  white-space: nowrap;
  position: relative;
}

.tab-link:hover {
  color: #111827;
  border-bottom-color: #d1d5db;
}

.tab-link-active {
  color: #2563eb;
  border-bottom-color: #2563eb;
  font-weight: 600;
}

.tab-icon {
  font-size: 1.1rem;
  display: inline-flex;
}

@media (max-width: 768px) {
  .tab-link {
    padding: 0.5rem 0;
    font-size: 0.875rem;
  }

  .tab-icon {
    font-size: 1rem;
  }
}
</style>
