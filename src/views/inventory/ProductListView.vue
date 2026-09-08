<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import { useInventoryStore } from '@/stores/inventory'
import { inventoryApi } from '@/api/inventory'
import { reportsApi } from '@/api/reports'
import { usePagination } from '@/composables/usePagination'
import { usePermissions } from '@/composables/usePermissions'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import AppTable from '@/components/ui/AppTable.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppPagination from '@/components/ui/AppPagination.vue'
import ProductFormModal from './ProductFormModal.vue'

Chart.register(...registerables)

const inv   = useInventoryStore()
const pg    = usePagination({ pageSize: 25 })
const perms = usePermissions()

// ── Filters ────────────────────────────────────────────────────────────────────
const search      = ref('')
const filterCat   = ref('')       // category name
const filterBrand = ref('')       // brand name
const filterStock = ref('')       // '' | 'low' | 'ok'
const sortKey     = ref('name')
const sortDir     = ref('asc')

// ── Form modal ─────────────────────────────────────────────────────────────────
const showForm    = ref(false)
const editProduct = ref(null)

// ── WhatsApp export ────────────────────────────────────────────────────────────
const exporting   = ref(false)

// ── Date-range analytics ───────────────────────────────────────────────────────
const today = new Date().toISOString().slice(0, 10)
const firstOfMonth = new Date(new Date().getFullYear(), new Date().getMonth(), 1)
  .toISOString().slice(0, 10)

const dateFrom       = ref(firstOfMonth)
const dateTo         = ref(today)
const analyticsData  = ref(null)
const analyticsLoading = ref(false)
const chartCanvas    = ref(null)
let   chartInstance  = null

// ── Table columns ──────────────────────────────────────────────────────────────
const columns = [
  { key: 'name',       label: 'Product Name', sortable: true },
  { key: 'brand',      label: 'Brand' },
  { key: 'category',   label: 'Category' },
  { key: 'sku',        label: 'SKU' },
  { key: 'stock',      label: 'Stock',      align: 'right' },
  { key: 'sell_price', label: 'Sell Price', align: 'right' },
  { key: 'cost_price', label: 'Cost Price', align: 'right' },
  { key: 'actions',    label: '' },
]

// ── Load products ──────────────────────────────────────────────────────────────
async function load() {
  const ordering = sortDir.value === 'desc' ? `-${sortKey.value}` : sortKey.value
  const params = {
    search:   search.value || undefined,
    category: filterCat.value || undefined,
    brand:    filterBrand.value || undefined,
    ordering,
    ...pg.queryParams.value,
  }
  if (filterStock.value === 'low') params.low_stock = true
  await inv.fetchProducts(params)
  pg.setFromResponse({ count: inv.pagination.count })
}

function handleSort(key) {
  if (sortKey.value === key) sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  else { sortKey.value = key; sortDir.value = 'asc' }
}

watch([search, filterCat, filterBrand, filterStock, () => pg.currentPage.value, sortKey, sortDir], load)

// ── Filter bar options (loaded from API) ───────────────────────────────────────
const catOptions   = computed(() => inv.categories.map(c => ({ value: c.name, label: c.name })))
const brandOptions = computed(() => inv.brands.map(b => ({ value: b.name, label: b.name })))

const stockOptions = [
  { value: '',    label: 'All Stock' },
  { value: 'low', label: 'Low Stock' },
  { value: 'ok',  label: 'In Stock'  },
]

function clearFilters() {
  search.value = ''; filterCat.value = ''; filterBrand.value = ''; filterStock.value = ''
}

const hasFilters = computed(() =>
  search.value || filterCat.value || filterBrand.value || filterStock.value
)

