<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { sparePartsApi } from '@/api/spareParts'
import { useUiStore } from '@/stores/ui'
import { usePagination } from '@/composables/usePagination'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import AppPagination from '@/components/ui/AppPagination.vue'
import SparePartFormModal from './SparePartFormModal.vue'
import SparePartLedgerModal from './SparePartLedgerModal.vue'

const router = useRouter()
const ui     = useUiStore()
const pg     = usePagination({ pageSize: 30 })

const parts       = ref([])
const categories  = ref([])
const loading     = ref(false)
const search      = ref('')
const activeCategory = ref('')
const showLowStock   = ref(false)

// Modals
const showForm   = ref(false)
const editPart   = ref(null)
const showLedger = ref(false)
const ledgerPart = ref(null)

// Category icon map
const catIcons = {
  display_panel:  '📱',
  oca_glass:      '🔳',
  battery:        '🔋',
  charging_flex:  '⚡',
  body_frame:     '🏗️',
  camera_module:  '📷',
}

const catColors = {
  display_panel:  'cat-blue',
  oca_glass:      'cat-cyan',
  battery:        'cat-green',
  charging_flex:  'cat-yellow',
  body_frame:     'cat-orange',
  camera_module:  'cat-purple',
}

async function loadCategories() {
  const { data } = await sparePartsApi.categories()
  categories.value = data
}

async function load() {
  loading.value = true
  try {
    const params = {
      search:   search.value   || undefined,
      category: activeCategory.value || undefined,
      low_stock: showLowStock.value ? 'true' : undefined,
      ...pg.queryParams.value,
    }
    const { data } = await sparePartsApi.list(params)
    parts.value = Array.isArray(data) ? data : (data.results || [])
    pg.setFromResponse({ count: Array.isArray(data) ? data.length : (data.count || 0) })
  } finally { loading.value = false }
}

watch([search, activeCategory, showLowStock, () => pg.currentPage.value], load)
onMounted(() => { loadCategories(); load() })

// Stock-in / out quick entry
const showEntry   = ref(false)
const entryPart   = ref(null)
const entryMode   = ref('in')   // 'in' | 'out'
const entryQty    = ref(1)
const entryType   = ref('')
const entryRef    = ref('')
const entryNote   = ref('')
const submitting  = ref(false)
const entryError  = ref('')

const inTypes  = [
  { value: 'purchase',        label: 'Purchase / Stock-In' },
  { value: 'opening_balance', label: 'Opening Balance'     },
  { value: 'return_in',       label: 'Return from Tech'    },
  { value: 'adjustment_in',   label: 'Manual Adjustment'   },
  { value: 'transfer_in',     label: 'Transfer In'         },
]
const outTypes = [
  { value: 'repair_use',      label: 'Used in Repair'      },
  { value: 'sale',            label: 'Sold to Customer'    },
  { value: 'damaged',         label: 'Damaged / Written-Off'},
  { value: 'testing',         label: 'Used for Testing'    },
  { value: 'adjustment_out',  label: 'Manual Adjustment'   },
  { value: 'return_out',      label: 'Returned to Supplier'},
  { value: 'transfer_out',    label: 'Transfer Out'        },
]

const entryTypes = computed(() => entryMode.value === 'in' ? inTypes : outTypes)

function openEntry(part, mode) {
  entryPart.value  = part
  entryMode.value  = mode
  entryQty.value   = 1
  entryType.value  = entryTypes.value[0]?.value || ''
  entryRef.value   = ''
  entryNote.value  = ''
  entryError.value = ''
  showEntry.value  = true
}

