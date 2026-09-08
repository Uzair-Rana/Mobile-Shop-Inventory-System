<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import SyncIndicator from './SyncIndicator.vue'

const auth   = useAuthStore()
const ui     = useUiStore()
const router = useRouter()

defineProps({ title: { type: String, default: '' } })

const userMenuOpen = ref(false)
const menuContainer = ref(null)

function toggleMenu() {
  userMenuOpen.value = !userMenuOpen.value
}

function closeMenu() {
  userMenuOpen.value = false
}

async function handleLogout() {
  closeMenu()
  await auth.logout()
  router.push('/')
}

const initials = computed(() =>
  auth.user?.first_name?.[0]?.toUpperCase() ||
  auth.user?.username?.[0]?.toUpperCase() || '?'
)

function handleOutsideClick(e) {
  if (menuContainer.value && !menuContainer.value.contains(e.target)) {
    userMenuOpen.value = false
  }
}

onMounted(() => document.addEventListener('mousedown', handleOutsideClick))
onUnmounted(() => document.removeEventListener('mousedown', handleOutsideClick))
</script>

<template>
  <header class="topbar flex items-center px-4 gap-3 shrink-0">

    <!-- Sidebar toggle -->
    <button
      class="toggle-btn"
      aria-label="Toggle sidebar"
      @click="ui.toggleSidebar()"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round"
          :d="ui.sidebarOpen
            ? 'M6 18L18 6M6 6l12 12'
            : 'M4 6h16M4 12h16M4 18h16'"
        />
      </svg>
    </button>

    <!-- Page title with breadcrumb style -->
    <div class="flex items-center gap-2 flex-1 min-w-0">
      <span class="text-gray-300 text-xs hidden sm:block font-semibold">My Phone</span>
      <span class="text-gray-400 text-xs hidden sm:block">/</span>
      <h1 class="topbar-title truncate">{{ title }}</h1>
    </div>

    <!-- Right cluster -->
    <div class="flex items-center gap-2 shrink-0">

      <!-- Sync indicator -->
      <SyncIndicator />

      <!-- Separator -->
      <div class="topbar-sep" />

      <!-- POS button — primary CTA -->
      <RouterLink to="/pos" class="pos-btn" title="Point of Sale">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
        </svg>
        <span>POS</span>
        <span class="pos-kbd">F9</span>
      </RouterLink>

      <!-- Separator -->
      <div class="topbar-sep" />

      <!-- User menu -->
      <div ref="menuContainer" class="user-menu-container relative">
        <button
          class="user-trigger"
          :class="{ 'active': userMenuOpen }"
          aria-label="User menu"
          @click="toggleMenu"
        >
          <div class="user-avatar-sm">{{ initials }}</div>
          <span class="hidden sm:block text-xs font-medium text-gray-600 max-w-[80px] truncate">
            {{ auth.user?.username }}
          </span>
          <svg
            class="w-3 h-3 text-gray-400 transition-transform duration-150"
            :class="{ 'rotate-180': userMenuOpen }"
            fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
          </svg>
        </button>

        <!-- Dropdown -->
        <Transition name="dropdown">
          <div v-if="userMenuOpen" class="user-dropdown" role="menu">
            <!-- Profile header -->
            <div class="user-dropdown-header">
              <div class="user-avatar-lg">{{ initials }}</div>
              <div class="min-w-0 flex-1">
                <p class="text-sm font-semibold text-gray-900 truncate">
                  {{ auth.user?.full_name || auth.user?.username }}
                </p>
                <p class="text-xs text-gray-400 truncate">{{ auth.user?.email || auth.user?.role_display }}</p>
              </div>
            </div>

            <div class="user-dropdown-role">
              <span class="badge badge-blue">{{ auth.user?.role_display || 'Staff' }}</span>
              <span class="text-[10px] text-gray-400">{{ auth.user?.username }}</span>
            </div>

            <div class="user-dropdown-sep" />

            <RouterLink
              to="/settings/company"
              class="user-dropdown-item"
              role="menuitem"
              @click="closeMenu"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065zM15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
              Settings
            </RouterLink>

            <RouterLink
              to="/reports"
              class="user-dropdown-item"
              role="menuitem"
              @click="closeMenu"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
              </svg>
              Reports
            </RouterLink>

            <div class="user-dropdown-sep" />

            <button
              class="user-dropdown-item text-red-600 hover:bg-red-50 w-full text-left"
              role="menuitem"
              @click="handleLogout"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
              </svg>
              Sign out
            </button>
          </div>
        </Transition>
      </div>
    </div>
  </header>
