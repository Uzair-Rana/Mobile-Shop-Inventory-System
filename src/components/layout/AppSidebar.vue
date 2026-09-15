<script setup>
import { computed, ref } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import NavIcon from '@/components/ui/NavIcon.vue'
import { TABS, tabMatchPrefixes } from '@/config/sections'
import logoImg from '@/assets/logo of My Phone.png'

const auth  = useAuthStore()
const ui    = useUiStore()
const route = useRoute()

// Major tabs — each opens its section hub (which shows options in the body).
const tabs = computed(() => TABS)

function isActive(tab) {
  if (tab.to === '/dashboard') return route.path === '/dashboard'
  return tabMatchPrefixes(tab).some(p => route.path.startsWith(p))
}

const initials = computed(() =>
  auth.user?.first_name?.[0]?.toUpperCase() ||
  auth.user?.username?.[0]?.toUpperCase() || 'A'
)
</script>

<template>
  <aside
    :class="ui.sidebarOpen ? 'sidebar-open' : 'sidebar-closed'"
    class="sidebar flex flex-col shrink-0 h-full overflow-hidden transition-[width] duration-250 ease-out"
  >
    <!-- ── Brand bar ──────────────────────────────────────────────────── -->
    <div class="brand-bar flex items-center gap-3 px-4 shrink-0">
      <div class="brand-logo-wrap shrink-0">
        <img
          :src="logoImg"
          alt="My Phone"
          class="brand-logo-img"
          :class="ui.sidebarOpen ? 'logo-lg' : 'logo-sm'"
        />
      </div>
      <Transition name="fade-slide">
        <div v-if="ui.sidebarOpen" class="min-w-0 overflow-hidden">
          <p class="brand-name">My Phone</p>
          <p class="brand-sub">Mobile Shop ERP</p>
        </div>
      </Transition>
    </div>

    <!-- ── Major tabs ────────────────────────────────────────────────── -->
    <nav class="flex-1 overflow-y-auto overflow-x-hidden py-3 px-3 space-y-1" aria-label="Main navigation">
      <RouterLink
        v-for="tab in tabs"
        :key="tab.to"
        :to="tab.to"
        :title="!ui.sidebarOpen ? tab.label : undefined"
        :class="[
          isActive(tab)
            ? (tab.accent ? 'link-pos-active' : 'link-active')
            : (tab.accent ? 'link-pos'        : 'link'),
        ]"
      >
        <span class="link-icon">
          <NavIcon :icon="tab.icon" class="w-[18px] h-[18px]" />
        </span>
        <Transition name="fade-slide">
          <span v-if="ui.sidebarOpen" class="link-label">{{ tab.label }}</span>
        </Transition>
      </RouterLink>
    </nav>

    <!-- ── User strip ─────────────────────────────────────────────────── -->
    <div class="user-strip mx-3 mb-3 shrink-0 rounded-xl">
      <div class="flex items-center gap-3 px-3 py-2.5">
        <div class="user-avatar shrink-0">{{ initials }}</div>
        <Transition name="fade-slide">
          <div v-if="ui.sidebarOpen" class="flex-1 min-w-0">
            <p class="user-name truncate">{{ auth.user?.full_name || auth.user?.username }}</p>
            <p class="user-role truncate">{{ auth.user?.role_display || 'Administrator' }}</p>
          </div>
        </Transition>
        <Transition name="fade-slide">
          <span v-if="ui.sidebarOpen" class="online-dot shrink-0" />
        </Transition>
      </div>
    </div>
  </aside>
</template>

<style scoped>
/* ── Sidebar shell ───────────────────────────────────────────────────────── */
.sidebar {
  background: #0c0e13;
  background-image: radial-gradient(ellipse at 50% 0%, rgba(225,29,72,.09) 0%, transparent 55%);
  border-right: 1px solid rgba(255,255,255,.06);
}
.sidebar-open   { width: 264px; }
.sidebar-closed { width: 64px;  }

