<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { sparePartsApi } from '@/api/spareParts'
import { useUiStore } from '@/stores/ui'
import AppButton from '@/components/ui/AppButton.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import SparePartFormModal from './SparePartFormModal.vue'

const route  = useRoute()
const router = useRouter()
const ui     = useUiStore()

const part       = ref(null)
const categories = ref([])
const loading    = ref(true)
const showEdit   = ref(false)

// Entry panel state
const entryMode  = ref('in')
const entryQty   = ref(1)
const entryType  = ref('purchase')
const entryRef   = ref('')
const entryNote  = ref('')
const entryUnit  = ref(null)
const submitting = ref(false)
const entryErr   = ref('')

const inTypes  = [
  { value: 'purchase',        label: 'Purchase / Stock-In'   },
  { value: 'opening_balance', label: 'Opening Balance'        },
  { value: 'return_in',       label: 'Return from Tech'       },
  { value: 'adjustment_in',   label: 'Manual Adjustment (In)' },
  { value: 'transfer_in',     label: 'Transfer In'            },
]
const outTypes = [
  { value: 'repair_use',      label: 'Used in Repair'          },
  { value: 'sale',            label: 'Sold to Customer'        },
  { value: 'damaged',         label: 'Damaged / Write-Off'     },
  { value: 'testing',         label: 'Used for Testing'        },
  { value: 'adjustment_out',  label: 'Manual Adjustment (Out)' },
  { value: 'return_out',      label: 'Returned to Supplier'    },
  { value: 'transfer_out',    label: 'Transfer Out'            },
]

const entryTypes = computed(() => entryMode.value === 'in' ? inTypes : outTypes)

// Ledger rows sorted ascending for reconstruction display
const ledger = computed(() =>
  [...(part.value?.ledger || [])].sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
)

const totalIn  = computed(() => ledger.value.reduce((s, e) => e.qty > 0 ? s + e.qty : s, 0))
const totalOut = computed(() => ledger.value.reduce((s, e) => e.qty < 0 ? s + Math.abs(e.qty) : s, 0))
const stockOnHand = computed(() => part.value?.stock_on_hand ?? 0)

const entryTypeLabels = {
  opening_balance: 'Opening Balance', purchase: 'Purchase',
  repair_use: 'Used in Repair',       sale: 'Sale',
  return_in: 'Return In',             return_out: 'Return Out',
  adjustment_in: 'Adj. In',           adjustment_out: 'Adj. Out',
  transfer_in: 'Transfer In',         transfer_out: 'Transfer Out',
  damaged: 'Damaged',                 testing: 'Testing',
}

const catColors = {
  display_panel: '#3b82f6', oca_glass: '#06b6d4', battery: '#22c55e',
  charging_flex: '#f59e0b', body_frame: '#f97316', camera_module: '#8b5cf6',
}

async function load() {
  loading.value = true
  try {
    const [partRes, catRes] = await Promise.allSettled([
      sparePartsApi.get(route.params.id),
      sparePartsApi.categories(),
    ])
    if (partRes.status === 'fulfilled') part.value = partRes.value.data
    else { router.replace('/spare-parts'); return }
    if (catRes.status === 'fulfilled')  categories.value = catRes.value.data
  } finally { loading.value = false }
}

onMounted(load)

function setMode(m) {
  entryMode.value  = m
  entryType.value  = m === 'in' ? inTypes[0].value : outTypes[0].value
  entryQty.value   = 1
  entryRef.value   = ''
  entryNote.value  = ''
  entryUnit.value  = null
  entryErr.value   = ''
}

async function submitEntry() {
  if (entryQty.value < 1) { entryErr.value = 'Qty must be at least 1.'; return }
  if (entryMode.value === 'out' && entryQty.value > stockOnHand.value) {
    entryErr.value = `Only ${stockOnHand.value} in stock.`; return
  }
  submitting.value = true
  entryErr.value   = ''
  try {
    const payload = { entry_type: entryType.value, qty: entryQty.value, reference: entryRef.value, note: entryNote.value }
    if (entryMode.value === 'in' && entryUnit.value) payload.unit_cost = entryUnit.value
    if (entryMode.value === 'in') {
      await sparePartsApi.stockIn(part.value.id, payload)
    } else {
      await sparePartsApi.stockOut(part.value.id, payload)
    }
    ui.toastSuccess?.(`Stock ${entryMode.value === 'in' ? 'in' : 'out'} recorded.`)
    await load()
    setMode(entryMode.value)
  } catch (e) {
    entryErr.value = e.displayMessage || e.response?.data?.detail || 'Failed.'
  } finally { submitting.value = false }
}

