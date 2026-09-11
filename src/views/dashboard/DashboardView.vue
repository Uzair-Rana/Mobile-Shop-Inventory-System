<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { usePermissions } from '@/composables/usePermissions'
import { salesApi } from '@/api/sales'
import { inventoryApi } from '@/api/inventory'
import { repairsApi } from '@/api/repairs'
import { installmentsApi } from '@/api/installments'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import { INVOICE_STATUS, REPAIR_STATUS } from '@/utils/constants'

const auth  = useAuthStore()
const perms = usePermissions()

const loading        = ref(true)
const summary        = ref(null)
const lowStock       = ref([])
const recentInvoices = ref([])
const pendingRepairs = ref([])
const overdueInstall = ref([])

const today      = new Date().toISOString().slice(0, 10)
const todayLabel = new Date().toLocaleDateString('en-PK', {
  weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
})
const greeting   = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return 'Good morning'
  if (h < 17) return 'Good afternoon'
  return 'Good evening'
})

onMounted(async () => {
  try {
    const [sumRes, stockRes, invRes, repairRes, installRes] = await Promise.allSettled([
      salesApi.getDailySummary(today),
      inventoryApi.listLowStock({ page_size: 6 }),
      salesApi.listInvoices({ ordering: '-created_at', page_size: 8 }),
      repairsApi.listJobs({ page_size: 8 }),
      installmentsApi.listOverdue({ page_size: 8 }),
    ])
    if (sumRes.status     === 'fulfilled') summary.value        = sumRes.value.data
    if (stockRes.status   === 'fulfilled') lowStock.value       = stockRes.value.data?.results  ?? stockRes.value.data
    if (invRes.status     === 'fulfilled') recentInvoices.value = invRes.value.data?.results    ?? invRes.value.data
    if (repairRes.status  === 'fulfilled') pendingRepairs.value = repairRes.value.data?.results ?? repairRes.value.data
    if (installRes.status === 'fulfilled') overdueInstall.value = installRes.value.data?.results ?? installRes.value.data
  } finally {
    loading.value = false
  }
})

const cashVariance = computed(() => {
  if (!summary.value) return null
  return (summary.value.cash_received || 0) - (summary.value.expected_cash || 0)
})

const exceptions = computed(() => {
  const list = []
  overdueInstall.value.forEach(p => list.push({
    severity: 'urgent', icon: 'calendar',
    label:    `Overdue installment — ${p.customer_name} (${p.plan_number})`,
    meta:     `PKR ${Number(p.balance_remaining || 0).toLocaleString()}`,
    link:     `/installments/${p.id}`,
  }))
  pendingRepairs.value.filter(r => r.status === 'ready').forEach(r => list.push({
    severity: 'warn', icon: 'wrench',
    label:    `Ready for pickup — ${r.customer_name} · ${r.device_model}`,
    meta:     `#${r.job_number}`,
    link:     `/repairs/jobs/${r.id}`,
  }))
  lowStock.value.forEach(item => list.push({
    severity: 'warn', icon: 'box',
    label:    `Low stock — ${item.name}`,
    meta:     `${item.stock_qty} remaining`,
    link:     `/inventory/accessories`,
  }))
  return list
})

function invStatus(val) {
  return Object.values(INVOICE_STATUS || {}).find(s => s.value === val) || { label: val, badge: 'badge-gray' }
}
function repairStatus(val) {
  return Object.values(REPAIR_STATUS || {}).find(s => s.value === val) || { label: val, badge: 'badge-gray' }
}
</script>

