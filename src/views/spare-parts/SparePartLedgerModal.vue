<script setup>
/**
 * SparePartLedgerModal — displays the full immutable stock ledger for one part.
 * Every row is a ledger entry (IN or OUT). Running balance is shown per row.
 * Fully reconstructible: balance at any row = SUM(qty) of all rows above.
 */
import { ref, watch, computed } from 'vue'
import { sparePartsApi } from '@/api/spareParts'
import AppModal from '@/components/ui/AppModal.vue'
import AppButton from '@/components/ui/AppButton.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'

const props = defineProps({
  open: { type: Boolean, required: true },
  part: { type: Object,  default: null  },
})
const emit = defineEmits(['close'])

const entries   = ref([])
const loading   = ref(false)
const totalIn   = computed(() => entries.value.reduce((s, e) => e.qty > 0 ? s + e.qty : s, 0))
const totalOut  = computed(() => entries.value.reduce((s, e) => e.qty < 0 ? s + Math.abs(e.qty) : s, 0))
const balance   = computed(() => totalIn.value - totalOut.value)

const entryTypeLabels = {
  opening_balance: 'Opening Balance',
  purchase:        'Purchase',
  repair_use:      'Used in Repair',
  sale:            'Sale',
  return_in:       'Return In',
  return_out:      'Return to Supplier',
  adjustment_in:   'Adjustment In',
  adjustment_out:  'Adjustment Out',
  transfer_in:     'Transfer In',
  transfer_out:    'Transfer Out',
  damaged:         'Damaged / Write-Off',
  testing:         'Testing / Demo',
}

watch(() => props.open, async (v) => {
  if (v && props.part?.id) {
    loading.value = true
    try {
      const { data } = await sparePartsApi.ledger(props.part.id)
      entries.value = Array.isArray(data) ? data : (data.results || [])
    } finally { loading.value = false }
  } else {
    entries.value = []
  }
})