// ── Analytics ──────────────────────────────────────────────────────────────────
async function loadAnalytics() {
  if (!dateFrom.value || !dateTo.value) return
  analyticsLoading.value = true
  try {
    const { data } = await reportsApi.salesSummary({
      date_from: dateFrom.value,
      date_to: dateTo.value,
    })
    analyticsData.value = data
    await nextTick()
    renderChart(data)
  } catch { analyticsData.value = null }
  finally { analyticsLoading.value = false }
}

function renderChart(data) {
  if (!chartCanvas.value) return
  if (chartInstance) { chartInstance.destroy(); chartInstance = null }

  const labels  = (data.daily || []).map(d => d.date)
  const totals  = (data.daily || []).map(d => parseFloat(d.total || 0))
  const counts  = (data.daily || []).map(d => d.count || 0)

  chartInstance = new Chart(chartCanvas.value, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Revenue (PKR)',
          data: totals,
          backgroundColor: 'rgba(225,29,72,.75)',
          borderColor: '#e11d48',
          borderWidth: 1.5,
          borderRadius: 4,
          yAxisID: 'y',
        },
        {
          label: 'Invoices',
          data: counts,
          type: 'line',
          borderColor: '#2563eb',
          backgroundColor: 'rgba(37,99,235,.08)',
          borderWidth: 2,
          pointBackgroundColor: '#2563eb',
          pointRadius: 3,
          tension: 0.35,
          fill: true,
          yAxisID: 'y1',
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top', labels: { font: { size: 11 }, boxWidth: 12 } },
        tooltip: {
          callbacks: {
            label: ctx => ctx.datasetIndex === 0
              ? `Revenue: Rs. ${Number(ctx.raw).toLocaleString()}`
              : `Invoices: ${ctx.raw}`,
          },
        },
      },
      scales: {
        y:  { position: 'left',  title: { display: true, text: 'Revenue (PKR)', font: { size: 10 } }, grid: { color: 'rgba(0,0,0,.05)' } },
        y1: { position: 'right', title: { display: true, text: 'Invoices',      font: { size: 10 } }, grid: { drawOnChartArea: false } },
        x:  { grid: { display: false }, ticks: { font: { size: 10 } } },
      },
    },
  })
}

watch([dateFrom, dateTo], loadAnalytics)

// ── WhatsApp export ────────────────────────────────────────────────────────────
async function exportAndShareWhatsApp() {
  exporting.value = true
  try {
    const params = {
      search:   search.value   || undefined,
      category: filterCat.value || undefined,
      brand:    filterBrand.value || undefined,
    }
    const { data } = await inventoryApi.exportExcel(params)
    const fileUrl  = data.file_url   // absolute URL returned by backend
    const fileName = data.file_name  // e.g. products-2026-09-08.xlsx

    const msg = [
      `📦 *My Phone — Product List*`,
      `━━━━━━━━━━━━━━━━━━━━━━`,
      `📅 Date: ${new Date().toLocaleDateString('en-PK')}`,
      filterCat.value   ? `📂 Category: ${filterCat.value}` : null,
      filterBrand.value ? `🏷️ Brand: ${filterBrand.value}`  : null,
      search.value      ? `🔍 Search: ${search.value}`       : null,
      ``,
      `📥 Download Excel:`,
      fileUrl,
      ``,
      `_Sent from My Phone ERP_`,
    ].filter(Boolean).join('\n')

    window.open(
      `https://wa.me/?text=${encodeURIComponent(msg)}`,
      '_blank',
      'noopener,noreferrer'
    )
  } catch (e) {
    console.error('Export failed', e)
  } finally {
    exporting.value = false
  }
}

// ── Init ───────────────────────────────────────────────────────────────────────
function openNew()   { editProduct.value = null; showForm.value = true }
function openEdit(p) { editProduct.value = p;    showForm.value = true }
function onSaved()   { showForm.value = false;   load() }

onMounted(async () => {
  await Promise.all([
    load(),
    inv.fetchCategories(),
    inv.fetchBrands(),
    loadAnalytics(),
  ])
})
</script>

