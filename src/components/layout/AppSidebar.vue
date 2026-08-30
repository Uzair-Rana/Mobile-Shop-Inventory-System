<script setup>
import { computed } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { PERMISSIONS } from '@/utils/constants'
import NavIcon from '@/components/ui/NavIcon.vue'

const auth  = useAuthStore()
const ui    = useUiStore()
const route = useRoute()

const nav = computed(() => [
  {
    items: [
      { name: 'Dashboard',     to: '/dashboard',             icon: 'home'     },
      { name: 'Point of Sale', to: '/pos',                   icon: 'pos',   accent: true },
    ],
  },
  {
    label: 'Inventory',
    items: [
      { name: 'Products',      to: '/inventory/products',    icon: 'box'    },
      { name: 'IMEI Units',    to: '/inventory/units',       icon: 'device' },
      { name: 'Accessories',   to: '/inventory/accessories', icon: 'plug'   },
    ],
  },
  {
    label: 'Sales',
    items: [
      { name: 'Invoices',      to: '/sales/invoices',        icon: 'receipt'  },
      { name: 'Installments',  to: '/installments',          icon: 'calendar' },
    ],
  },
  {
    label: 'Operations',
    items: [
      { name: 'Repairs',       to: '/repairs/jobs',          icon: 'wrench'   },
      { name: 'Purchases',     to: '/purchases/orders',      icon: 'truck'    },
      { name: 'Customers',     to: '/customers',             icon: 'users'    },
      { name: 'Suppliers',     to: '/suppliers',             icon: 'building' },
    ],
  },
  {
    label: 'Analytics',
    show: auth.hasPermission(PERMISSIONS.VIEW_REPORTS),
    items: [
      { name: 'Reports',       to: '/reports',               icon: 'chart'    },
    ],
  },
  {
    items: [
      { name: 'Cash',          to: '/cash',                  icon: 'cash'     },
      { name: 'Transfers',     to: '/transfers',             icon: 'transfer' },
      { name: 'Settings',      to: '/settings',              icon: 'cog'      },
    ],
  },
])

function isActive(to) {
  return route.path === to || (to !== '/dashboard' && route.path.startsWith(to))
}

const initials = computed(() =>
  auth.user?.first_name?.[0]?.toUpperCase() ||
  auth.user?.username?.[0]?.toUpperCase() || '?'
)
</script>