/* ── Brand bar ───────────────────────────────────────────────────────────── */
.brand-bar {
  height: 64px;
  min-height: 64px;
  border-bottom: 1px solid rgba(255,255,255,.07);
}
.brand-logo-wrap { flex-shrink: 0; }
.brand-logo-img  {
  object-fit: contain;
  border-radius: 10px;
  background: rgba(255,255,255,.07);
  padding: 4px;
  filter: drop-shadow(0 0 10px rgba(225,29,72,.4));
  transition: all 200ms;
}
.logo-lg { width: 40px; height: 40px; }
.logo-sm { width: 36px; height: 36px; }

.brand-name {
  font-size: 1rem;
  font-weight: 900;
  color: #ffffff;
  letter-spacing: -0.025em;
  line-height: 1;
  white-space: nowrap;
}
.brand-sub {
  font-size: .6875rem;
  font-weight: 600;
  color: #fb7185;
  letter-spacing: .12em;
  text-transform: uppercase;
  margin-top: 3px;
  white-space: nowrap;
}

/* ── Section label ───────────────────────────────────────────────────────── */
.nav-section {
  padding: .9rem .75rem .3rem;
  font-size: .6875rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: .1em;
  color: rgba(255,255,255,.22);
  user-select: none;
  white-space: nowrap;
}
.nav-rule { margin: .5rem .75rem; height: 1px; background: rgba(255,255,255,.07); }

/* ── Nav links ───────────────────────────────────────────────────────────── */
.link, .link-pos, .link-active, .link-pos-active {
  display: flex;
  align-items: center;
  gap: .75rem;
  padding: 0 .75rem;
  height: 40px;
  border-radius: 10px;
  text-decoration: none;
  transition: all 130ms ease;
  margin-bottom: 2px;
}

.link { color: rgba(255,255,255,.44); }
.link:hover {
  background: rgba(255,255,255,.06);
  color: rgba(255,255,255,.88);
}

.link-active {
  background: rgba(225,29,72,.16);
  color: #fda4af;
  box-shadow: inset 0 0 0 1px rgba(225,29,72,.25);
}

.link-pos { color: #fb7185; }
.link-pos:hover {
  background: rgba(225,29,72,.12);
  color: #fda4af;
}

.link-pos-active {
  background: linear-gradient(135deg, rgba(225,29,72,.28), rgba(190,18,60,.22));
  color: #fff;
  box-shadow: inset 0 0 0 1px rgba(225,29,72,.35);
}

.link-icon {
  width: 22px; height: 22px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

.link-label {
  font-size: .9375rem;       /* 14px — clearly readable */
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1;
}

/* ── User strip ──────────────────────────────────────────────────────────── */
.user-strip {
  background: rgba(255,255,255,.05);
  border: 1px solid rgba(255,255,255,.08);
}
.user-avatar {
  width: 32px; height: 32px;
  border-radius: 10px;
  background: linear-gradient(135deg, #e11d48, #9f1239);
  display: flex; align-items: center; justify-content: center;
  font-size: .75rem; font-weight: 800; color: #fff;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(225,29,72,.45);
}
.user-name {
  font-size: .9rem;
  font-weight: 600;
  color: rgba(255,255,255,.9);
  line-height: 1.2;
}
.user-role {
  font-size: .75rem;
  color: rgba(255,255,255,.38);
  text-transform: uppercase;
  letter-spacing: .06em;
  margin-top: 2px;
}
.online-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 6px #22c55e;
}

/* ── Transitions ─────────────────────────────────────────────────────────── */
.fade-slide-enter-active { transition: all 130ms ease-out; }
.fade-slide-leave-active { transition: all 90ms  ease-in; }
.fade-slide-enter-from   { opacity: 0; transform: translateX(-8px); }
.fade-slide-leave-to     { opacity: 0; transform: translateX(-4px); }
</style>