<template>
  <div class="space-y-4">

    <!-- ══ FILTER BAR ═══════════════════════════════════════════════════════ -->
    <div class="filter-bar">
      <!-- Search -->
      <div class="search-wrap">
        <svg class="search-icon" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <input
          v-model="search"
          type="search"
          class="search-input"
          placeholder="Search name, SKU, brand…"
        />
      </div>

      <!-- Scrollable pill filters -->
      <div class="pills-scroll">

        <!-- Stock status pills -->
        <button
          v-for="opt in stockOptions"
          :key="opt.value"
          class="pill"
          :class="filterStock === opt.value ? 'pill-active' : ''"
          @click="filterStock = opt.value"
        >
          {{ opt.label }}
        </button>

        <div class="pill-sep" />

        <!-- Category pills -->
        <button
          class="pill"
          :class="filterCat === '' ? 'pill-active' : ''"
          @click="filterCat = ''"
        >All Categories</button>
        <button
          v-for="c in catOptions"
          :key="c.value"
          class="pill"
          :class="filterCat === c.value ? 'pill-active' : ''"
          @click="filterCat = c.value"
        >
          {{ c.label }}
        </button>

        <div class="pill-sep" />

        <!-- Brand pills -->
        <button
          class="pill"
          :class="filterBrand === '' ? 'pill-active' : ''"
          @click="filterBrand = ''"
        >All Brands</button>
        <button
          v-for="b in brandOptions"
          :key="b.value"
          class="pill"
          :class="filterBrand === b.value ? 'pill-active' : ''"
          @click="filterBrand = b.value"
        >
          {{ b.label }}
        </button>
      </div>

      <!-- Right actions -->
      <div class="bar-actions">
        <button v-if="hasFilters" class="clear-btn" @click="clearFilters">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
          </svg>
          Clear
        </button>

        <!-- WhatsApp export -->
        <button class="wa-export-btn" :disabled="exporting" @click="exportAndShareWhatsApp">
          <svg v-if="exporting" class="w-4 h-4 spin-anim" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4">
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
          </svg>
          <span>{{ exporting ? 'Exporting…' : 'Send via WhatsApp' }}</span>
        </button>

        <AppButton variant="primary" @click="openNew">+ Add Product</AppButton>
      </div>
    </div>

    <!-- ══ DATE RANGE ANALYTICS ════════════════════════════════════════════ -->
    <div class="analytics-card">
      <!-- Date pickers header -->
      <div class="analytics-header">
        <div class="flex items-center gap-2">
          <div class="analytics-icon">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
            </svg>
          </div>
          <span class="analytics-title">Sales Analytics</span>
        </div>
        <div class="date-pickers">
          <label class="date-label">From</label>
          <input v-model="dateFrom" type="date" class="input input-sm date-input" />
          <label class="date-label">To</label>
          <input v-model="dateTo"   type="date" class="input input-sm date-input" />
        </div>
      </div>

      <!-- KPI summary row -->
      <div v-if="analyticsData" class="analytics-kpis">
        <div class="akpi">
          <span class="akpi-label">Total Revenue</span>
          <span class="akpi-value">PKR {{ Number(analyticsData.totals?.total_revenue || 0).toLocaleString() }}</span>
        </div>
        <div class="akpi">
          <span class="akpi-label">Invoices</span>
          <span class="akpi-value">{{ analyticsData.totals?.total_invoices || 0 }}</span>
        </div>
        <div class="akpi">
          <span class="akpi-label">Discounts Given</span>
          <span class="akpi-value text-red-600">PKR {{ Number(analyticsData.totals?.total_discount || 0).toLocaleString() }}</span>
        </div>
        <div class="akpi">
          <span class="akpi-label">Tax Collected</span>
          <span class="akpi-value">PKR {{ Number(analyticsData.totals?.total_tax || 0).toLocaleString() }}</span>
        </div>
      </div>

      <!-- Chart -->
      <div class="chart-wrap">
        <div v-if="analyticsLoading" class="chart-loading">
          <svg class="w-6 h-6 spin-anim text-gray-300" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
        </div>
        <canvas v-else ref="chartCanvas" />
      </div>

      <!-- Daily breakdown table -->
      <div v-if="analyticsData?.daily?.length" class="daily-table-wrap">
        <table class="table-base">
          <thead>
            <tr>
              <th>Date</th>
              <th class="text-right">Revenue (PKR)</th>
              <th class="text-right">Invoices</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in analyticsData.daily" :key="row.date">
              <td class="font-mono text-xs">{{ row.date }}</td>
              <td class="text-right font-semibold">{{ Number(row.total).toLocaleString() }}</td>
              <td class="text-right">{{ row.count }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else-if="!analyticsLoading" class="empty-analytics">
        No sales data for the selected period.
      </div>
    </div>

    <!-- ══ PRODUCTS TABLE ══════════════════════════════════════════════════ -->
    <AppTable
      :columns="columns"
      :loading="inv.loading"
      empty-message="No products found"
      :sort-key="sortKey"
      :sort-dir="sortDir"
      @sort="handleSort"
    >
      <tr v-for="p in inv.products" :key="p.id" class="cursor-pointer hover:bg-gray-50">
        <td class="px-3 py-2.5">
          <RouterLink :to="`/inventory/products/${p.id}`" class="font-medium text-[#e11d48] hover:underline">
            {{ p.name }}
          </RouterLink>
        </td>
        <td class="px-3 py-2.5 text-gray-600">{{ p.brand || '—' }}</td>
        <td class="px-3 py-2.5 text-gray-600">{{ p.category || '—' }}</td>
        <td class="px-3 py-2.5 font-mono text-xs text-gray-500">{{ p.sku }}</td>
        <td class="px-3 py-2.5 text-right">
          <span :class="p.stock_qty <= p.reorder_level ? 'text-red-600 font-semibold' : 'text-gray-700'">
            {{ p.stock_qty ?? '—' }}
          </span>
        </td>
        <td class="px-3 py-2.5 text-right">
          <MoneyDisplay :value="p.sell_price" />
        </td>
        <td class="px-3 py-2.5 text-right">
          <MoneyDisplay :value="p.cost_price" :mask="!perms.canViewCost.value" />
        </td>
        <td class="px-3 py-2.5 text-right">
          <button class="text-xs text-[#e11d48] hover:underline" @click.stop="openEdit(p)">Edit</button>
        </td>
      </tr>
    </AppTable>

    <AppPagination
      :current-page="pg.currentPage.value"
      :total-pages="pg.totalPages.value"
      :total-count="pg.totalCount.value"
      :page-size="pg.pageSize.value"
      @page="pg.goTo"
    />

    <ProductFormModal
      :open="showForm"
      :product="editProduct"
      @close="showForm = false"
      @saved="onSaved"
    />
  </div>
</template>

<style scoped>
/* ── Filter bar ──────────────────────────────────────────────────────────────── */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 0.625rem 0.875rem;
  box-shadow: 0 1px 3px rgba(0,0,0,.05);
  flex-wrap: wrap;
}

