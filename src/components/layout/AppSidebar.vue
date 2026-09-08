<script setup>
import { computed } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import NavIcon from '@/components/ui/NavIcon.vue'
import logoImg from '@/assets/logo of My Phone.png'

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
      { name: 'IMEI Devices',  to: '/inventory/devices',     icon: 'device' },
      { name: 'Accessories',   to: '/inventory/accessories', icon: 'plug'   },
      { name: 'Labels',        to: '/inventory/labels',      icon: 'tag'    },
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
      { name: 'Repairs',       to: '/repairs/board',         icon: 'wrench'   },
      { name: 'Purchases',     to: '/purchases/orders',      icon: 'truck'    },
      { name: 'Transfers',     to: '/transfers',             icon: 'transfer' },
      { name: 'Customers',     to: '/customers',             icon: 'users'    },
      { name: 'Suppliers',     to: '/suppliers',             icon: 'building' },
    ],
  },
  {
    label: 'Finance',
    items: [
      { name: 'Cash',          to: '/cash',                  icon: 'cash'     },
      { name: 'Expenses',      to: '/cash/expenses',         icon: 'expense'  },
    ],
  },
  {
    label: 'Analytics',
    show: auth.hasPermission('view_reports'),
    items: [
      { name: 'Reports',       to: '/reports',               icon: 'chart'    },
    ],
  },
  {
    items: [
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
    <div class="brand-bar flex items-center gap-2.5 px-3 shrink-0" style="height:52px">
      <!-- Logo image -->
      <div class="brand-logo shrink-0">
        <img
          :src="logoImg"
          alt="My Phone logo"
          class="brand-logo-img"
          :class="ui.sidebarOpen ? 'w-8 h-8' : 'w-7 h-7'"
        />
      </div>
      <Transition name="fade-slide">
        <div v-if="ui.sidebarOpen" class="min-w-0">
          <p class="text-[14px] text-white tracking-tight leading-none font-extrabold">My Phone</p>
          <p class="text-[9px] font-semibold tracking-widest uppercase mt-0.5" style="color:#fb7185">Mobile ERP</p>
        </div>
      </Transition>
    </div>

    <!-- ── Nav ───────────────────────────────────────────────────────────── -->
    <nav class="flex-1 overflow-y-auto overflow-x-hidden py-2 px-2" aria-label="Main navigation">
      <template v-for="section in nav" :key="section.label || 'root'">
        <template v-if="section.show !== false">
          <Transition name="fade-slide">
            <p v-if="ui.sidebarOpen && section.label" class="nav-section-label">
              {{ section.label }}
            </p>
          </Transition>
          <div v-if="!ui.sidebarOpen && section.label" class="nav-divider" />

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
            <p class="text-[11px] font-semibold text-white truncate leading-tight" style="opacity:.9">
              {{ auth.user?.full_name || auth.user?.username }}
            </p>
            <p class="text-[9px] text-white truncate mt-0.5 uppercase tracking-wide" style="opacity:.4">
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
  background: #0d0f14;
  background-image: radial-gradient(ellipse at 50% 0%, rgba(225,29,72,.07) 0%, transparent 60%);
  border-right: 1px solid rgba(255,255,255,.05);
}

.brand-bar { border-bottom: 1px solid rgba(255,255,255,.06); }

.brand-logo-img {
  object-fit: contain;
  border-radius: 8px;
  background: rgba(255,255,255,.08);
  padding: 3px;
  filter: drop-shadow(0 0 8px rgba(225,29,72,.35));
  transition: all 200ms;
}

.nav-section-label {
  padding: .75rem .5rem .25rem;
  font-size: .55rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: .1em; color: rgba(255,255,255,.2); user-select: none;
}
.nav-divider { margin: .4rem .5rem; height: 1px; background: rgba(255,255,255,.05); }

.nav-item, .nav-item-pos, .nav-item-active, .nav-item-pos-active {
  display: flex; align-items: center; gap: .625rem;
  padding: 0 .5rem; height: 34px; border-radius: 8px;
  text-decoration: none; transition: all 150ms ease; margin-bottom: 1px;
}

.nav-item { color: rgba(255,255,255,.42); }
.nav-item:hover { background: rgba(255,255,255,.05); color: rgba(255,255,255,.85); }

/* Active — red brand */
.nav-item-active {
  background: rgba(225,29,72,.14);
  color: #fda4af;
  box-shadow: inset 0 0 0 1px rgba(225,29,72,.22);
}

/* POS accent */
.nav-item-pos { color: #fb7185; }
.nav-item-pos:hover { background: rgba(225,29,72,.1); color: #fda4af; }
.nav-item-pos-active {
  background: linear-gradient(135deg, rgba(225,29,72,.25), rgba(190,18,60,.2));
  color: white;
  box-shadow: inset 0 0 0 1px rgba(225,29,72,.3);
}

.nav-icon-wrap { width:20px; height:20px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.nav-label { font-size:.8125rem; font-weight:500; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; line-height:1; }

.user-strip { background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.06); }
.user-avatar {
  width:26px; height:26px; border-radius:8px;
  background: linear-gradient(135deg, #e11d48, #9f1239);
  display:flex; align-items:center; justify-content:center;
  font-size:.625rem; font-weight:800; color:white; flex-shrink:0;
  box-shadow: 0 2px 6px rgba(225,29,72,.4);
}
.online-dot { width:6px; height:6px; border-radius:50%; background:#22c55e; flex-shrink:0; }

.fade-slide-enter-active { transition:all 120ms ease-out; }
.fade-slide-leave-active { transition:all 80ms ease-in; }
.fade-slide-enter-from { opacity:0; transform:translateX(-6px); }
.fade-slide-leave-to   { opacity:0; transform:translateX(-4px); }
</style>
