<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { installmentsApi } from '@/api/installments'
import { useUiStore } from '@/stores/ui'
import { useConfirm } from '@/composables/useConfirm'
import { formatDate } from '@/utils/date'
import { formatMoney } from '@/utils/money'
import { INSTALLMENT_STATUS } from '@/utils/constants'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppModal from '@/components/ui/AppModal.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'

const route  = useRoute()
const router = useRouter()
const ui     = useUiStore()
const { confirm } = useConfirm()

const plan     = ref(null)
const schedule = ref([])
const loading  = ref(true)
const showCollect   = ref(false)
const collectAmount = ref(0)
const collecting    = ref(false)

const isActive = computed(() => ['active', 'overdue'].includes(plan.value?.status))

onMounted(async () => {
  const [pRes, sRes] = await Promise.all([
    installmentsApi.getPlan(route.params.id),
    installmentsApi.getSchedule(route.params.id),
  ])
  plan.value     = pRes.data
  schedule.value = sRes.data
  loading.value  = false
})

function statusObj(val) {
  return Object.values(INSTALLMENT_STATUS).find(s => s.value === val) || { label: val, badge: 'badge-gray' }
}

async function handleCollect() {
  if (collectAmount.value <= 0) { ui.toastWarn('Enter a valid amount'); return }
  collecting.value = true
  try {
    await installmentsApi.collectPayment(plan.value.id, { amount: collectAmount.value })
    ui.toastSuccess('Payment collected')
    showCollect.value = false
    const res = await installmentsApi.getPlan(plan.value.id)
    plan.value = res.data
    const sRes = await installmentsApi.getSchedule(plan.value.id)
    schedule.value = sRes.data
  } catch (e) {
    ui.toastError(e.displayMessage || 'Collection failed')
  } finally { collecting.value = false }
}

async function handleDefault() {
  const ok = await confirm({
    title:  'Mark as Defaulted',
    message: `Mark installment plan #${plan.value.plan_number} as defaulted?`,
    effect: `Remaining balance of ${formatMoney(plan.value.remaining_amount)} will be flagged. This action affects customer credit standing.`,
    confirmLabel: 'Mark Defaulted',
    confirmClass: 'btn-danger',
  })
  if (!ok) return
  try {
    await installmentsApi.markDefaulted(plan.value.id, {})
    ui.toastSuccess('Marked as defaulted')
    const res = await installmentsApi.getPlan(plan.value.id)
    plan.value = res.data
  } catch (e) {
    ui.toastError(e.displayMessage || 'Failed')
  }
}
</script>

<template>
  <div v-if="!loading && plan" class="space-y-6 max-w-4xl">
    <div class="flex items-start justify-between flex-wrap gap-3">
      <div>
        <div class="flex items-center gap-3">
          <h2 class="text-xl font-bold text-gray-900">Installment Plan #{{ plan.plan_number }}</h2>
          <AppBadge :status="statusObj(plan.status)" />
        </div>
        <p class="text-sm text-gray-500 mt-1">{{ plan.customer_name }} &nbsp;·&nbsp; {{ plan.product_name }}</p>
      </div>
      <div class="flex gap-2">
        <template v-if="isActive">
          <AppButton variant="primary" @click="showCollect = true">Collect Payment</AppButton>
          <AppButton variant="danger" @click="handleDefault">Mark Defaulted</AppButton>
        </template>
        <AppButton variant="ghost" @click="router.back()">← Back</AppButton>
      </div>
    </div>

    <!-- Summary -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="card p-4"><p class="text-xs text-gray-500 uppercase">Total</p><MoneyDisplay :value="plan.total_amount" class="text-xl font-bold text-gray-900 block mt-1" /></div>
      <div class="card p-4"><p class="text-xs text-gray-500 uppercase">Paid</p><MoneyDisplay :value="plan.paid_amount" class="text-xl font-bold text-green-700 block mt-1" /></div>
      <div class="card p-4"><p class="text-xs text-gray-500 uppercase">Remaining</p><MoneyDisplay :value="plan.remaining_amount" class="text-xl font-bold text-red-600 block mt-1" /></div>
      <div class="card p-4"><p class="text-xs text-gray-500 uppercase">Installments</p><p class="text-xl font-bold text-gray-900 mt-1">{{ plan.paid_count }}/{{ plan.total_count }}</p></div>
    </div>

    <!-- Schedule -->
    <div class="card overflow-hidden">
      <div class="px-4 py-3 border-b border-gray-100 font-semibold text-sm">Payment Schedule</div>
      <table class="table-base">
        <thead><tr><th>#</th><th>Due Date</th><th class="text-right">Amount</th><th>Paid On</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="inst in schedule" :key="inst.id" :class="inst.status === 'overdue' ? 'bg-red-50' : ''">
            <td class="px-3 py-2 text-sm text-gray-500">{{ inst.installment_number }}</td>
            <td class="px-3 py-2 text-sm">{{ formatDate(inst.due_date) }}</td>
            <td class="px-3 py-2 text-right"><MoneyDisplay :value="inst.amount" /></td>
            <td class="px-3 py-2 text-sm text-gray-500">{{ inst.paid_at ? formatDate(inst.paid_at) : '—' }}</td>
            <td class="px-3 py-2">
              <AppBadge
                :label="inst.status"
                :variant="inst.status === 'paid' ? 'badge-green' : inst.status === 'overdue' ? 'badge-red' : 'badge-gray'"
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Collect payment modal -->
    <AppModal :open="showCollect" title="Collect Installment Payment" size="sm" @close="showCollect = false">
      <div class="space-y-3">
        <p class="text-sm text-gray-600">Remaining: <strong>{{ formatMoney(plan.remaining_amount) }}</strong></p>
        <div>
          <label class="label">Amount</label>
          <input v-model.number="collectAmount" type="number" min="0" step="100" :max="plan.remaining_amount" class="input" />
        </div>
      </div>
      <template #footer>
        <AppButton variant="secondary" @click="showCollect = false">Cancel</AppButton>
        <AppButton variant="primary" :loading="collecting" @click="handleCollect">Collect</AppButton>
      </template>
    </AppModal>
  </div>
  <div v-else class="text-center py-20 text-gray-400">Loading…</div>
</template>