.search-wrap { position: relative; flex-shrink: 0; }
.search-icon { position: absolute; left:.625rem; top:50%; transform:translateY(-50%); width:14px; height:14px; color:#9ca3af; pointer-events:none; }
.search-input {
  width: 200px;
  padding: .375rem .75rem .375rem 2rem;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  font-size: .8125rem;
  outline: none;
  transition: border-color 150ms;
  background: #f9fafb;
}
.search-input:focus { border-color: #e11d48; background: white; box-shadow: 0 0 0 3px rgba(225,29,72,.1); }

.pills-scroll {
  display: flex;
  align-items: center;
  gap: .375rem;
  overflow-x: auto;
  flex: 1;
  min-width: 0;
  padding-bottom: 2px; /* scrollbar clearance */
  scrollbar-width: none;
}
.pills-scroll::-webkit-scrollbar { display: none; }

.pill {
  flex-shrink: 0;
  padding: .25rem .75rem;
  border-radius: 99px;
  border: 1.5px solid #e5e7eb;
  background: white;
  font-size: .75rem;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  white-space: nowrap;
  transition: all 120ms;
}
.pill:hover { border-color: #e11d48; color: #e11d48; background: #fff1f2; }
.pill-active { background: #fff1f2; border-color: #e11d48; color: #be123c; font-weight: 700; }

.pill-sep { width: 1px; height: 18px; background: #e5e7eb; flex-shrink: 0; margin: 0 .25rem; }

.bar-actions { display:flex; align-items:center; gap:.5rem; flex-shrink:0; }

.clear-btn {
  display: inline-flex; align-items: center; gap:.25rem;
  padding: .3rem .625rem; border-radius: 6px;
  font-size: .75rem; font-weight: 600; color: #6b7280;
  background: #f3f4f6; border: 1px solid #e5e7eb; cursor: pointer;
  transition: all 120ms;
}
.clear-btn:hover { background: #fee2e2; color: #be123c; border-color: #fecdd3; }

/* WhatsApp export button */
.wa-export-btn {
  display: inline-flex; align-items: center; gap:.4rem;
  padding: .375rem .875rem;
  border-radius: 8px;
  background: linear-gradient(135deg,#25d366,#128c7e);
  color: white; font-size: .8rem; font-weight: 700;
  border: none; cursor: pointer;
  transition: all 150ms;
  box-shadow: 0 2px 8px rgba(37,211,102,.3);
  white-space: nowrap;
}
.wa-export-btn:hover { background:linear-gradient(135deg,#20bc5a,#0e7a6e); transform:translateY(-1px); box-shadow:0 4px 14px rgba(37,211,102,.4); }
.wa-export-btn:disabled { opacity:.6; pointer-events:none; }

/* ── Analytics card ──────────────────────────────────────────────────────────── */
.analytics-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,.05);
}

.analytics-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: .75rem 1rem;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  flex-wrap: wrap; gap: .5rem;
}
.analytics-icon {
  width: 28px; height: 28px; border-radius: 8px;
  background: #fff1f2; color: #e11d48;
  display: flex; align-items: center; justify-content: center;
}
.analytics-title {
  font-size: .75rem; font-weight: 700; color: #374151;
  text-transform: uppercase; letter-spacing: .06em;
}

.date-pickers { display: flex; align-items: center; gap: .5rem; }
.date-label   { font-size: .75rem; font-weight: 600; color: #6b7280; }
.date-input   { width: 140px; }

.analytics-kpis {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px,1fr));
  gap: 1px;
  background: #e5e7eb;
  border-bottom: 1px solid #e5e7eb;
}
.akpi {
  display: flex; flex-direction: column; gap: .15rem;
  padding: .75rem 1rem; background: white;
}
.akpi-label { font-size: .6rem; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; color: #9ca3af; }
.akpi-value { font-size: 1.1rem; font-weight: 800; color: #111827; font-variant-numeric: tabular-nums; }

.chart-wrap {
  padding: 1rem;
  height: 220px;
  position: relative;
}
.chart-loading {
  height: 100%;
  display: flex; align-items: center; justify-content: center;
}

.daily-table-wrap {
  border-top: 1px solid #f3f4f6;
  max-height: 220px;
  overflow-y: auto;
}

.empty-analytics {
  padding: 2rem;
  text-align: center;
  color: #9ca3af;
  font-size: .8rem;
}

/* ── Spinner ──────────────────────────────────────────────────────────────────── */
@keyframes spin { to { transform: rotate(360deg); } }
.spin-anim { animation: spin .7s linear infinite; }
</style>
