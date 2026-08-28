<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { purchasesApi } from '@/api/purchases'
import { useUiStore } from '@/stores/ui'
import { useConfirm } from '@/composables/useConfirm'
import { formatDate } from '@/utils/date'
import { formatMoney } from '@/utils/money'
import { PO_STATUS } from '@/utils/constants'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppModal from '@/components/ui/AppModal.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'

const route  = useRoute()
const router = useRouter()
const ui     = useUiStore()
const { confirm } = useConfirm()

const order    = ref(null)
const loading  = ref(true)
const receiving= ref(false)
const showPaymentModal = ref(false)
const paymentAmount = ref(0)
const addingPayment = ref(false)

const isReceivable = computed(() => ['ordered', 'partial'].includes(order.value?.status))
const isPayable    = computed(() => ['ordered', 'partial', 'received'].includes(order.value?.status))
const balance      = computed(() => (order.value?.total_amount || 0) - (order.value?.amount_paid || 0))

onMounted(async () => {
  const res = await purchasesApi.getOrder(route.params.id)
  order.value  = res.data
  loading.value = false
})

function statusObj(val) {
  return Object.values(PO_STATUS).find(s => s.value === val) || { label: val, badge: 'badge-gray' }
}

async function handleReceive() {
  const ok = await confirm({
    title:  `Receive PO #${order.value.po_number}`,
    message: 'Mark all items as received and update inventory.',
    effect: `Adds ${order.value.line_count} line(s) to inventory. Inventory counts will be updated immediately.`,
    confirmLabel: 'Receive Order',
    confirmClass: 'btn-primary',
  })
  if (!ok) return
  receiving.value = true
  try {
    await purchasesApi.receiveOrder(order.value.id, {})
    ui.toastSuccess('Order received — inventory updated')
    const res = await purchasesApi.getOrder(order.value.id)
    order.value = res.data
  } catch (e) {
    ui.toastError(e.displayMessage || 'Receive failed')
  } finally { receiving.value = false }
}

async function handlePayment() {
  if (paymentAmount.value <= 0) { ui.toastWarn('Enter a valid amount'); return }
  addingPayment.value = true
  try {
    await purchasesApi.addPayment(order.value.id, { amount: paymentAmount.value })
    ui.toastSuccess('Payment recorded')
    showPaymentModal.value = false
    const res = await purchasesApi.getOrder(order.value.id)
    order.value = res.data
  } catch (e) {
    ui.toastError(e.displayMessage || 'Payment failed')
  } finally { addingPayment.value = false }
}
</script>

<template>
  <div v-if="!loading && order" class="space-y-6 max-w-4xl">
    <div class="flex items-start justify-between flex-wrap gap-3">
      <div>
        <div class="flex items-center gap-3">
          <h2 class="text-xl font-bold text-gray-900">PO #{{ order.po_number }}</h2>
          <AppBadge :status="statusObj(order.status)" />
        </div>
        <p class="text-sm text-gray-500">{{ order.supplier_name }} &nbsp;·&nbsp; {{ formatDate(order.created_at) }}</p>
      </div>
      <div class="flex gap-2">
        <AppButton v-if="isReceivable" variant="primary" :loading="receiving" @click="handleReceive">Mark as Received</AppButton>
        <AppButton v-if="isPayable && balance > 0" variant="secondary" @click="showPaymentModal = true">Record Payment</AppButton>
        <AppButton variant="ghost" @click="router.back()">← Back</AppButton>
      </div>
    </div>

    <!-- Financials -->
    <div class="grid grid-cols-3 gap-4">
      <div class="card p-4"><p class="text-xs text-gray-500 uppercase">Order Total</p><MoneyDisplay :value="order.total_amount" class="text-xl font-bold text-gray-900 block mt-1" /></div>
      <div class="card p-4"><p class="text-xs text-gray-500 uppercase">Paid</p><MoneyDisplay :value="order.amount_paid" class="text-xl font-bold text-green-700 block mt-1" /></div>
      <div class="card p-4"><p class="text-xs text-gray-500 uppercase">Balance</p><MoneyDisplay :value="balance" class="text-xl font-bold block mt-1" :class="balance > 0 ? 'text-red-600' : 'text-gray-900'" /></div>
    </div>

    <!-- Lines -->
    <div class="card overflow-hidden">
      <div class="px-4 py-3 border-b border-gray-100 font-semibold text-sm">Items</div>
      <table class="table-base">
        <thead><tr><th>Product</th><th class="text-right">Qty</th><th class="text-right">Ordered</th><th class="text-right">Received</th><th class="text-right">Unit Cost</th><th class="text-right">Total</th></tr></thead>
        <tbody>
          <tr v-for="line in order.lines" :key="line.id">
            <td class="px-3 py-2.5">{{ line.product_name }}</td>
            <td class="px-3 py-2.5 text-right">{{ line.qty_ordered }}</td>
            <td class="px-3 py-2.5 text-right">{{ line.qty_ordered }}</td>
            <td class="px-3 py-2.5 text-right">{{ line.qty_received }}</td>
            <td class="px-3 py-2.5 text-right"><MoneyDisplay :value="line.unit_cost" /></td>
            <td class="px-3 py-2.5 text-right font-medium"><MoneyDisplay :value="line.qty_ordered * line.unit_cost" /></td>
          </tr>
        </tbody>
      </table>
    </div>

    <AppModal :open="showPaymentModal" title="Record Payment" size="sm" @close="showPaymentModal = false">
      <div class="space-y-3">
        <p class="text-sm text-gray-600">Balance due: <strong>{{ formatMoney(balance) }}</strong></p>
        <div>
          <label class="label">Amount</label>
          <input v-model.number="paymentAmount" type="number" :max="balance" min="0" step="100" class="input" />
        </div>
      </div>
      <template #footer>
        <AppButton variant="secondary" @click="showPaymentModal = false">Cancel</AppButton>
        <AppButton variant="primary" :loading="addingPayment" @click="handlePayment">Record Payment</AppButton>
      </template>
    </AppModal>
  </div>
  <div v-else class="text-center py-20 text-gray-400">Loading…</div>
</template>
