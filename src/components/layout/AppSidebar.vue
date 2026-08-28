<script setup>
/**
 * AppSidebar — compact, keyboard-navigable nav.
 *
 * Collapsed (icon-only) = 44px wide, a sliver — barely takes space.
 * Expanded = 188px — tight but readable.
 * No section labels when collapsed.
 * Alert badges on nav items (low stock, overdue, etc.) come from the ui store.
 */
import { computed, h } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { PERMISSIONS } from '@/utils/constants'

const auth  = useAuthStore()
const ui    = useUiStore()
const route = useRoute()

const nav = computed(() => [
  {
    items: [
      { name: 'Dashboard',     to: '/dashboard',           icon: 'home'     },
      { name: 'Point of Sale', to: '/pos',                 icon: 'pos',  accent: true },
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
      { name: 'Settings',      to: '/settings',              icon: 'cog'      },
    ],
  },
])

function isActive(to) {
  return route.path === to || (to !== '/dashboard' && route.path.startsWith(to))
}
</script>

<template>
  <aside
    :style="ui.sidebarOpen ? 'width:188px' : 'width:44px'"
    class="bg-gray-950 text-gray-400 flex flex-col shrink-0 h-full overflow-hidden transition-[width] duration-150"
  >
    <!-- Brand mark -->
    <div
      class="flex items-center gap-2 px-2.5 border-b border-gray-800 shrink-0"
      style="height:40px"  /* matches top bar height exactly */
    >
      <div
        class="h-6 w-6 rounded bg-blue-600 flex items-center justify-center shrink-0 font-bold text-white"
        style="font-size:10px;letter-spacing:.05em"
        aria-label="DEVNEST"
      >DN</div>
      <Transition name="fade">
        <span v-if="ui.sidebarOpen" class="text-xs font-bold text-white tracking-widest whitespace-nowrap">
          DEVNEST
        </span>
      </Transition>
    </div>

    <!-- Nav -->
    <nav class="flex-1 overflow-y-auto overflow-x-hidden py-1" aria-label="Main navigation">
      <template v-for="section in nav" :key="section.label || 'main'">
        <!-- Skip hidden sections -->
        <template v-if="section.show !== false">
          <!-- Section label (only when expanded) -->
          <Transition name="fade">
            <p
              v-if="ui.sidebarOpen && section.label"
              class="px-2.5 pt-3 pb-0.5 text-[9px] font-bold uppercase tracking-widest text-gray-600 select-none"
            >{{ section.label }}</p>
          </Transition>
          <div v-if="!ui.sidebarOpen && section.label" class="mx-2.5 my-1 border-t border-gray-800" />

          <ul class="space-y-px px-1.5 py-0.5">
            <li v-for="item in section.items" :key="item.to">
              <RouterLink
                :to="item.to"
                :title="item.name"
                :class="[
                  isActive(item.to)
                    ? item.accent
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-800 text-white'
                    : item.accent
                      ? 'text-blue-400 hover:bg-blue-600/20 hover:text-blue-300'
                      : 'hover:bg-gray-800 hover:text-gray-100',
                ]"
                class="flex items-center gap-2 px-2 rounded transition-colors"
                style="height:28px;min-width:0"
              >
                <NavIcon
                  :icon="item.icon"
                  class="w-3.5 h-3.5 shrink-0"
                  :class="isActive(item.to) ? 'opacity-100' : 'opacity-70'"
                />
                <Transition name="fade">
                  <span
                    v-if="ui.sidebarOpen"
                    class="text-xs font-medium whitespace-nowrap overflow-hidden text-ellipsis"
                  >{{ item.name }}</span>
                </Transition>
              </RouterLink>
            </li>
          </ul>
        </template>
      </template>
    </nav>

    <!-- User strip -->
    <div
      class="border-t border-gray-800 flex items-center gap-2 px-2.5 shrink-0 overflow-hidden"
      style="height:36px"
    >
      <div
        class="h-5 w-5 rounded-full bg-gray-700 flex items-center justify-center text-[10px] font-bold shrink-0 text-gray-200"
        aria-hidden="true"
      >{{ auth.user?.first_name?.[0]?.toUpperCase() || auth.user?.username?.[0]?.toUpperCase() || '?' }}</div>
      <Transition name="fade">
        <div v-if="ui.sidebarOpen" class="flex-1 min-w-0">
          <p class="text-[11px] font-semibold text-gray-200 truncate leading-none">
            {{ auth.user?.full_name || auth.user?.username }}
          </p>
          <p class="text-[9px] text-gray-500 truncate mt-0.5">{{ auth.user?.role_display || 'Staff' }}</p>
        </div>
      </Transition>
    </div>
  </aside>
</template>

<!-- ── Inline icon renderer ──────────────────────────────────────────────────── -->
<script>
const ICON_PATHS = {
  home:     ['M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6'],
  pos:      ['M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z'],
  box:      ['M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4'],
  device:   ['M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z'],
  plug:     ['M13 10V3L4 14h7v7l9-11h-7z'],   /* lightning bolt — more recognisable for accessories */
  receipt:  ['M9 14l6-6m-5.5.5h.01m4.99 5h.01M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16l3.5-2 3.5 2 3.5-2 3.5 2z'],
  calendar: ['M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z'],
  wrench:   ['M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z', 'M15 12a3 3 0 11-6 0 3 3 0 016 0z'],
  truck:    ['M9 17a2 2 0 11-4 0 2 2 0 014 0zM19 17a2 2 0 11-4 0 2 2 0 014 0zM13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10h10zm0 0h6l2-4V10h-8v6z'],
  users:    ['M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z'],
  building: ['M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4'],
  chart:    ['M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z'],
  cog:      ['M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z', 'M15 12a3 3 0 11-6 0 3 3 0 016 0z'],
}

export default {
  name: 'NavIcon',
  props: { icon: String },
  setup(props, { attrs }) {
    return () => h('svg', {
      xmlns: 'http://www.w3.org/2000/svg',
      fill: 'none',
      stroke: 'currentColor',
      'stroke-width': '1.75',
      'stroke-linecap': 'round',
      'stroke-linejoin': 'round',
      viewBox: '0 0 24 24',
      class: attrs.class,
      'aria-hidden': 'true',
    }, (ICON_PATHS[props.icon] || ICON_PATHS.box).map(d =>
      h('path', { d })
    ))
  },
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.1s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