function fmtDate(iso) {
  return new Date(iso).toLocaleString('en-PK', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

// CSV export of the full ledger
function exportCsv() {
  const rows = [
    ['Date', 'Type', 'Qty', 'Balance After', 'Unit Cost', 'Reference', 'Note', 'Actor'],
    ...entries.value.map(e => [
      fmtDate(e.created_at),
      entryTypeLabels[e.entry_type] || e.entry_type,
      e.qty,
      e.balance_after,
      e.unit_cost ?? '',
      e.reference ?? '',
      e.note ?? '',
      e.actor_name ?? '',
    ]),
  ]
  const csv  = rows.map(r => r.map(v => `"${String(v).replace(/"/g, '""')}"`).join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href     = url
  a.download = `ledger-${props.part?.sku}-${new Date().toISOString().slice(0,10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <AppModal
    :open="open"
    :title="part ? `Ledger — ${part.name}` : 'Ledger'"
    size="xl"
    @close="emit('close')"
  >
    <!-- Summary strip -->
    <div v-if="part" class="summary-strip">
      <div class="summ-item">
        <span class="summ-label">SKU</span>
        <span class="summ-val font-mono">{{ part.sku }}</span>
      </div>
      <div class="summ-item">
        <span class="summ-label">Total In</span>
        <span class="summ-val text-green-700">+{{ totalIn }}</span>
      </div>
      <div class="summ-item">
        <span class="summ-label">Total Out</span>
        <span class="summ-val text-red-600">−{{ totalOut }}</span>
      </div>
      <div class="summ-item">
        <span class="summ-label">Balance</span>
        <span class="summ-val font-extrabold" :class="balance <= (part.reorder_level || 3) ? 'text-red-600' : 'text-gray-900'">
          {{ balance }}
        </span>
      </div>
      <div class="summ-item">
        <span class="summ-label">Entries</span>
        <span class="summ-val">{{ entries.length }}</span>
      </div>
    </div>

    <!-- Ledger table -->
    <div class="ledger-wrap">
      <div v-if="loading" class="ledger-loading">
        <svg class="w-6 h-6 spin text-gray-300" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
        </svg>
      </div>

      <table v-else-if="entries.length" class="ledger-table">
        <thead>
          <tr>
            <th>Date & Time</th>
            <th>Entry Type</th>
            <th class="text-right">Qty</th>
            <th class="text-right">Balance After</th>
            <th class="text-right">Unit Cost</th>
            <th>Reference</th>
            <th>Note</th>
            <th>By</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="entry in entries"
            :key="entry.id"
            :class="entry.qty > 0 ? 'row-in' : 'row-out'"
          >
            <td class="mono-sm text-gray-500">{{ fmtDate(entry.created_at) }}</td>
            <td>
              <span class="type-badge" :class="entry.qty > 0 ? 'type-in' : 'type-out'">
                {{ entry.qty > 0 ? '▲' : '▼' }}
                {{ entryTypeLabels[entry.entry_type] || entry.entry_type }}
              </span>
            </td>
            <td class="text-right font-bold" :class="entry.qty > 0 ? 'text-green-700' : 'text-red-600'">
              {{ entry.qty > 0 ? '+' : '' }}{{ entry.qty }}
            </td>
            <td class="text-right font-extrabold tabular-nums">{{ entry.balance_after }}</td>
            <td class="text-right text-gray-500">
              <span v-if="entry.unit_cost">Rs. {{ Number(entry.unit_cost).toLocaleString() }}</span>
              <span v-else class="text-gray-300">—</span>
            </td>
            <td class="mono-sm text-gray-600">{{ entry.reference || '—' }}</td>
            <td class="text-gray-600" style="max-width:180px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap">
              {{ entry.note || '—' }}
            </td>
            <td class="text-gray-500 text-sm">{{ entry.actor_name || 'system' }}</td>
          </tr>
        </tbody>
      </table>

      <div v-else class="ledger-empty">
        <svg class="w-10 h-10 mx-auto text-gray-300 mb-2" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
        </svg>
        <p class="text-gray-500">No ledger entries yet. Use Stock In / Stock Out to record movements.</p>
      </div>
    </div>

    <template #footer>
      <AppButton v-if="entries.length" variant="secondary" @click="exportCsv">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
        </svg>
        Export CSV
      </AppButton>
      <AppButton variant="primary" @click="emit('close')">Close</AppButton>
    </template>
  </AppModal>
</template>

<style scoped>
/* Summary */
.summary-strip {
  display: flex; gap: 2rem; flex-wrap: wrap;
  background: #f9fafb; border: 1px solid #e5e7eb;
  border-radius: 10px; padding: .875rem 1.25rem;
  margin-bottom: 1rem;
}
.summ-item  { display: flex; flex-direction: column; gap: .15rem; }
.summ-label { font-size: .7rem; font-weight: 700; text-transform: uppercase; letter-spacing: .07em; color: #9ca3af; }
.summ-val   { font-size: 1.125rem; font-weight: 700; color: #111827; font-variant-numeric: tabular-nums; }

/* Ledger table */
.ledger-wrap {
  max-height: 480px; overflow-y: auto;
  border: 1px solid #e5e7eb; border-radius: 10px;
}
.ledger-loading {
  display: flex; align-items: center; justify-content: center;
  padding: 3rem; color: #9ca3af;
}
.ledger-table {
  width: 100%; font-size: .875rem; border-collapse: collapse;
}
.ledger-table thead tr {
  position: sticky; top: 0; z-index: 1;
  background: #f9fafb; border-bottom: 2px solid #e5e7eb;
}
.ledger-table thead th {
  padding: .625rem 1rem; text-align: left;
  font-size: .7rem; font-weight: 800; text-transform: uppercase;
  letter-spacing: .07em; color: #9ca3af; white-space: nowrap;
}
.ledger-table tbody tr { border-bottom: 1px solid #f3f4f6; transition: background 80ms; }
.ledger-table tbody tr:hover { background: #fafafa; }
.ledger-table tbody td { padding: .625rem 1rem; vertical-align: middle; }

.row-in  { }
.row-out { background: #fffafa; }

.type-badge {
  display: inline-flex; align-items: center; gap: .3rem;
  font-size: .8rem; font-weight: 700; padding: .15rem .5rem;
  border-radius: 6px; white-space: nowrap;
}
.type-in  { background: #dcfce7; color: #15803d; }
.type-out { background: #ffe4e6; color: #be123c; }

.mono-sm { font-family: ui-monospace, monospace; font-size: .8125rem; }
.tabular-nums { font-variant-numeric: tabular-nums; }

.ledger-empty { padding: 3rem; text-align: center; }

@keyframes spin { to { transform: rotate(360deg); } }
.spin { animation: spin .7s linear infinite; }
</style>
