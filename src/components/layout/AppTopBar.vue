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

const userMenuOpen  = ref(false)
const menuContainer = ref(null)

function toggleMenu()  { userMenuOpen.value = !userMenuOpen.value }
function closeMenu()   { userMenuOpen.value = false }

async function handleLogout() {
  closeMenu()
  await auth.logout()
}

const initials = computed(() =>
  auth.user?.first_name?.[0]?.toUpperCase() ||
  auth.user?.username?.[0]?.toUpperCase() || 'A'
)

function handleOutsideClick(e) {
  if (menuContainer.value && !menuContainer.value.contains(e.target)) {
    userMenuOpen.value = false
  }
}
onMounted(()  => document.addEventListener('mousedown', handleOutsideClick))
onUnmounted(() => document.removeEventListener('mousedown', handleOutsideClick))
</script>

<template>
  <header class="topbar shrink-0 flex items-center px-5 gap-3">

    <!-- Sidebar toggle -->
    <button class="toggle-btn" aria-label="Toggle sidebar" @click="ui.toggleSidebar()">
      <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round"
          :d="ui.sidebarOpen ? 'M6 18L18 6M6 6l12 12' : 'M4 6h16M4 12h16M4 18h16'"
        />
      </svg>
    </button>

    <!-- Breadcrumb + title -->
    <div class="flex items-center gap-2 flex-1 min-w-0">
      <span class="topbar-brand hidden md:block">My Phone</span>
      <svg class="w-3.5 h-3.5 text-gray-300 hidden md:block" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
      </svg>
      <h1 class="topbar-title truncate">{{ title }}</h1>
    </div>

    <!-- Right actions -->
    <div class="flex items-center gap-2.5 shrink-0">

      <SyncIndicator />
      <div class="sep" />

      <!-- POS quick-launch -->
      <RouterLink to="/pos" class="pos-btn">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
        </svg>
        <span class="hidden sm:inline">Point of Sale</span>
        <span class="pos-kbd">F9</span>
      </RouterLink>

      <div class="sep" />

      <!-- User dropdown -->
      <div ref="menuContainer" class="relative">
        <button class="user-btn" :class="{ active: userMenuOpen }" @click="toggleMenu">
          <div class="avatar">{{ initials }}</div>
          <div class="hidden sm:block text-left min-w-0">
            <p class="user-btn-name truncate">{{ auth.user?.full_name || auth.user?.username }}</p>
            <p class="user-btn-role truncate">{{ auth.user?.role_display || 'Admin' }}</p>
          </div>
          <svg class="w-4 h-4 text-gray-400 shrink-0 transition-transform duration-150"
               :class="{ 'rotate-180': userMenuOpen }"
               fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
          </svg>
        </button>

        <Transition name="dropdown">
          <div v-if="userMenuOpen" class="dropdown" role="menu">
            <!-- Header -->
            <div class="dp-header">
              <div class="dp-avatar">{{ initials }}</div>
              <div class="min-w-0">
                <p class="dp-name truncate">{{ auth.user?.full_name || auth.user?.username }}</p>
                <p class="dp-sub  truncate">{{ auth.user?.email || auth.user?.role_display }}</p>
              </div>
            </div>
            <div class="dp-rule" />

            <RouterLink to="/settings/company" class="dp-item" @click="closeMenu">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065zM15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
              Settings
            </RouterLink>

            <RouterLink to="/reports" class="dp-item" @click="closeMenu">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
              </svg>
              Reports
            </RouterLink>

            <div class="dp-rule" />

            <button class="dp-item dp-danger w-full text-left" @click="handleLogout">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
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
/* ── Top bar ──────────────────────────────────────────────────────────────── */
.topbar {
  height: 64px;
  min-height: 64px;
  background: rgba(255,255,255,.95);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid #e9ecef;
  box-shadow: 0 1px 0 rgba(0,0,0,.04), 0 2px 10px rgba(0,0,0,.05);
  position: relative;
  z-index: 100;
}