<template>
  <div class="dashboard">

    <!-- ── Page header ────────────────────────────────────────────────────── -->
    <div class="dash-header">
      <div>
        <h1 class="dash-greeting">
          {{ greeting }},
          <span class="gradient-brand">{{ auth.user?.first_name || auth.user?.username }}</span> 👋
        </h1>
        <p class="dash-date">{{ todayLabel }}</p>
      </div>
      <RouterLink to="/pos" class="btn btn-primary btn-lg gap-2">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
        </svg>
        Open POS
      </RouterLink>
    </div>

    <!-- ── KPI Strip ──────────────────────────────────────────────────────── -->
    <div class="kpi-grid">

      <!-- Today's Sales -->
      <div class="kpi kpi-brand">
        <div class="kpi-icon kpi-icon-brand">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 14l6-6m-5.5.5h.01m4.99 5h.01M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16l3.5-2 3.5 2 3.5-2 3.5 2z"/>
          </svg>
        </div>
        <div class="kpi-body">
          <p class="kpi-label">Today's Sales</p>
          <div v-if="loading" class="skeleton h-8 w-36 mt-1 mb-1" />
          <MoneyDisplay v-else :value="summary?.total_sales" class="kpi-value" />
          <p class="kpi-sub">{{ summary?.invoice_count ?? 0 }} invoices today</p>
        </div>
        <div class="kpi-accent" />
      </div>

      <!-- Cash Collected -->
      <div class="kpi kpi-green">
        <div class="kpi-icon kpi-icon-green">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"/>
          </svg>
        </div>
        <div class="kpi-body">
          <p class="kpi-label">Cash Collected</p>
          <div v-if="loading" class="skeleton h-8 w-36 mt-1 mb-1" />
          <MoneyDisplay v-else :value="summary?.cash_received" class="kpi-value text-green-700" />
          <p class="kpi-sub">received today</p>
        </div>
        <div class="kpi-accent kpi-accent-green" />
      </div>

      <!-- Gross Profit -->
      <div v-if="perms.canViewProfit.value" class="kpi kpi-purple">
        <div class="kpi-icon kpi-icon-purple">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
          </svg>
        </div>
        <div class="kpi-body">
          <p class="kpi-label">Gross Profit</p>
          <div v-if="loading" class="skeleton h-8 w-36 mt-1 mb-1" />
          <MoneyDisplay v-else :value="summary?.gross_profit" class="kpi-value text-violet-700" />
          <p v-if="summary?.gross_margin != null" class="kpi-sub">{{ summary.gross_margin?.toFixed(1) }}% margin</p>
        </div>
        <div class="kpi-accent kpi-accent-purple" />
      </div>

      <!-- Cash Variance -->
      <div class="kpi" :class="cashVariance != null && cashVariance < 0 ? 'kpi-red' : ''">
        <div class="kpi-icon" :class="cashVariance != null && cashVariance < 0 ? 'kpi-icon-red' : 'kpi-icon-gray'">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3"/>
          </svg>
        </div>
        <div class="kpi-body">
          <p class="kpi-label">Cash Variance</p>
          <div v-if="loading" class="skeleton h-8 w-24 mt-1 mb-1" />
          <MoneyDisplay
            v-else :value="cashVariance"
            class="kpi-value"
            :class="cashVariance == null ? '' : cashVariance < 0 ? 'text-red-600' : 'text-green-700'"
          />
          <p class="kpi-sub">vs expected</p>
        </div>
      </div>

      <!-- Open Repairs -->
      <div class="kpi kpi-orange">
        <div class="kpi-icon kpi-icon-orange">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065zM15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
        </div>
        <div class="kpi-body">
          <p class="kpi-label">Open Repairs</p>
          <div v-if="loading" class="skeleton h-8 w-16 mt-1 mb-1" />
          <p v-else class="kpi-value text-orange-600">{{ summary?.open_repairs ?? pendingRepairs.length }}</p>
          <p class="kpi-sub">{{ summary?.repairs_ready ?? 0 }} ready for pickup</p>
        </div>
        <div class="kpi-accent kpi-accent-orange" />
      </div>

      <!-- Overdue Plans -->
      <div class="kpi" :class="overdueInstall.length > 0 ? 'kpi-red' : ''">
        <div class="kpi-icon" :class="overdueInstall.length > 0 ? 'kpi-icon-red' : 'kpi-icon-gray'">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
          </svg>
        </div>
        <div class="kpi-body">
          <p class="kpi-label">Overdue Plans</p>
          <div v-if="loading" class="skeleton h-8 w-16 mt-1 mb-1" />
          <p v-else class="kpi-value" :class="overdueInstall.length > 0 ? 'text-red-600' : ''">
            {{ summary?.overdue_plans ?? overdueInstall.length }}
          </p>
          <p class="kpi-sub">installment plans</p>
        </div>
      </div>

    </div>

    <!-- ── Exceptions ─────────────────────────────────────────────────────── -->
    <div v-if="!loading && exceptions.length > 0" class="exceptions-card">
      <div class="exceptions-hd">
        <div class="flex items-center gap-2.5">
          <span class="alert-dot" />
          <span class="exceptions-title">Needs Attention</span>
          <span class="badge badge-red">{{ exceptions.length }}</span>
        </div>
        <span class="exceptions-meta">{{ exceptions.length }} item{{ exceptions.length !== 1 ? 's' : '' }} require action</span>
      </div>
      <div>
        <RouterLink
          v-for="(ex, i) in exceptions"
          :key="i"
          :to="ex.link || '#'"
          :class="ex.severity === 'urgent' ? 'exception-row-urgent' : 'exception-row-warn'"
        >
          <div class="w-1.5 self-stretch rounded-full shrink-0"
               :class="ex.severity === 'urgent' ? 'bg-red-500' : 'bg-amber-400'" />
          <svg class="w-4 h-4 shrink-0" :class="ex.severity === 'urgent' ? 'text-red-500' : 'text-amber-500'"
               fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path v-if="ex.icon === 'calendar'" stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            <path v-else-if="ex.icon === 'wrench'" stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
            <path v-else stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
          </svg>
          <span class="flex-1 text-sm font-medium text-gray-800 truncate">{{ ex.label }}</span>
          <span class="text-sm text-gray-500 font-semibold shrink-0">{{ ex.meta }}</span>
          <svg class="w-4 h-4 text-gray-400 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
          </svg>
        </RouterLink>
      </div>
    </div>

    <!-- ── Content grid ───────────────────────────────────────────────────── -->
    <div class="content-grid">

      <!-- Recent Invoices -->
      <div class="content-card">
        <div class="content-hd">
          <div class="content-hd-left">
            <div class="content-icon bg-blue-50 text-blue-600">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 14l6-6m-5.5.5h.01m4.99 5h.01M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16l3.5-2 3.5 2 3.5-2 3.5 2z"/>
              </svg>
            </div>
            <span>Recent Invoices</span>
          </div>
          <RouterLink to="/sales/invoices" class="view-all">View all →</RouterLink>
        </div>
        <table class="table-base">
          <thead>
            <tr>
              <th>Invoice #</th>
              <th>Customer</th>
              <th class="text-right">Total</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <template v-if="loading">
              <tr v-for="n in 5" :key="n"><td colspan="4"><div class="skeleton h-4 my-1.5 rounded" /></td></tr>
            </template>
            <template v-else>
              <tr v-for="inv in recentInvoices" :key="inv.id">
                <td>
                  <RouterLink :to="`/sales/invoices/${inv.id}`" class="mono-link">
                    {{ inv.invoice_number }}
                  </RouterLink>
                </td>
                <td class="text-gray-600 max-w-[140px] truncate">{{ inv.customer_name || 'Walk-in' }}</td>
                <td class="text-right font-semibold text-gray-800">
                  <MoneyDisplay :value="inv.grand_total" />
                </td>
                <td><AppBadge :status="invStatus(inv.status)" /></td>
              </tr>
              <tr v-if="!recentInvoices.length">
                <td colspan="4" class="empty-row">No invoices yet today</td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>

      <!-- Pending Repairs -->
      <div class="content-card">
        <div class="content-hd">
          <div class="content-hd-left">
            <div class="content-icon bg-orange-50 text-orange-600">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065zM15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
            </div>
            <span>Active Repairs</span>
          </div>
          <RouterLink to="/repairs/board" class="view-all">View board →</RouterLink>
        </div>
        <table class="table-base">
          <thead>
            <tr>
              <th>Job #</th>
              <th>Device</th>
              <th>Customer</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <template v-if="loading">
              <tr v-for="n in 5" :key="n"><td colspan="4"><div class="skeleton h-4 my-1.5 rounded" /></td></tr>
            </template>
            <template v-else>
              <tr
                v-for="job in pendingRepairs"
                :key="job.id"
                :class="job.status === 'ready' ? 'row-warn' : ''"
              >
                <td>
                  <RouterLink :to="`/repairs/jobs/${job.id}`" class="mono-link">{{ job.job_number }}</RouterLink>
                </td>
                <td class="text-gray-600 max-w-[120px] truncate">{{ job.device_model }}</td>
                <td class="text-gray-600 max-w-[120px] truncate">{{ job.customer_name }}</td>
                <td><AppBadge :status="repairStatus(job.status)" /></td>
              </tr>
              <tr v-if="!pendingRepairs.length">
                <td colspan="4" class="empty-row">No active repairs</td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>

    </div>
  </div>
