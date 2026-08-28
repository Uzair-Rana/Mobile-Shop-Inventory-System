<script setup>
/**
 * InvoiceDetailView
 * ─ Finalized invoices: no edit affordance. Only Return / Void flows.
 * ─ Draft invoices: show edit option.
 * ─ All destructive actions state their financial/inventory effect before commit.
 */
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { salesApi } from '@/api/sales'
import { useUiStore } from '@/stores/ui'
import { useConfirm } from '@/composables/useConfirm'
import { usePermissions } from '@/composables/usePermissions'
import { formatDate, formatDateTime } from '@/utils/date'
import { formatMoney } from '@/utils/money'
import { INVOICE_STATUS } from '@/utils/constants'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppInput from '@/components/ui/AppInput.vue'

const route  = useRoute()
const router = useRouter()
const ui     = useUiStore()
const { confirm } = useConfirm()
const perms  = usePermissions()

const invoice  = ref(null)
const loading  = ref(true)

const isFinalized = computed(() => ['finalized','paid','partially_paid'].includes(invoice.value?.status))
const isVoided    = computed(() => invoice.value?.status === 'voided')
const isReturned  = computed(() => invoice.value?.status === 'returned')
const isEditable  = computed(() => invoice.value?.status === 'draft')

// Return flow
const showReturnModal = ref(false)
const returnReason    = ref('')
const returnLines     = ref([])
const returning       = ref(false)

// Void flow
const voidReason = ref('')
const voiding    = ref(false)

onMounted(async () => {
  const res     = await salesApi.getInvoice(route.params.id)
  invoice.value = res.data
  loading.value = false
  returnLines.value = (res.data.lines || []).map(l => ({ ...l, return_qty: 0 }))
})

function statusObj(val) {
  return Object.values(INVOICE_STATUS).find(s => s.value === val) || { label: val, badge: 'badge-gray' }
}

// ── Void invoice ──────────────────────────────────────────────────────────────
async function handleVoid() {
  const lines  = invoice.value.lines || []
  const units  = lines.filter(l => l.type === 'unit').length
  const effect = [
    units > 0 ? `Restocks ${units} device unit(s) back to inventory.` : '',
    `Reverses sale amount of ${formatMoney(invoice.value.grand_total)}.`,
    'This cannot be undone.',
  ].filter(Boolean).join(' ')

  const ok = await confirm({
    title: `Void Invoice #${invoice.value.invoice_number}`,
    message: 'This will cancel the entire sale.',
    effect,
    confirmLabel: 'Void Invoice',
    confirmClass: 'btn-danger',
  })
  if (!ok) return

  voiding.value = true
  try {
    await salesApi.voidInvoice(invoice.value.id, { reason: voidReason.value })
    ui.toastSuccess('Invoice voided')
    const res = await salesApi.getInvoice(invoice.value.id)
    invoice.value = res.data
  } catch (e) {
    ui.toastError(e.displayMessage || 'Void failed')
  } finally { voiding.value = false }
}

// ── Return ────────────────────────────────────────────────────────────────────
async function handleReturn() {
  const returnItems = returnLines.value.filter(l => l.return_qty > 0)
  if (returnItems.length === 0) { ui.toastWarn('Select at least one item to return'); return }

  const refundTotal = returnItems.reduce((sum, l) => sum + (l.unit_price * l.return_qty), 0)
  const effect      = `Restocks ${returnItems.length} line(s) and refunds ${formatMoney(refundTotal)} to the customer.`

  const ok = await confirm({
    title:  `Return Items — Invoice #${invoice.value.invoice_number}`,
    message: 'The selected items will be returned and inventory restocked.',
    effect,
    confirmLabel: 'Process Return',
    confirmClass: 'btn-danger',
  })
  if (!ok) return

  returning.value = true
  try {
    await salesApi.returnInvoice(invoice.value.id, {
      lines: returnItems.map(l => ({ line_id: l.id, qty: l.return_qty })),
    })
    ui.toastSuccess('Return processed')
    showReturnModal.value = false
    const res = await salesApi.getInvoice(invoice.value.id)
    invoice.value = res.data
  } catch (e) {
    ui.toastError(e.displayMessage || 'Return failed')
  } finally { returning.value = false }
}
</script>