</template>

<style scoped>
.topbar {
  height: 52px;
  min-height: 52px;
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(226,232,240,0.8);
  box-shadow: 0 1px 0 rgba(0,0,0,0.04), 0 2px 8px rgba(0,0,0,0.04);
}

.toggle-btn {
  width: 32px; height: 32px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 8px;
  color: #64748b;
  border: none; background: none;
  cursor: pointer;
  transition: all 120ms;
  flex-shrink: 0;
}
.toggle-btn:hover { background: #f1f5f9; color: #0f172a; }

.topbar-title {
  font-size: 0.875rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.01em;
}

.topbar-sep {
  width: 1px; height: 20px;
  background: linear-gradient(180deg, transparent, #e2e8f0, transparent);
}

/* POS button — brand red */
.pos-btn {
  display: inline-flex; align-items: center; gap: .35rem;
  padding: .35rem .75rem; border-radius: 8px;
  background: linear-gradient(135deg, #e11d48, #be123c);
  color: white; font-size: .75rem; font-weight: 700;
  text-decoration: none; letter-spacing: .02em;
  transition: all 150ms;
  box-shadow: 0 2px 8px rgba(190,18,60,.35), inset 0 1px 0 rgba(255,255,255,.15);
}
.pos-btn:hover {
  background: linear-gradient(135deg, #be123c, #9f1239);
  transform: translateY(-1px);
  box-shadow: 0 4px 14px rgba(190,18,60,.45);
}
.pos-kbd {
  font-size: 0.55rem;
  background: rgba(255,255,255,0.2);
  padding: 0.05rem 0.3rem;
  border-radius: 3px;
  font-family: ui-monospace, monospace;
  font-weight: 600;
  letter-spacing: 0.05em;
}

/* User trigger */
.user-trigger {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.3rem 0.5rem;
  border-radius: 8px;
  border: 1px solid transparent;
  background: transparent;
  cursor: pointer;
  transition: all 120ms;
}
.user-trigger:hover, .user-trigger.active {
  background: #f1f5f9;
  border-color: #e2e8f0;
}

.user-avatar-sm {
  width: 26px; height: 26px; border-radius: 8px;
  background: linear-gradient(135deg, #e11d48, #9f1239);
  color: white; font-size: .6rem; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 1px 4px rgba(225,29,72,.35); flex-shrink: 0;
}

/* Dropdown */
.user-dropdown {
  position: absolute;
  right: 0;
  top: calc(100% + 6px);
  width: 220px;
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 10px 30px rgba(0,0,0,0.12), 0 4px 10px rgba(0,0,0,0.06);
  z-index: 100;
  overflow: hidden;
}
.user-dropdown-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem 0.625rem;
}
.user-avatar-lg {
  width: 36px; height: 36px; border-radius: 10px;
  background: linear-gradient(135deg, #e11d48, #9f1239);
  color: white; font-size: .75rem; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 2px 8px rgba(225,29,72,.35); flex-shrink: 0;
}
.user-dropdown-role {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1rem 0.625rem;
}
.user-dropdown-sep {
  height: 1px;
  background: #f1f5f9;
  margin: 0.25rem 0;
}
.user-dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.5rem 1rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #374151;
  text-decoration: none;
  transition: background 100ms;
  cursor: pointer;
  border: none;
  background: none;
  width: 100%;
}
.user-dropdown-item:hover { background: #f8fafc; }

/* Dropdown animation */
.dropdown-enter-active { animation: dropdown-in 150ms ease-out; }
.dropdown-leave-active { animation: dropdown-in 100ms ease-in reverse; }
@keyframes dropdown-in {
  from { opacity: 0; transform: translateY(-6px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}
</style>