function fmtDate(iso) {
  return new Date(iso).toLocaleString('en-PK', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function exportCsv() {
  const rows = [
    ['Date', 'Type', 'Qty', 'Balance After', 'Unit Cost', 'Reference', 'Note', 'By'],
    ...ledger.value.map(e => [
      fmtDate(e.created_at), entryTypeLabels[e.entry_type] || e.entry_type,
      e.qty, e.balance_after, e.unit_cost ?? '', e.reference ?? '', e.note ?? '', e.actor_name ?? '',
    ]),
  ]
  const csv  = rows.map(r => r.map(v => `"${String(v).replace(/"/g, '""')}"`).join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href     = url
  a.download = `ledger-${part.value?.sku}-${new Date().toISOString().slice(0,10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <div v-if="loading" class="flex items-center justify-center py-24 text-gray-400 text-lg">Loading…</div>

  <div v-else-if="part" class="detail-layout">

    <!-- ── Left: Part info + Ledger ───────────────────────────────────── -->
    <div class="detail-left">

      <!-- Header card -->
      <div class="info-card" :style="`border-top: 4px solid ${catColors[part.category] || '#9ca3af'}`">
        <div class="info-head">
          <div class="flex-1 min-w-0">
            <div class="info-sku">{{ part.sku }}</div>
            <h2 class="info-name">{{ part.name }}</h2>
            <p class="info-cat">{{ part.category_display }}</p>
          </div>
          <div class="info-stock" :class="part.low_stock ? 'stock-low' : 'stock-ok'">
            <span class="stock-big">{{ stockOnHand }}</span>
            <span class="stock-label">in stock</span>
            <span v-if="part.low_stock" class="low-warn">⚠ Low</span>
          </div>
        </div>

        <div v-if="part.brand_compat" class="compat-row">
          <span class="compat-chip">🏷 {{ part.brand_compat }}</span>
          <span v-if="part.model_compat" class="compat-chip">📱 {{ part.model_compat }}</span>
        </div>

        <div class="attr-chips">
          <span v-if="part.display_type && part.display_type !== 'N/A'" class="attr-chip chip-blue">{{ part.display_type }}</span>
          <span v-if="part.with_frame" class="attr-chip chip-gray">With Frame</span>
          <span v-if="part.battery_capacity" class="attr-chip chip-green">{{ part.battery_capacity }} mAh</span>
          <span v-if="part.camera_position && part.camera_position !== 'N/A'" class="attr-chip chip-purple">
            {{ part.camera_position === 'front' ? 'Front' : part.camera_position === 'rear' ? 'Rear' : 'Front+Rear' }} Camera
          </span>
        </div>

        <div class="price-row">
          <div class="price-block">
            <span class="price-lbl">Cost Price</span>
            <MoneyDisplay :value="part.cost_price" class="price-val" />
          </div>
          <div class="price-block">
            <span class="price-lbl">Sell Price</span>
            <MoneyDisplay :value="part.sell_price" class="price-val text-red-600" />
          </div>
          <div class="price-block">
            <span class="price-lbl">Reorder At</span>
            <span class="price-val">{{ part.reorder_level }}</span>
          </div>
        </div>

        <div class="info-actions">
          <AppButton variant="ghost" size="sm" @click="router.push('/spare-parts')">← Back</AppButton>
          <AppButton variant="secondary" size="sm" @click="showEdit = true">Edit Part</AppButton>
        </div>
      </div>

      <!-- Ledger summary KPIs -->
      <div class="kpi-row">
        <div class="kpi-box kpi-in">
          <span class="kpi-label">Total Received</span>
          <span class="kpi-val">+{{ totalIn }}</span>
        </div>
        <div class="kpi-box kpi-out">
          <span class="kpi-label">Total Issued</span>
          <span class="kpi-val">−{{ totalOut }}</span>
        </div>
        <div class="kpi-box">
          <span class="kpi-label">Net Balance</span>
          <span class="kpi-val font-extrabold" :class="stockOnHand <= part.reorder_level ? 'text-red-600' : 'text-gray-900'">
            {{ stockOnHand }}
          </span>
        </div>
        <div class="kpi-box">
          <span class="kpi-label">Entries</span>
          <span class="kpi-val">{{ ledger.length }}</span>
        </div>
      </div>

      <!-- Ledger table -->
      <div class="ledger-section">
        <div class="ledger-hd">
          <span class="ledger-title">Stock Ledger</span>
          <button v-if="ledger.length" class="export-btn" @click="exportCsv">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
            </svg>
            Export CSV
          </button>
        </div>

        <div class="ledger-wrap">
          <table v-if="ledger.length" class="ledger-tbl">
            <thead>
              <tr>
                <th>#</th>
                <th>Date</th>
                <th>Type</th>
                <th class="r">Qty</th>
                <th class="r">Balance</th>
                <th>Reference</th>
                <th>Note</th>
                <th>By</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(entry, i) in ledger" :key="entry.id" :class="entry.qty > 0 ? 'tr-in' : 'tr-out'">
                <td class="mono-xs text-gray-400">{{ i + 1 }}</td>
                <td class="mono-xs text-gray-500 nowrap">{{ fmtDate(entry.created_at) }}</td>
                <td>
                  <span class="type-tag" :class="entry.qty > 0 ? 'tag-in' : 'tag-out'">
                    {{ entry.qty > 0 ? '▲' : '▼' }} {{ entryTypeLabels[entry.entry_type] || entry.entry_type }}
                  </span>
                </td>
                <td class="r bold" :class="entry.qty > 0 ? 'text-green-700' : 'text-red-600'">
                  {{ entry.qty > 0 ? '+' : '' }}{{ entry.qty }}
                </td>
                <td class="r bold tabular">{{ entry.balance_after }}</td>
                <td class="mono-xs text-gray-600">{{ entry.reference || '—' }}</td>
                <td class="td-note text-gray-600">{{ entry.note || '—' }}</td>
                <td class="text-gray-400 mono-xs">{{ entry.actor_name || 'sys' }}</td>
              </tr>
            </tbody>
          </table>
          <div v-else class="ledger-empty">
            No entries yet. Use the panel on the right to record your first stock movement.
          </div>
        </div>
      </div>
    </div>

    <!-- ── Right: Quick entry panel ──────────────────────────────────── -->
    <div class="entry-col">
      <div class="entry-card">
        <div class="entry-title-row">
          <span class="entry-title">Record Movement</span>
          <div class="mode-toggle">
            <button class="mtog" :class="entryMode === 'in' ? 'mtog-in' : ''" @click="setMode('in')">
              ▲ In
            </button>
            <button class="mtog" :class="entryMode === 'out' ? 'mtog-out' : ''" :disabled="stockOnHand === 0" @click="setMode('out')">
              ▼ Out
            </button>
          </div>
        </div>

        <div class="entry-form">
          <!-- Current balance -->
          <div class="bal-row">
            <span class="bal-lbl">Current balance</span>
            <span class="bal-num" :class="stockOnHand <= part.reorder_level ? 'text-red-600' : 'text-gray-900'">
              {{ stockOnHand }}
            </span>
          </div>

          <!-- Entry type -->
          <div class="ef">
            <label class="label">Movement Type <span class="req">*</span></label>
            <select v-model="entryType" class="input select-arrow">
              <option v-for="t in entryTypes" :key="t.value" :value="t.value">{{ t.label }}</option>
            </select>
          </div>

          <!-- Qty -->
          <div class="ef">
            <label class="label">Quantity <span class="req">*</span></label>
            <div class="qty-r">
              <button class="qb" @click="entryQty = Math.max(1, entryQty - 1)">−</button>
              <input v-model.number="entryQty" type="number" min="1" class="input text-center font-bold text-lg" />
              <button class="qb" @click="entryQty++">+</button>
            </div>
            <p class="preview" :class="entryMode === 'in' ? 'pv-in' : 'pv-out'">
              After: <strong>{{ entryMode === 'in' ? stockOnHand + entryQty : stockOnHand - entryQty }}</strong>
            </p>
          </div>

          <!-- Unit cost (only for stock-in) -->
          <div v-if="entryMode === 'in'" class="ef">
            <label class="label">Unit Cost (Rs.) <span class="label-opt">optional</span></label>
            <input v-model.number="entryUnit" type="number" min="0" step="10" class="input" placeholder="e.g. 850" />
          </div>

          <!-- Reference -->
          <div class="ef">
            <label class="label">Reference <span class="label-opt">PO / Job #</span></label>
            <input v-model="entryRef" type="text" class="input" placeholder="e.g. PO-0042" />
          </div>

          <!-- Note -->
          <div class="ef">
            <label class="label">Note</label>
            <textarea v-model="entryNote" rows="2" class="input" placeholder="Optional…" />
          </div>

          <p v-if="entryErr" class="text-red-600 text-sm font-medium">{{ entryErr }}</p>

          <button
            class="btn w-full"
            :class="entryMode === 'in' ? 'btn-success' : 'btn-danger'"
            :disabled="submitting || (entryMode === 'out' && stockOnHand === 0)"
            @click="submitEntry"
          >
            <svg v-if="submitting" class="w-4 h-4 spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            {{ submitting ? 'Saving…' : entryMode === 'in' ? '▲ Confirm Stock In' : '▼ Confirm Stock Out' }}
          </button>
        </div>
      </div>

      <!-- Description card -->
      <div v-if="part.description" class="desc-card">
        <p class="desc-title">Description</p>
        <p class="desc-body">{{ part.description }}</p>
      </div>
    </div>
  </div>

  <SparePartFormModal
    :open="showEdit"
    :part="part"
    :categories="categories"
    @close="showEdit = false"
    @saved="() => { showEdit = false; load() }"
  />
</template>

<style scoped>
.detail-layout { display: grid; grid-template-columns: 1fr 340px; gap: 1.5rem; align-items: start; }
@media (max-width: 900px) { .detail-layout { grid-template-columns: 1fr; } }

/* Info card */
.info-card { background: white; border-radius: 14px; border: 1px solid #e5e7eb; padding: 1.5rem; box-shadow: 0 1px 4px rgba(0,0,0,.05); display: flex; flex-direction: column; gap: 1rem; }
.info-head  { display: flex; align-items: flex-start; gap: 1rem; }
.info-sku   { font-size: .8125rem; font-family: ui-monospace,monospace; color: #9ca3af; margin-bottom: .2rem; }
.info-name  { font-size: 1.5rem; font-weight: 800; color: #111827; letter-spacing: -.02em; line-height: 1.2; }
.info-cat   { font-size: .875rem; color: #6b7280; margin-top: .2rem; }
.info-stock { text-align: right; flex-shrink: 0; }
.stock-big  { font-size: 2.5rem; font-weight: 900; line-height: 1; display: block; }
.stock-label{ font-size: .875rem; color: #6b7280; }
.low-warn   { display: block; font-size: .75rem; font-weight: 700; color: #dc2626; margin-top: .15rem; }
.stock-ok   { color: #111827; }
.stock-low  { color: #dc2626; }

.compat-row { display: flex; flex-wrap: wrap; gap: .4rem; }
.compat-chip { font-size: .8125rem; font-weight: 500; background: #f3f4f6; color: #374151; padding: .2rem .625rem; border-radius: 99px; }
.attr-chips { display: flex; flex-wrap: wrap; gap: .35rem; }
.attr-chip  { font-size: .75rem; font-weight: 700; padding: .2rem .6rem; border-radius: 99px; }
.chip-blue   { background: #dbeafe; color: #1d4ed8; }
.chip-gray   { background: #f3f4f6; color: #4b5563; }
.chip-green  { background: #dcfce7; color: #15803d; }
.chip-purple { background: #ede9fe; color: #6d28d9; }

.price-row  { display: flex; gap: 1.5rem; flex-wrap: wrap; }
.price-block{ display: flex; flex-direction: column; }
.price-lbl  { font-size: .7rem; font-weight: 700; text-transform: uppercase; letter-spacing: .07em; color: #9ca3af; }
.price-val  { font-size: 1.125rem; font-weight: 700; color: #111827; }
.info-actions { display: flex; gap: .5rem; }

/* KPIs */
.kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: .75rem; }
.kpi-box { background: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: .875rem 1rem; display: flex; flex-direction: column; gap: .2rem; box-shadow: 0 1px 3px rgba(0,0,0,.04); }
.kpi-label { font-size: .7rem; font-weight: 700; text-transform: uppercase; letter-spacing: .07em; color: #9ca3af; }
.kpi-val   { font-size: 1.5rem; font-weight: 800; color: #111827; font-variant-numeric: tabular-nums; }
.kpi-in  { border-top: 3px solid #22c55e; }
.kpi-out { border-top: 3px solid #ef4444; }

/* Ledger section */
.ledger-section { background: white; border: 1px solid #e5e7eb; border-radius: 14px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,.05); }
.ledger-hd  { display: flex; align-items: center; justify-content: space-between; padding: .875rem 1.25rem; background: #f9fafb; border-bottom: 1px solid #e5e7eb; }
.ledger-title { font-size: .875rem; font-weight: 800; color: #374151; text-transform: uppercase; letter-spacing: .07em; }
.export-btn { display: inline-flex; align-items: center; gap: .3rem; font-size: .8125rem; font-weight: 600; color: #6b7280; background: white; border: 1px solid #e5e7eb; border-radius: 7px; padding: .3rem .7rem; cursor: pointer; transition: all 120ms; }
.export-btn:hover { background: #f3f4f6; }
.ledger-wrap { max-height: 440px; overflow-y: auto; }
.ledger-tbl  { width: 100%; font-size: .875rem; border-collapse: collapse; }
.ledger-tbl thead tr { position: sticky; top: 0; background: #f9fafb; border-bottom: 2px solid #e5e7eb; }
.ledger-tbl thead th { padding: .5rem .875rem; font-size: .7rem; font-weight: 800; text-transform: uppercase; letter-spacing: .07em; color: #9ca3af; white-space: nowrap; }
.ledger-tbl tbody tr { border-bottom: 1px solid #f3f4f6; }
.ledger-tbl tbody tr:hover { background: #fafafa; }
.ledger-tbl tbody td { padding: .5rem .875rem; vertical-align: middle; }
.r        { text-align: right; }
.bold     { font-weight: 700; }
.tabular  { font-variant-numeric: tabular-nums; }
.mono-xs  { font-family: ui-monospace,monospace; font-size: .8125rem; }
.nowrap   { white-space: nowrap; }
.td-note  { max-width: 160px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.tr-out   { background: #fffafa; }
.type-tag { display: inline-flex; align-items: center; gap: .25rem; font-size: .75rem; font-weight: 700; padding: .15rem .5rem; border-radius: 6px; white-space: nowrap; }
.tag-in   { background: #dcfce7; color: #15803d; }
.tag-out  { background: #ffe4e6; color: #be123c; }
.ledger-empty { padding: 2.5rem; text-align: center; color: #9ca3af; font-size: .9375rem; }

/* Entry column */
.entry-col  { display: flex; flex-direction: column; gap: 1rem; }
.entry-card { background: white; border: 1px solid #e5e7eb; border-radius: 14px; padding: 1.25rem; box-shadow: 0 1px 4px rgba(0,0,0,.05); }
.entry-title-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; }
.entry-title { font-size: 1rem; font-weight: 800; color: #111827; }

.mode-toggle { display: flex; background: #f3f4f6; border-radius: 8px; padding: 3px; gap: 3px; }
.mtog { flex: 1; padding: .35rem .6rem; border-radius: 6px; border: none; font-size: .8125rem; font-weight: 700; cursor: pointer; background: transparent; color: #6b7280; transition: all 120ms; }
.mtog:disabled { opacity: .35; cursor: not-allowed; }
.mtog-in  { background: white; color: #15803d; box-shadow: 0 1px 4px rgba(0,0,0,.1); }
.mtog-out { background: white; color: #be123c; box-shadow: 0 1px 4px rgba(0,0,0,.1); }

.entry-form { display: flex; flex-direction: column; gap: .875rem; }
.ef         { display: flex; flex-direction: column; gap: .3rem; }
.bal-row    { display: flex; align-items: center; justify-content: space-between; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px; padding: .625rem .875rem; }
.bal-lbl    { font-size: .8125rem; font-weight: 600; color: #6b7280; }
.bal-num    { font-size: 1.5rem; font-weight: 900; }
.qty-r      { display: flex; align-items: center; gap: .5rem; }
.qb         { width: 38px; height: 38px; border-radius: 9px; border: 1.5px solid #e5e7eb; background: white; font-size: 1.25rem; font-weight: 700; cursor: pointer; transition: all 120ms; }
.qb:hover   { border-color: #e11d48; color: #e11d48; }
.preview    { font-size: .875rem; font-weight: 500; margin-top: .25rem; }
.pv-in      { color: #15803d; }
.pv-out     { color: #be123c; }
.req        { color: #e11d48; }
.label-opt  { font-weight: 400; color: #9ca3af; font-size: .8125rem; margin-left: .25rem; }

.desc-card  { background: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: 1.125rem; }
.desc-title { font-size: .75rem; font-weight: 700; text-transform: uppercase; letter-spacing: .07em; color: #9ca3af; margin-bottom: .5rem; }
.desc-body  { font-size: .9375rem; color: #374151; line-height: 1.6; }

@keyframes spin { to { transform: rotate(360deg); } }
.spin { animation: spin .7s linear infinite; }
</style>
