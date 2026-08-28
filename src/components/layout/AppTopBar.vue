<script setup>
/**
 * AppTopBar — 40px tall, maximum information density.
 * Left: hamburger + breadcrumb title
 * Centre: nothing (keep scannable space clear)
 * Right: Sync indicator · POS shortcut · User
 */
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import SyncIndicator from './SyncIndicator.vue'

const auth   = useAuthStore()
const ui     = useUiStore()
const router = useRouter()

defineProps({ title: { type: String, default: '' } })

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}
</script>

<template>
  <header
    class="h-10 bg-white border-b border-gray-200 flex items-center px-3 gap-2 shrink-0"
    style="min-height:40px"
  >
    <!-- Sidebar toggle -->
    <button
      class="btn btn-ghost btn-sm p-1 -ml-0.5 text-gray-500"
      aria-label="Toggle sidebar"
      @click="ui.toggleSidebar()"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"/>
      </svg>
    </button>

    <!-- Breadcrumb / page title -->
    <h1 class="text-xs font-semibold text-gray-700 flex-1 truncate tracking-wide">{{ title }}</h1>

    <!-- Right cluster -->
    <div class="flex items-center gap-2 shrink-0">
      <!-- Always-visible sync status -->
      <SyncIndicator />

      <!-- Divider -->
      <span class="w-px h-4 bg-gray-200" aria-hidden="true" />

      <!-- POS shortcut — most-used action, prominent -->
      <RouterLink
        to="/pos"
        class="btn btn-primary btn-sm font-semibold tracking-wide"
        title="Open Point of Sale  [F9]"
      >
        <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
        </svg>
        POS
      </RouterLink>

      <!-- Divider -->
      <span class="w-px h-4 bg-gray-200" aria-hidden="true" />

      <!-- User menu -->
      <div class="relative group">
        <button
          class="flex items-center gap-1.5 text-xs text-gray-600 hover:text-gray-900 py-1 px-1.5 rounded hover:bg-gray-100"
          aria-label="User menu"
          aria-haspopup="true"
        >
          <span
            class="h-5 w-5 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-[10px] font-bold shrink-0"
            aria-hidden="true"
          >
            {{ auth.user?.first_name?.[0]?.toUpperCase() || auth.user?.username?.[0]?.toUpperCase() || '?' }}
          </span>
          <span class="hidden sm:block max-w-[6rem] truncate font-medium">{{ auth.user?.username }}</span>
          <svg class="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
          </svg>
        </button>

        <!-- Dropdown -->
        <div
          class="absolute right-0 top-full mt-0.5 hidden group-hover:block group-focus-within:block z-50 w-44 card py-1"
          style="box-shadow:0 4px 12px rgba(0,0,0,.12)"
          role="menu"
        >
          <div class="px-3 py-1.5 border-b border-gray-100">
            <p class="text-xs font-semibold text-gray-800">{{ auth.user?.full_name || auth.user?.username }}</p>
            <p class="text-[10px] text-gray-400">{{ auth.user?.role_display || 'Staff' }}</p>
          </div>
          <RouterLink
            to="/settings"
            class="flex items-center gap-2 px-3 py-1.5 text-xs text-gray-700 hover:bg-gray-50"
            role="menuitem"
          >Settings</RouterLink>
          <hr class="border-gray-100 my-0.5" />
          <button
            class="w-full text-left flex items-center gap-2 px-3 py-1.5 text-xs text-red-600 hover:bg-red-50"
            role="menuitem"
            @click="handleLogout"
          >Sign out</button>
        </div>
      </div>
    </div>
  </header>
</template>