</template>

<style scoped>
.dashboard { display: flex; flex-direction: column; gap: 1.5rem; }

/* ── Header ── */
.dash-header {
  display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem;
}
.dash-greeting {
  font-size: 1.75rem;
  font-weight: 900;
  color: #0f1117;
  letter-spacing: -0.03em;
  line-height: 1.15;
}
.dash-date {
  font-size: 1rem;
  color: #9ca3af;
  margin-top: .375rem;
}

/* ── KPI grid ── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1rem;
}

.kpi {
  background: #fff;
  border-radius: 14px;
  border: 1px solid #e5e7eb;
  padding: 1.25rem 1.375rem 1rem;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  box-shadow: 0 1px 4px rgba(0,0,0,.05);
  transition: all 200ms;
  position: relative;
  overflow: hidden;
}
.kpi:hover { box-shadow: 0 6px 20px rgba(0,0,0,.09); transform: translateY(-2px); }

.kpi-accent {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, #e11d48, #fb7185);
  opacity: 0;
  transition: opacity 200ms;
}
.kpi:hover .kpi-accent { opacity: 1; }
.kpi-accent-green  { background: linear-gradient(90deg, #22c55e, #4ade80); }
.kpi-accent-purple { background: linear-gradient(90deg, #8b5cf6, #a78bfa); }
.kpi-accent-orange { background: linear-gradient(90deg, #f97316, #fb923c); }

.kpi-icon {
  width: 44px; height: 44px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.kpi-icon-brand  { background: #fff1f2; color: #e11d48; }
.kpi-icon-green  { background: #f0fdf4; color: #16a34a; }
.kpi-icon-purple { background: #f5f3ff; color: #7c3aed; }
.kpi-icon-orange { background: #fff7ed; color: #ea580c; }
.kpi-icon-red    { background: #fef2f2; color: #dc2626; }
.kpi-icon-gray   { background: #f9fafb; color: #6b7280; }

.kpi-body  { flex: 1; min-width: 0; }
.kpi-label { font-size: .75rem; font-weight: 700; text-transform: uppercase; letter-spacing: .07em; color: #9ca3af; margin-bottom: .2rem; }
.kpi-value { font-size: 1.625rem; font-weight: 800; color: #0f1117; letter-spacing: -.03em; line-height: 1.1; display: block; }
.kpi-sub   { font-size: .8125rem; color: #9ca3af; margin-top: .3rem; }

/* ── Exceptions ── */
.exceptions-card {
  background: #fff;
  border-radius: 14px;
  border: 1px solid #fecaca;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(239,68,68,.08);
}
.exceptions-hd {
  display: flex; align-items: center; justify-content: space-between;
  padding: .875rem 1.25rem;
  background: #fff5f5;
  border-bottom: 1px solid #fecaca;
}
.exceptions-title { font-size: 1rem; font-weight: 700; color: #991b1b; }
.exceptions-meta  { font-size: .875rem; color: #9ca3af; }
.alert-dot {
  width: 10px; height: 10px; border-radius: 50%; background: #ef4444;
  animation: pulse-ring 1.6s infinite;
}

/* ── Content grid ── */
.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(480px, 1fr));
  gap: 1.25rem;
}
.content-card {
  background: #fff; border-radius: 14px;
  border: 1px solid #e5e7eb; overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,.05);
}
.content-hd {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1rem 1.25rem;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  font-size: .875rem; font-weight: 700; color: #374151;
  text-transform: uppercase; letter-spacing: .06em;
}
.content-hd-left { display: flex; align-items: center; gap: .625rem; }
.content-icon {
  width: 28px; height: 28px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.view-all {
  font-size: .875rem; font-weight: 600; color: #e11d48;
  text-decoration: none; text-transform: none; letter-spacing: 0;
  transition: color 120ms;
}
.view-all:hover { color: #9f1239; }

.mono-link {
  font-family: ui-monospace, monospace;
  font-size: .9rem; font-weight: 700;
  color: #e11d48; text-decoration: none;
}
.mono-link:hover { text-decoration: underline; }

.empty-row {
  text-align: center; padding: 2.5rem 0;
  color: #9ca3af; font-size: .9375rem;
}
</style>
