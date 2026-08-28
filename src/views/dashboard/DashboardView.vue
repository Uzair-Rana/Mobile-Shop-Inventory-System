<script setup>
/**
 * DashboardView — exception-first layout.
 *
 * Visual hierarchy:
 *   1. Exception rail  — low stock · overdue installments · stuck repairs · sync errors
 *   2. KPI strip       — today's numbers (compact, one row)
 *   3. Two columns     — recent invoices (left) | pending repairs (right)
 *
 * If there are zero exceptions, the rail collapses to nothing — no "All clear" fluff.
 * Vanity greeting removed. Date + shift info in the top bar is enough.
 */
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { usePermissions } from '@/composables/usePermissions'
import { useSyncStore } from '@/stores/sync'
import { salesApi } from '@/api/sales'
import { inventoryApi } from '@/api/inventory'
import { repairsApi } from '@/api/repairs'
import { installmentsApi } from '@/api/installments'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import { formatDate, daysUntil } from '@/utils/date'
import { INVOICE_STATUS, REPAIR_STATUS, INSTALLMENT_STATUS } from '@/utils/constants'

const auth  = useAuthStore()
const perms = usePermissions()
const sync  = useSyncStore()

const loading        = ref(true)
const summary        = ref(null)
const lowStock       = ref([])
const recentInvoices = ref([])
const pendingRepairs = ref([])
const overdueInstall = ref([])
const today          = new Date().toISOString().slice(0, 10)

onMounted(async () => {
  try {
    const [sumRes, stockRes, invRes, repairRes, installRes] = await Promise.allSettled([
      salesApi.getDailySummary(today),
      inventoryApi.listLowStock({ page_size: 8 }),
      salesApi.listInvoices({ ordering: '-created_at', page_size: 8 }),
      repairsApi.listJobs({ status: 'waiting_parts,in_progress,ready', page_size: 8 }),
      installmentsApi.listOverdue({ page_size: 8 }),
    ])
    if (sumRes.status === 'fulfilled')     summary.value        = sumRes.value.data
    if (stockRes.status === 'fulfilled')   lowStock.value       = stockRes.value.data.results   ?? stockRes.value.data
    if (invRes.status === 'fulfilled')     recentInvoices.value = invRes.value.data.results     ?? invRes.value.data
    if (repairRes.status === 'fulfilled')  pendingRepairs.value = repairRes.value.data.results  ?? repairRes.value.data
    if (installRes.status === 'fulfilled') overdueInstall.value = installRes.value.data.results ?? installRes.value.data
  } finally {
    loading.value = false
  }
})

// Build exception list — only items that need attention now
const exceptions = computed(() => {
  const list = []

  if (sync.status.value === 'error' || sync.status.value === 'offline') {
    list.push({
      severity: 'urgent',
      icon: 'wifi',
      label: sync.status.value === 'offline' ? 'Device is offline — sales may not sync' : 'Sync error — check connection',
      link: null,
    })
  }

  overdueInstall.value.forEach(p => list.push({
    severity: 'urgent',
    icon: 'calendar',
    label: `Overdue: ${p.customer_name} — ${p.plan_number}`,
    meta: `Rs. ${p.overdue_amount?.toLocaleString() ?? '?'} overdue`,
    link: `/installments/${p.id}`,
  }))

  pendingRepairs.value
    .filter(r => r.status === 'ready')
    .forEach(r => list.push({
      severity: 'warn',
      icon: 'wrench',
      label: `Ready for pickup: ${r.customer_name} — ${r.device_model}`,
      meta: `#${r.job_number}`,
      link: `/repairs/jobs/${r.id}`,
    }))

  pendingRepairs.value
    .filter(r => r.status === 'waiting_parts')
    .forEach(r => list.push({
      severity: 'warn',
      icon: 'wrench',
      label: `Waiting parts: ${r.device_model}`,
      meta: `#${r.job_number}`,
      link: `/repairs/jobs/${r.id}`,
    }))

  lowStock.value.forEach(item => list.push({
    severity: 'warn',
    icon: 'box',
    label: `Low stock: ${item.name}`,
    meta: `${item.stock_qty} remaining`,
    link: `/inventory/accessories`,
  }))

  return list
})