async function submitEntry() {
  if (!entryType.value)      { entryError.value = 'Select an entry type.'; return }
  if (entryQty.value < 1)    { entryError.value = 'Qty must be at least 1.'; return }
  submitting.value = true
  entryError.value = ''
  try {
    const payload = {
      entry_type: entryType.value,
      qty:        entryQty.value,
      reference:  entryRef.value,
      note:       entryNote.value,
    }
    if (entryMode.value === 'in') {
      await sparePartsApi.stockIn(entryPart.value.id, payload)
    } else {
      await sparePartsApi.stockOut(entryPart.value.id, payload)
    }
    ui.toastSuccess?.(`Stock ${entryMode.value === 'in' ? 'in' : 'out'} recorded.`)
    showEntry.value = false
    load()
  } catch (e) {
    entryError.value = e.displayMessage || e.response?.data?.detail || 'Failed.'
  } finally { submitting.value = false }
}

function openNew()   { editPart.value = null;  showForm.value  = true }
function openEdit(p) { editPart.value = p;     showForm.value  = true }
function openLedger(p) { ledgerPart.value = p; showLedger.value = true }
function onSaved()   { showForm.value  = false; load() }
</script>

<template>
  <div class="sp-page">

    <!-- ── Page header ──────────────────────────────────────────────────── -->
    <div class="sp-header">
      <div>
        <h1 class="page-title">Spare Parts Catalog</h1>
        <p class="page-subtitle">Hardware components — ledger-based stock tracking</p>
      </div>
      <button class="btn btn-primary" @click="openNew">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
        </svg>
        Add Part
      </button>
    </div>

    <!-- ── Category filter pills ────────────────────────────────────────── -->
    <div class="cat-bar">
      <button
        class="cat-pill"
        :class="activeCategory === '' ? 'cat-active' : ''"
        @click="activeCategory = ''"
      >All Categories</button>
      <button
        v-for="cat in categories"
        :key="cat.value"
        class="cat-pill"
        :class="[catColors[cat.value] || '', activeCategory === cat.value ? 'cat-active' : '']"
        @click="activeCategory = activeCategory === cat.value ? '' : cat.value"
      >
        <span>{{ catIcons[cat.value] || '📦' }}</span>
        {{ cat.label }}
      </button>
    </div>

    <!-- ── Search + toggles ──────────────────────────────────────────────── -->
    <div class="sp-toolbar">
      <div class="search-wrap">
        <svg class="search-ico" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <input v-model="search" type="search" class="input pl-9 w-64" placeholder="Search SKU, name, brand, model…" />
      </div>
      <label class="low-stock-toggle">
        <input v-model="showLowStock" type="checkbox" class="sr-only" />
        <span class="toggle-track" :class="showLowStock ? 'track-on' : ''">
          <span class="toggle-thumb" :class="showLowStock ? 'thumb-on' : ''" />
        </span>
        <span class="text-sm font-medium text-gray-700">Low stock only</span>
      </label>
      <span class="flex-1" />
      <span class="count-badge">{{ parts.length }} part{{ parts.length !== 1 ? 's' : '' }}</span>
    </div>

    <!-- ── Parts grid ────────────────────────────────────────────────────── -->
    <div v-if="loading" class="parts-grid">
      <div v-for="n in 12" :key="n" class="skeleton h-48 rounded-xl" />
    </div>

    <div v-else-if="parts.length" class="parts-grid">
      <div
        v-for="part in parts"
        :key="part.id"
        class="part-card"
        :class="part.low_stock ? 'card-low' : ''"
      >
        <!-- Category stripe -->
        <div class="card-stripe" :class="catColors[part.category] || 'cat-blue'" />

        <!-- Header -->
        <div class="card-head">
          <div class="cat-badge" :class="catColors[part.category] || 'cat-blue'">
            {{ catIcons[part.category] || '📦' }} {{ part.category_display }}
          </div>
          <div v-if="part.low_stock" class="low-badge">⚠ Low</div>
        </div>

        <!-- Name + SKU -->
        <div
          class="card-name cursor-pointer"
          @click="router.push(`/spare-parts/${part.id}`)"
        >{{ part.name }}</div>
        <div class="card-sku">{{ part.sku }}</div>

        <!-- Compat info -->
        <div v-if="part.brand_compat" class="card-compat">
          {{ part.brand_compat }}
          <span v-if="part.model_compat"> · {{ part.model_compat }}</span>
        </div>

        <!-- Attribute chips -->
        <div class="card-chips">
          <span v-if="part.display_type && part.display_type !== 'N/A'" class="chip chip-blue">
            {{ part.display_type }}
          </span>
          <span v-if="part.with_frame" class="chip chip-gray">With Frame</span>
          <span v-if="part.battery_capacity" class="chip chip-green">
            {{ part.battery_capacity }} mAh
          </span>
          <span v-if="part.camera_position && part.camera_position !== 'N/A'" class="chip chip-purple">
            {{ part.camera_position === 'front' ? 'Front' : part.camera_position === 'rear' ? 'Rear' : 'Front+Rear' }}
          </span>
        </div>

        <!-- Stock counter -->
        <div class="card-stock" :class="part.low_stock ? 'stock-low' : 'stock-ok'">
          <span class="stock-num">{{ part.stock_on_hand }}</span>
          <span class="stock-label">in stock</span>
          <span class="stock-reorder">reorder @ {{ part.reorder_level }}</span>
        </div>

        <!-- Price row -->
        <div class="card-price">
          <div>
            <span class="price-label">Cost</span>
            <MoneyDisplay :value="part.cost_price" class="price-val" />
          </div>
          <div>
            <span class="price-label">Sell</span>
            <MoneyDisplay :value="part.sell_price" class="price-val price-sell" />
          </div>
        </div>

        <!-- Actions -->
        <div class="card-actions">
          <button class="act-btn act-in"  @click="openEntry(part, 'in')">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
            </svg>
            Stock In
          </button>
          <button class="act-btn act-out" :disabled="part.stock_on_hand === 0" @click="openEntry(part, 'out')">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M20 12H4"/>
            </svg>
            Stock Out
          </button>
          <button class="act-btn act-ledger" @click="openLedger(part)">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
            </svg>
            Ledger
          </button>
          <button class="act-btn act-edit" @click="openEdit(part)">Edit</button>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <svg class="w-12 h-12 mx-auto text-gray-300 mb-3" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
      </svg>
      <p class="text-gray-500 font-medium">No spare parts found.</p>
      <button class="btn btn-primary mt-3" @click="openNew">Add your first part</button>
    </div>

    <AppPagination
      :current-page="pg.currentPage.value"
      :total-pages="pg.totalPages.value"
      :total-count="pg.totalCount.value"
      :page-size="pg.pageSize.value"
      @page="pg.goTo"
    />

    <!-- ── Quick stock entry panel ───────────────────────────────────────── -->
    <Teleport to="body">
      <Transition name="panel-slide">
        <div v-if="showEntry" class="entry-backdrop" @click.self="showEntry = false">
          <div class="entry-panel">
            <div class="entry-head">
              <div>
                <h3 class="entry-title">
                  {{ entryMode === 'in' ? '📥 Stock In' : '📤 Stock Out' }}
                </h3>
                <p class="entry-part">{{ entryPart?.name }} · {{ entryPart?.sku }}</p>
              </div>
              <button class="entry-close" @click="showEntry = false">✕</button>
            </div>

            <div class="entry-body space-y-4">
              <!-- Mode toggle -->
              <div class="mode-toggle">
                <button
                  class="mode-btn"
                  :class="entryMode === 'in' ? 'mode-active-in' : ''"
                  @click="entryMode = 'in'; entryType = inTypes[0].value"
                >📥 Stock In</button>
                <button
                  class="mode-btn"
                  :class="entryMode === 'out' ? 'mode-active-out' : ''"
                  :disabled="entryPart?.stock_on_hand === 0"
                  @click="entryMode = 'out'; entryType = outTypes[0].value"
                >📤 Stock Out</button>
              </div>

              <!-- Current balance -->
              <div class="balance-strip">
                <span class="bal-label">Current balance</span>
                <span class="bal-val">{{ entryPart?.stock_on_hand ?? 0 }} units</span>
              </div>

              <!-- Entry type -->
              <div>
                <label class="label">Entry Type <span class="text-red-500">*</span></label>
                <select v-model="entryType" class="input select-arrow">
                  <option v-for="t in entryTypes" :key="t.value" :value="t.value">{{ t.label }}</option>
                </select>
              </div>

              <!-- Qty -->
              <div>
                <label class="label">Quantity <span class="text-red-500">*</span></label>
                <div class="qty-row">
                  <button class="qty-btn" @click="entryQty = Math.max(1, entryQty - 1)">−</button>
                  <input v-model.number="entryQty" type="number" min="1" class="input text-center font-bold" />
                  <button class="qty-btn" @click="entryQty++">+</button>
                </div>
                <!-- Preview -->
                <p v-if="entryQty > 0" class="preview-line" :class="entryMode === 'in' ? 'text-green-700' : 'text-red-600'">
                  Balance after: <strong>
                    {{ entryMode === 'in'
                      ? (entryPart?.stock_on_hand || 0) + entryQty
                      : (entryPart?.stock_on_hand || 0) - entryQty }}
                  </strong>
                </p>
              </div>

              <!-- Reference -->
              <div>
                <label class="label">Reference <span class="label-optional">(PO/Job #)</span></label>
                <input v-model="entryRef" type="text" class="input" placeholder="e.g. PO-0042, JOB-0018" />
              </div>

              <!-- Note -->
              <div>
                <label class="label">Note</label>
                <textarea v-model="entryNote" rows="2" class="input" placeholder="Optional details…" />
              </div>

              <p v-if="entryError" class="text-red-600 text-sm font-medium">{{ entryError }}</p>
            </div>

            <div class="entry-footer">
              <button class="btn btn-secondary" @click="showEntry = false">Cancel</button>
              <button
                class="btn"
                :class="entryMode === 'in' ? 'btn-success' : 'btn-danger'"
                :disabled="submitting"
                @click="submitEntry"
              >
                <svg v-if="submitting" class="w-4 h-4 spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                {{ submitting ? 'Saving…' : entryMode === 'in' ? 'Confirm Stock In' : 'Confirm Stock Out' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Form + Ledger modals -->
    <SparePartFormModal
      :open="showForm"
      :part="editPart"
      :categories="categories"
      @close="showForm = false"
      @saved="onSaved"
    />
    <SparePartLedgerModal
      :open="showLedger"
      :part="ledgerPart"
      @close="showLedger = false"
    />
  </div>
</template>

<style scoped>
.sp-page   { display: flex; flex-direction: column; gap: 1.25rem; }
.sp-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }

/* Category bar */
.cat-bar { display: flex; flex-wrap: wrap; gap: .5rem; }
.cat-pill {
  display: inline-flex; align-items: center; gap: .35rem;
  padding: .4rem .875rem; border-radius: 99px;
  border: 1.5px solid #e5e7eb; background: white;
  font-size: .875rem; font-weight: 500; color: #374151;
  cursor: pointer; transition: all 120ms; white-space: nowrap;
}
.cat-pill:hover { border-color: #9ca3af; background: #f9fafb; }
.cat-active     { font-weight: 700; }

.cat-blue   { border-color: #bfdbfe !important; background: #eff6ff !important; color: #1d4ed8 !important; }
.cat-cyan   { border-color: #a5f3fc !important; background: #ecfeff !important; color: #0e7490 !important; }
.cat-green  { border-color: #bbf7d0 !important; background: #f0fdf4 !important; color: #15803d !important; }
.cat-yellow { border-color: #fde68a !important; background: #fffbeb !important; color: #92400e !important; }
.cat-orange { border-color: #fed7aa !important; background: #fff7ed !important; color: #c2410c !important; }
.cat-purple { border-color: #ddd6fe !important; background: #f5f3ff !important; color: #6d28d9 !important; }

/* Toolbar */
.sp-toolbar   { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; }
.search-wrap  { position: relative; }
.search-ico   { position: absolute; left: .75rem; top: 50%; transform: translateY(-50%); width: 16px; height: 16px; color: #9ca3af; pointer-events: none; }
.low-stock-toggle { display: flex; align-items: center; gap: .5rem; cursor: pointer; }
.toggle-track { width: 36px; height: 20px; border-radius: 99px; background: #d1d5db; position: relative; transition: background 150ms; }
.track-on     { background: #e11d48; }
.toggle-thumb { position: absolute; width: 14px; height: 14px; border-radius: 50%; background: white; top: 3px; left: 3px; transition: left 150ms; box-shadow: 0 1px 3px rgba(0,0,0,.2); }
.thumb-on     { left: 19px; }
.count-badge  { font-size: .875rem; color: #6b7280; font-weight: 500; }

/* Parts grid */
.parts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

/* Part card */
.part-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 1.125rem;
  display: flex; flex-direction: column; gap: .625rem;
  box-shadow: 0 1px 4px rgba(0,0,0,.05);
  transition: all 200ms;
  position: relative; overflow: hidden;
}
.part-card:hover { box-shadow: 0 6px 20px rgba(0,0,0,.09); transform: translateY(-2px); }
.card-low        { border-color: #fca5a5; background: #fff9f9; }

.card-stripe { position: absolute; top: 0; left: 0; right: 0; height: 3px; }
.cat-blue.card-stripe   { background: #3b82f6; }
.cat-cyan.card-stripe   { background: #06b6d4; }
.cat-green.card-stripe  { background: #22c55e; }
.cat-yellow.card-stripe { background: #f59e0b; }
.cat-orange.card-stripe { background: #f97316; }
.cat-purple.card-stripe { background: #8b5cf6; }

.card-head  { display: flex; align-items: center; justify-content: space-between; margin-top: .25rem; }
.cat-badge  {
  font-size: .7rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: .04em; padding: .2rem .5rem; border-radius: 6px;
}
.low-badge  { font-size: .7rem; font-weight: 800; color: #dc2626; background: #fee2e2; padding: .2rem .5rem; border-radius: 6px; }
.card-name  { font-size: 1rem; font-weight: 700; color: #111827; line-height: 1.3; }
.card-sku   { font-size: .8125rem; color: #9ca3af; font-family: ui-monospace, monospace; }
.card-compat { font-size: .8125rem; color: #6b7280; }
.card-chips { display: flex; flex-wrap: wrap; gap: .3rem; }
.chip       { font-size: .7rem; font-weight: 600; padding: .15rem .5rem; border-radius: 99px; }
.chip-blue   { background: #dbeafe; color: #1d4ed8; }
.chip-gray   { background: #f3f4f6; color: #4b5563; }
.chip-green  { background: #dcfce7; color: #15803d; }
.chip-purple { background: #ede9fe; color: #6d28d9; }

.card-stock  { display: flex; align-items: baseline; gap: .4rem; }
.stock-num   { font-size: 1.75rem; font-weight: 900; line-height: 1; }
.stock-label { font-size: .875rem; font-weight: 500; }
.stock-reorder { font-size: .75rem; color: #9ca3af; margin-left: auto; }
.stock-ok    { color: #111827; }
.stock-low   { color: #dc2626; }

.card-price  { display: flex; gap: 1.5rem; }
.price-label { font-size: .7rem; font-weight: 700; text-transform: uppercase; letter-spacing: .06em; color: #9ca3af; display: block; }
.price-val   { font-size: .9375rem; font-weight: 700; color: #374151; display: block; }
.price-sell  { color: #e11d48; }

.card-actions { display: flex; gap: .375rem; flex-wrap: wrap; margin-top: .25rem; }
.act-btn {
  flex: 1; min-width: 0; display: inline-flex; align-items: center; justify-content: center; gap: .25rem;
  padding: .4rem .5rem; border-radius: 8px; font-size: .8125rem; font-weight: 600;
  border: 1.5px solid; cursor: pointer; transition: all 120ms; white-space: nowrap;
}
.act-btn:disabled { opacity: .35; cursor: not-allowed; }
.act-in     { background: #f0fdf4; border-color: #bbf7d0; color: #15803d; }
.act-in:hover:not(:disabled) { background: #dcfce7; }
.act-out    { background: #fff1f2; border-color: #fecdd3; color: #be123c; }
.act-out:hover:not(:disabled) { background: #ffe4e6; }
.act-ledger { background: #f5f3ff; border-color: #ddd6fe; color: #6d28d9; }
.act-ledger:hover { background: #ede9fe; }
.act-edit   { background: #f9fafb; border-color: #e5e7eb; color: #374151; }
.act-edit:hover { background: #f3f4f6; }

/* Empty state */
.empty-state { text-align: center; padding: 4rem 0; }

/* Entry panel */
.entry-backdrop {
  position: fixed; inset: 0; background: rgba(0,0,0,.45);
  z-index: 500; display: flex; justify-content: flex-end;
}
.entry-panel {
  width: 420px; max-width: 100vw; height: 100%;
  background: white; display: flex; flex-direction: column;
  box-shadow: -8px 0 32px rgba(0,0,0,.15);
}
.entry-head  { display: flex; align-items: flex-start; justify-content: space-between; padding: 1.5rem 1.5rem 1rem; border-bottom: 1px solid #e5e7eb; }
.entry-title { font-size: 1.25rem; font-weight: 800; color: #111827; }
.entry-part  { font-size: .875rem; color: #6b7280; margin-top: .25rem; }
.entry-close { width: 32px; height: 32px; border-radius: 8px; border: none; background: #f3f4f6; cursor: pointer; font-size: 1rem; color: #374151; }
.entry-body  { flex: 1; overflow-y: auto; padding: 1.25rem 1.5rem; }
.entry-footer { padding: 1rem 1.5rem; border-top: 1px solid #e5e7eb; display: flex; gap: .75rem; }

.mode-toggle { display: flex; background: #f3f4f6; border-radius: 10px; padding: 3px; gap: 3px; }
.mode-btn    { flex: 1; padding: .4rem; border-radius: 7px; border: none; font-size: .875rem; font-weight: 600; cursor: pointer; transition: all 120ms; background: transparent; color: #6b7280; }
.mode-active-in  { background: white; color: #15803d; box-shadow: 0 1px 4px rgba(0,0,0,.1); }
.mode-active-out { background: white; color: #be123c; box-shadow: 0 1px 4px rgba(0,0,0,.1); }

.balance-strip { display: flex; align-items: center; justify-content: space-between; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px; padding: .75rem 1rem; }
.bal-label     { font-size: .8125rem; font-weight: 600; color: #6b7280; }
.bal-val       { font-size: 1.25rem; font-weight: 800; color: #111827; }

.qty-row     { display: flex; align-items: center; gap: .5rem; }
.qty-btn     { width: 40px; height: 40px; border-radius: 10px; border: 1.5px solid #e5e7eb; background: white; font-size: 1.25rem; font-weight: 700; cursor: pointer; transition: all 120ms; }
.qty-btn:hover { border-color: #e11d48; color: #e11d48; }
.preview-line { font-size: .875rem; margin-top: .375rem; }
.label-optional { font-weight: 400; color: #9ca3af; font-size: .8125rem; }

/* Panel slide animation */
.panel-slide-enter-active { transition: transform 250ms ease; }
.panel-slide-leave-active { transition: transform 200ms ease; }
.panel-slide-enter-from .entry-panel,
.panel-slide-leave-to   .entry-panel { transform: translateX(100%); }

@keyframes spin { to { transform: rotate(360deg); } }
.spin { animation: spin .7s linear infinite; }
</style>