<template>
  <div v-if="!loading && invoice" class="space-y-6 max-w-4xl">
    <!-- Header -->
    <div class="flex items-start gap-4 flex-wrap">
      <div class="flex-1">
        <div class="flex items-center gap-3">
          <h2 class="text-xl font-bold text-gray-900">Invoice #{{ invoice.invoice_number }}</h2>
          <AppBadge :status="statusObj(invoice.status)" />
        </div>
        <p class="text-sm text-gray-500 mt-1">
          {{ formatDateTime(invoice.created_at) }} &nbsp;·&nbsp;
          {{ invoice.customer_name || 'Walk-in customer' }} &nbsp;·&nbsp;
          Created by {{ invoice.created_by_name }}
        </p>
      </div>

      <div class="flex items-center gap-2 flex-wrap">
        <!-- Finalized: show Return and Void; no Edit -->
        <template v-if="isFinalized">
          <AppButton variant="secondary" @click="showReturnModal = true">Return Items</AppButton>
          <AppButton
            v-if="perms.canVoidInvoices.value"
            variant="danger"
            :loading="voiding"
            @click="handleVoid"
          >Void Invoice</AppButton>
        </template>
        <!-- Draft: allow edit -->
        <template v-if="isEditable">
          <AppButton variant="secondary">Edit Draft</AppButton>
          <AppButton variant="primary">Finalize</AppButton>
        </template>
        <!-- Voided/Returned: read-only notice -->
        <span v-if="isVoided || isReturned" class="text-xs text-gray-500 italic">This invoice is {{ invoice.status }} — no further actions available.</span>

        <AppButton variant="ghost" @click="router.back()">← Back</AppButton>
      </div>
    </div>

    <!-- Line items -->
    <div class="card overflow-hidden">
      <table class="table-base">
        <thead><tr>
          <th>Product</th><th>IMEI</th><th class="text-right">Qty</th>
          <th class="text-right">Unit Price</th><th class="text-right">Disc</th><th class="text-right">Total</th>
        </tr></thead>
        <tbody>
          <tr v-for="line in invoice.lines" :key="line.id">
            <td class="px-3 py-2.5">{{ line.product_name }}</td>
            <td class="px-3 py-2.5 font-mono text-xs text-gray-500">{{ line.imei || '—' }}</td>
            <td class="px-3 py-2.5 text-right">{{ line.qty }}</td>
            <td class="px-3 py-2.5 text-right"><MoneyDisplay :value="line.unit_price" /></td>
            <td class="px-3 py-2.5 text-right text-green-700">
              <MoneyDisplay v-if="line.discount_abs > 0" :value="line.discount_abs" />
              <span v-else-if="line.discount_pct > 0">{{ line.discount_pct }}%</span>
              <span v-else class="text-gray-400">—</span>
            </td>
            <td class="px-3 py-2.5 text-right font-medium"><MoneyDisplay :value="line.line_total" /></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Totals -->
    <div class="flex justify-end">
      <div class="w-64 space-y-2 text-sm">
        <div class="flex justify-between text-gray-600"><span>Subtotal</span><MoneyDisplay :value="invoice.subtotal" /></div>
        <div v-if="invoice.tax_amount > 0" class="flex justify-between text-gray-600"><span>Tax</span><MoneyDisplay :value="invoice.tax_amount" /></div>
        <div v-if="invoice.invoice_discount > 0" class="flex justify-between text-green-700"><span>Discount</span><span>− <MoneyDisplay :value="invoice.invoice_discount" /></span></div>
        <hr class="border-gray-200" />
        <div class="flex justify-between font-bold text-base text-gray-900"><span>Total</span><MoneyDisplay :value="invoice.grand_total" /></div>
        <div class="flex justify-between text-gray-600"><span>Paid</span><MoneyDisplay :value="invoice.amount_paid" /></div>
        <div
          v-if="invoice.balance_due > 0"
          class="flex justify-between font-semibold text-red-600"
        ><span>Balance Due</span><MoneyDisplay :value="invoice.balance_due" /></div>
      </div>
    </div>

    <!-- Return modal -->
    <AppModal :open="showReturnModal" title="Return Items" size="lg" @close="showReturnModal = false">
      <div class="space-y-3">
        <p class="text-sm text-gray-600">Select items and quantities to return:</p>
        <table class="table-base">
          <thead><tr>
            <th>Product</th><th>IMEI</th><th class="text-right">Sold</th><th class="text-right">Return Qty</th>
          </tr></thead>
          <tbody>
            <tr v-for="line in returnLines" :key="line.id">
              <td class="px-3 py-2">{{ line.product_name }}</td>
              <td class="px-3 py-2 font-mono text-xs">{{ line.imei || '—' }}</td>
              <td class="px-3 py-2 text-right">{{ line.qty }}</td>
              <td class="px-3 py-2 text-right">
                <input
                  v-model.number="line.return_qty"
                  type="number"
                  :min="0"
                  :max="line.qty"
                  class="input w-16 text-right text-sm"
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <template #footer>
        <AppButton variant="secondary" @click="showReturnModal = false">Cancel</AppButton>
        <AppButton variant="danger" :loading="returning" @click="handleReturn">Process Return</AppButton>
      </template>
    </AppModal>
  </div>
  <div v-else class="text-center py-20 text-gray-400">Loading…</div>
</template>