function invStatusObj(val) {
  return Object.values(INVOICE_STATUS).find(s => s.value === val) || { label: val, badge: 'badge-gray' }
}
function repairStatusObj(val) {
  return Object.values(REPAIR_STATUS).find(s => s.value === val) || { label: val, badge: 'badge-gray' }
}

// Cash variance: difference between expected cash and what was received
const cashVariance = computed(() => {
  if (!summary.value) return null
  return (summary.value.cash_received || 0) - (summary.value.expected_cash || 0)
})
</script>

<template>
  <div class="space-y-2.5">

    <!-- ── 1. Exception rail — leads the page ─────────────────────────────── -->
    <div v-if="!loading && exceptions.length > 0" class="card overflow-hidden">
      <div class="panel-header">
        <div class="flex items-center gap-1.5">
          <!-- Pulsing dot only when there are urgent items -->
          <span
            v-if="exceptions.some(e => e.severity === 'urgent')"
            class="h-1.5 w-1.5 rounded-full bg-red-500 animate-pulse"
            aria-hidden="true"
          />
          <span>Attention Required</span>
          <span class="badge badge-red ml-1">{{ exceptions.length }}</span>
        </div>
      </div>
      <ul>
        <li
          v-for="(ex, i) in exceptions"
          :key="i"
          :class="ex.severity === 'urgent' ? 'exception-row-urgent' : 'exception-row-warn'"
        >
          <!-- Severity indicator bar -->
          <div
            class="w-0.5 self-stretch shrink-0 rounded-full"
            :class="ex.severity === 'urgent' ? 'bg-red-500' : 'bg-amber-400'"
            aria-hidden="true"
          />

          <!-- Icon -->
          <svg class="w-3.5 h-3.5 shrink-0" :class="ex.severity === 'urgent' ? 'text-red-500' : 'text-amber-500'" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true">
            <path v-if="ex.icon === 'calendar'"  stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            <path v-else-if="ex.icon === 'wrench'" stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
            <path v-else-if="ex.icon === 'box'" stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
            <path v-else stroke-linecap="round" stroke-linejoin="round" d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
          </svg>

          <!-- Message -->
          <div class="flex-1 min-w-0">
            <RouterLink
              v-if="ex.link"
              :to="ex.link"
              class="text-xs font-medium text-gray-900 hover:underline underline-offset-2 truncate block"
            >{{ ex.label }}</RouterLink>
            <span v-else class="text-xs font-medium text-gray-900 truncate block">{{ ex.label }}</span>
          </div>

          <!-- Meta -->
          <span v-if="ex.meta" class="text-[11px] text-gray-500 shrink-0 tabular-nums">{{ ex.meta }}</span>

          <!-- Arrow -->
          <RouterLink
            v-if="ex.link"
            :to="ex.link"
            class="shrink-0 text-gray-400 hover:text-gray-600"
            aria-label="Go to issue"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
            </svg>
          </RouterLink>
        </li>
      </ul>
    </div>

    <!-- ── 2. KPI strip — one compact row, not hero cards ─────────────────── -->
    <div class="grid grid-cols-2 sm:grid-cols-4 xl:grid-cols-6 gap-2">
      <div class="stat-cell">
        <span class="stat-label">Today's Sales</span>
        <MoneyDisplay :value="summary?.total_sales" class="stat-value" />
        <span class="stat-sub">{{ summary?.invoice_count ?? 0 }} invoices</span>
      </div>

      <div class="stat-cell">
        <span class="stat-label">Cash In</span>
        <MoneyDisplay :value="summary?.cash_received" class="stat-value text-green-700" />
        <span class="stat-sub">collected today</span>
      </div>

      <div class="stat-cell">
        <span class="stat-label">Gross Profit</span>
        <MoneyDisplay
          :value="summary?.gross_profit"
          :mask="!perms.canViewProfit.value"
          class="stat-value text-blue-700"
        />
        <span v-if="perms.canViewProfit.value && summary?.gross_margin != null" class="stat-sub">
          {{ summary.gross_margin?.toFixed(1) }}% margin
        </span>
      </div>

      <!-- Cash variance — only shown when non-zero, draws attention if there's a discrepancy -->
      <div
        class="stat-cell"
        :class="cashVariance !== null && cashVariance !== 0 ? (cashVariance < 0 ? 'border-red-300' : 'border-green-300') : ''"
      >
        <span class="stat-label">Cash Variance</span>
        <MoneyDisplay
          :value="cashVariance"
          class="stat-value"
          :class="cashVariance == null ? '' : cashVariance < 0 ? 'text-red-600' : cashVariance > 0 ? 'text-green-700' : 'text-gray-900'"
        />
        <span class="stat-sub">vs. expected</span>
      </div>

      <div class="stat-cell">
        <span class="stat-label">Open Repairs</span>
        <p class="stat-value">{{ summary?.open_repairs ?? pendingRepairs.length }}</p>
        <span class="stat-sub">{{ summary?.repairs_ready ?? 0 }} ready pickup</span>
      </div>

      <div class="stat-cell">
        <span class="stat-label">Overdue Plans</span>
        <p class="stat-value" :class="overdueInstall.length > 0 ? 'text-red-600' : ''">
          {{ summary?.overdue_plans ?? overdueInstall.length }}
        </p>
        <span class="stat-sub">installments</span>
      </div>
    </div>

    <!-- ── 3. Two-column working area ─────────────────────────────────────── -->
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-2.5">

      <!-- Recent invoices -->
      <div class="card overflow-hidden">
        <div class="panel-header">
          <span>Recent Invoices</span>
          <RouterLink to="/sales/invoices" class="text-[11px] text-blue-500 hover:underline font-normal normal-case tracking-normal">
            All invoices →
          </RouterLink>
        </div>
        <table class="table-base">
          <thead>
            <tr>
              <th>Invoice</th>
              <th>Customer</th>
              <th class="text-right">Total</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="inv in recentInvoices" :key="inv.id">
              <td class="font-mono text-blue-700">
                <RouterLink :to="`/sales/invoices/${inv.id}`" class="hover:underline">#{{ inv.invoice_number }}</RouterLink>
              </td>
              <td>
                <span class="truncate max-w-[10rem] block">{{ inv.customer_name || 'Walk-in' }}</span>
              </td>
              <td class="text-right money font-medium">
                <MoneyDisplay :value="inv.grand_total" />
              </td>
              <td>
                <AppBadge :status="invStatusObj(inv.status)" />
              </td>
            </tr>
            <tr v-if="!loading && recentInvoices.length === 0">
              <td colspan="4" class="py-6 text-center text-gray-400 text-xs">No invoices today</td>
            </tr>
            <!-- Loading skeleton -->
            <template v-if="loading">
              <tr v-for="n in 5" :key="n">
                <td colspan="4"><div class="h-3 bg-gray-100 rounded animate-pulse my-1" /></td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>

      <!-- Pending repairs -->
      <div class="card overflow-hidden">
        <div class="panel-header">
          <span>Pending Repairs</span>
          <RouterLink to="/repairs/jobs" class="text-[11px] text-blue-500 hover:underline font-normal normal-case tracking-normal">
            All jobs →
          </RouterLink>
        </div>
        <table class="table-base">
          <thead>
            <tr>
              <th>Job</th>
              <th>Device</th>
              <th>Customer</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="job in pendingRepairs"
              :key="job.id"
              :class="job.status === 'ready' ? 'row-warn' : ''"
            >
              <td class="font-mono text-blue-700">
                <RouterLink :to="`/repairs/jobs/${job.id}`" class="hover:underline">#{{ job.job_number }}</RouterLink>
              </td>
              <td class="truncate max-w-[8rem]">{{ job.device_model }}</td>
              <td class="truncate max-w-[8rem]">{{ job.customer_name }}</td>
              <td><AppBadge :status="repairStatusObj(job.status)" /></td>
            </tr>
            <tr v-if="!loading && pendingRepairs.length === 0">
              <td colspan="4" class="py-6 text-center text-gray-400 text-xs">No pending jobs</td>
            </tr>
            <template v-if="loading">
              <tr v-for="n in 4" :key="n">
                <td colspan="4"><div class="h-3 bg-gray-100 rounded animate-pulse my-1" /></td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>

    </div><!-- /grid -->
  </div>
</template>