<template>
  <aside
    :class="ui.sidebarOpen ? 'w-[240px]' : 'w-[56px]'"
    class="sidebar flex flex-col shrink-0 h-full overflow-hidden transition-[width] duration-200 ease-out"
  >
    <!-- ── Brand ─────────────────────────────────────────────────────────── -->
    <div class="brand-bar flex items-center gap-3 px-3 shrink-0" style="height:52px">
      <div class="brand-logo shrink-0">
        <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="28" height="28" rx="7" fill="url(#brand-grad)"/>
          <path d="M7 14.5l4.5 4.5L21 9" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
          <defs>
            <linearGradient id="brand-grad" x1="0" y1="0" x2="28" y2="28" gradientUnits="userSpaceOnUse">
              <stop stop-color="#3b82f6"/>
              <stop offset="1" stop-color="#6366f1"/>
            </linearGradient>
          </defs>
        </svg>
      </div>
      <Transition name="fade-slide">
        <div v-if="ui.sidebarOpen" class="min-w-0">
          <p class="text-[13px] text-white tracking-tight leading-none font-extrabold">DEVNEST</p>
          <p class="text-[9px] text-blue-400 font-semibold tracking-widest uppercase mt-0.5">Mobile ERP</p>
        </div>
      </Transition>
    </div>

    <!-- ── Nav ───────────────────────────────────────────────────────────── -->
    <nav class="flex-1 overflow-y-auto overflow-x-hidden py-2 px-2" aria-label="Main navigation">
      <template v-for="section in nav" :key="section.label || 'root'">
        <template v-if="section.show !== false">

          <!-- Section label -->
          <Transition name="fade-slide">
            <p v-if="ui.sidebarOpen && section.label" class="nav-section-label">
              {{ section.label }}
            </p>
          </Transition>
          <div v-if="!ui.sidebarOpen && section.label" class="nav-divider" />

          <!-- Nav items -->
          <RouterLink
            v-for="item in section.items"
            :key="item.to"
            :to="item.to"
            :title="!ui.sidebarOpen ? item.name : undefined"
            :class="[
              isActive(item.to)
                ? item.accent ? 'nav-item-pos-active' : 'nav-item-active'
                : item.accent ? 'nav-item-pos' : 'nav-item',
            ]"
          >
            <span class="nav-icon-wrap">
              <NavIcon :icon="item.icon" class="w-[15px] h-[15px]" />
            </span>
            <Transition name="fade-slide">
              <span v-if="ui.sidebarOpen" class="nav-label">{{ item.name }}</span>
            </Transition>
          </RouterLink>

        </template>
      </template>
    </nav>

    <!-- ── User strip ────────────────────────────────────────────────────── -->
    <div class="user-strip mx-2 mb-2 rounded-lg shrink-0">
      <div class="flex items-center gap-2.5 px-2.5 py-2">
        <div class="user-avatar shrink-0">{{ initials }}</div>
        <Transition name="fade-slide">
          <div v-if="ui.sidebarOpen" class="flex-1 min-w-0">
            <p class="text-[11px] font-semibold text-white truncate leading-tight" style="opacity:0.9">
              {{ auth.user?.full_name || auth.user?.username }}
            </p>
            <p class="text-[9px] text-white truncate mt-0.5 uppercase tracking-wide" style="opacity:0.4">
              {{ auth.user?.role_display || 'Staff' }}
            </p>
          </div>
        </Transition>
        <Transition name="fade-slide">
          <div v-if="ui.sidebarOpen" class="online-dot shrink-0" />
        </Transition>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  background: #0d1117;
  background-image: radial-gradient(ellipse at 50% 0%, rgba(59,130,246,0.08) 0%, transparent 60%);
  border-right: 1px solid rgba(255,255,255,0.05);
}

.brand-bar { border-bottom: 1px solid rgba(255,255,255,0.05); }
.brand-logo { filter: drop-shadow(0 0 8px rgba(59,130,246,0.4)); }

.nav-section-label {
  padding: 0.75rem 0.5rem 0.25rem;
  font-size: 0.55rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: rgba(255,255,255,0.2);
  user-select: none;
}
.nav-divider {
  margin: 0.4rem 0.5rem;
  height: 1px;
  background: rgba(255,255,255,0.05);
}

.nav-item, .nav-item-pos, .nav-item-active, .nav-item-pos-active {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0 0.5rem;
  height: 34px;
  border-radius: 8px;
  text-decoration: none;
  transition: all 150ms ease;
  margin-bottom: 1px;
}

.nav-item { color: rgba(255,255,255,0.45); }
.nav-item:hover { background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.85); }

.nav-item-active {
  background: rgba(59,130,246,0.14);
  color: #93c5fd;
  box-shadow: inset 0 0 0 1px rgba(59,130,246,0.2);
}

.nav-item-pos { color: #60a5fa; }
.nav-item-pos:hover { background: rgba(59,130,246,0.1); color: #93c5fd; }

.nav-item-pos-active {
  background: linear-gradient(135deg, rgba(59,130,246,0.25), rgba(99,102,241,0.2));
  color: white;
  box-shadow: inset 0 0 0 1px rgba(99,102,241,0.3);
}

.nav-icon-wrap {
  width: 20px; height: 20px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

.nav-label {
  font-size: 0.8125rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1;
}

.user-strip {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.06);
}
.user-avatar {
  width: 26px; height: 26px;
  border-radius: 8px;
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  display: flex; align-items: center; justify-content: center;
  font-size: 0.625rem; font-weight: 800; color: white;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(59,130,246,0.35);
}
.online-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: #22c55e;
  flex-shrink: 0;
}

.fade-slide-enter-active { transition: all 120ms ease-out; }
.fade-slide-leave-active { transition: all 80ms ease-in; }
.fade-slide-enter-from { opacity: 0; transform: translateX(-6px); }
.fade-slide-leave-to   { opacity: 0; transform: translateX(-4px); }
</style>