/* Toggle */
.toggle-btn {
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 10px; color: #6b7280;
  border: none; background: none; cursor: pointer; transition: all 120ms;
  flex-shrink: 0;
}
.toggle-btn:hover { background: #f3f4f6; color: #111827; }

/* Title */
.topbar-brand {
  font-size: .875rem;
  font-weight: 700;
  color: #9ca3af;
  letter-spacing: .01em;
}
.topbar-title {
  font-size: 1.0625rem;      /* 16px — was 14px */
  font-weight: 700;
  color: #111827;
  letter-spacing: -.02em;
}

/* Separator */
.sep { width: 1px; height: 24px; background: #e5e7eb; }

/* POS button */
.pos-btn {
  display: inline-flex; align-items: center; gap: .4rem;
  padding: .45rem 1rem; border-radius: 10px;
  background: linear-gradient(135deg, #e11d48, #be123c);
  color: #fff; font-size: .875rem; font-weight: 700;
  text-decoration: none; letter-spacing: .01em;
  transition: all 140ms;
  box-shadow: 0 2px 10px rgba(190,18,60,.3), inset 0 1px 0 rgba(255,255,255,.14);
}
.pos-btn:hover {
  background: linear-gradient(135deg, #be123c, #9f1239);
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(190,18,60,.38);
}
.pos-kbd {
  font-size: .6875rem; background: rgba(255,255,255,.18);
  padding: .1rem .35rem; border-radius: 4px;
  font-family: ui-monospace, monospace; font-weight: 700;
}

/* User button */
.user-btn {
  display: flex; align-items: center; gap: .625rem;
  padding: .4rem .75rem;
  border-radius: 10px; border: 1px solid transparent;
  background: transparent; cursor: pointer; transition: all 120ms;
  max-width: 200px;
  position: relative;
}
.user-btn:hover, .user-btn.active {
  background: #f3f4f6; border-color: #e5e7eb;
}
.avatar {
  width: 32px; height: 32px; border-radius: 10px;
  background: linear-gradient(135deg, #e11d48, #9f1239);
  color: #fff; font-size: .8125rem; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 2px 6px rgba(225,29,72,.35); flex-shrink: 0;
}
.user-btn-name {
  font-size: .9rem; font-weight: 600; color: #111827;
  line-height: 1.2; max-width: 100px;
}
.user-btn-role {
  font-size: .75rem; color: #9ca3af; line-height: 1.2; max-width: 100px;
}

/* Dropdown */
.dropdown {
  position: absolute; right: 0; top: calc(100% + 8px);
  width: 240px; background: #fff;
  border-radius: 14px; border: 1px solid #e5e7eb;
  box-shadow: 0 12px 32px rgba(0,0,0,.14), 0 4px 12px rgba(0,0,0,.07);
  z-index: 9999; overflow: hidden;
}
.dp-header {
  display: flex; align-items: center; gap: .875rem;
  padding: 1rem 1.125rem .75rem;
}
.dp-avatar {
  width: 40px; height: 40px; border-radius: 11px;
  background: linear-gradient(135deg, #e11d48, #9f1239);
  color: #fff; font-size: .875rem; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 2px 10px rgba(225,29,72,.35); flex-shrink: 0;
}
.dp-name { font-size: .9375rem; font-weight: 700; color: #111827; line-height: 1.2; }
.dp-sub  { font-size: .8125rem; color: #9ca3af; margin-top: 2px; }
.dp-rule { height: 1px; background: #f3f4f6; margin: .25rem 0; }
.dp-item {
  display: flex; align-items: center; gap: .625rem;
  padding: .625rem 1.125rem;
  font-size: .9375rem; font-weight: 500; color: #374151;
  text-decoration: none; transition: background 100ms;
  cursor: pointer; border: none; background: none; width: 100%;
}
.dp-item:hover  { background: #f9fafb; }
.dp-danger      { color: #dc2626; }
.dp-danger:hover { background: #fff1f2; }

/* Dropdown animation */
.dropdown-enter-active { animation: dp-in 150ms ease-out; }
.dropdown-leave-active { animation: dp-in 100ms ease-in reverse; }
@keyframes dp-in {
  from { opacity:0; transform:translateY(-8px) scale(.97); }
  to   { opacity:1; transform:translateY(0)   scale(1);   }
}
</style>
