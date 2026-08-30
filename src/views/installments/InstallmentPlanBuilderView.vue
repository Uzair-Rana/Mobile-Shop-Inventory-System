<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMockDataStore } from '@/stores/mockData'
import { useUiStore } from '@/stores/ui'
import { formatMoney } from '@/utils/money'
import { formatDate } from '@/utils/date'
import AppButton from '@/components/ui/AppButton.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'

const mock   = useMockDataStore()
const router = useRouter()
const ui     = useUiStore()

const saleAmount     = ref(100000)
const downPayment    = ref(20000)
const markupRate     = ref(10)
const installmentCount = ref(6)
const customerId     = ref('')
const productName    = ref('')
const saving         = ref(false)

const financedAmount = computed(() => Math.max(0, Number(saleAmount.value) - Number(downPayment.value)))
const totalPayable   = computed(() => financedAmount.value * (1 + Number(markupRate.value) / 100))
const installmentAmount = computed(() =>
  installmentCount.value > 0 ? totalPayable.value / Number(installmentCount.value) : 0
)

const schedule = computed(() => {
  const items = []
  const today = new Date()
  for (let i = 1; i <= Number(installmentCount.value); i++) {
    const due = new Date(today)
    due.setMonth(due.getMonth() + i)
    items.push({ n: i, due_date: due.toISOString().slice(0, 10), amount: installmentAmount.value })
  }
  return items
})

const selectedCustomer = computed(() =>
  customerId.value ? mock.getCustomer(customerId.value) : null
)

async function handleSave() {
  if (!customerId.value || !productName.value) {
    ui.toastWarn('Select a customer and enter product name')
    return
  }
  saving.value = true
  await new Promise(r => setTimeout(r, 150))
  ui.toastSuccess('Installment plan created')
  router.push('/installments')
}
</script>

<template>
  <div class="space-y-4 max-w-4xl">
    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-gray-900">New Installment Plan</h2>
      <AppButton variant="ghost" @click="router.back()">← Back</AppButton>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-2 gap-4">
      <!-- Left: inputs -->
      <div class="space-y-3">
        <div class="card p-4 space-y-3">
          <p class="text-xs font-semibold uppercase text-gray-500">Customer & Product</p>
          <div>
            <label class="label">Customer</label>
            <select v-model="customerId" class="input" data-no-scanner-refocus>
              <option value="">Select customer…</option>
              <option v-for="c in mock.customers" :key="c.id" :value="c.id">{{ c.name }} — {{ c.phone }}</option>
            </select>
          </div>
          <div>
            <label class="label">Product / Item</label>
            <input v-model="productName" type="text" class="input" placeholder="e.g. Samsung Galaxy S23" data-no-scanner-refocus />
          </div>
        </div>

        <div class="card p-4 space-y-3">
          <p class="text-xs font-semibold uppercase text-gray-500">Payment Terms</p>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="label">Sale Amount (Rs.)</label>
              <input v-model.number="saleAmount" type="number" min="0" step="1000" class="input" data-no-scanner-refocus />
            </div>
            <div>
              <label class="label">Down Payment (Rs.)</label>
              <input v-model.number="downPayment" type="number" min="0" step="1000" class="input" data-no-scanner-refocus />
            </div>
            <div>
              <label class="label">Markup (%)</label>
              <input v-model.number="markupRate" type="number" min="0" max="100" step="0.5" class="input" data-no-scanner-refocus />
            </div>
            <div>
              <label class="label">Installments</label>
              <select v-model="installmentCount" class="input" data-no-scanner-refocus>
                <option :value="3">3 months</option>
                <option :value="6">6 months</option>
                <option :value="9">9 months</option>
                <option :value="12">12 months</option>
                <option :value="18">18 months</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Summary formula -->
        <div class="card p-4 space-y-2 bg-blue-50 border-blue-200">
          <p class="text-xs font-bold text-blue-800 uppercase tracking-wide">Calculation</p>
          <div class="space-y-1 text-sm">
            <div class="flex justify-between"><span class="text-gray-600">Sale Amount</span><MoneyDisplay :value="saleAmount" /></div>
            <div class="flex justify-between"><span class="text-gray-600">Down Payment</span><MoneyDisplay :value="downPayment" /></div>
            <div class="flex justify-between border-t border-blue-200 pt-1"><span class="text-gray-700 font-medium">Financed Amount</span><MoneyDisplay :value="financedAmount" class="font-semibold" /></div>
            <div class="flex justify-between"><span class="text-gray-600">Markup ({{ markupRate }}%)</span><MoneyDisplay :value="financedAmount * markupRate / 100" /></div>
            <div class="flex justify-between border-t border-blue-200 pt-1"><span class="text-gray-700 font-medium">Total Payable</span><MoneyDisplay :value="totalPayable" class="font-bold text-blue-800" /></div>
            <div class="flex justify-between"><span class="text-gray-600">Per Installment</span><MoneyDisplay :value="installmentAmount" class="font-bold text-blue-700" /></div>
          </div>
        </div>

        <AppButton variant="primary" :loading="saving" class="w-full" @click="handleSave">Create Plan</AppButton>
      </div>

      <!-- Right: schedule preview -->
      <div class="card overflow-hidden">
        <div class="panel-header">Schedule Preview</div>
        <table class="table-base">
          <thead><tr><th>#</th><th>Due Date</th><th class="text-right">Amount</th></tr></thead>
          <tbody>
            <tr v-for="s in schedule" :key="s.n">
              <td class="px-3 py-2 text-sm text-gray-500">{{ s.n }}</td>
              <td class="px-3 py-2 text-sm">{{ formatDate(s.due_date) }}</td>
              <td class="px-3 py-2 text-right font-medium"><MoneyDisplay :value="s.amount" /></td>
            </tr>
          </tbody>
        </table>
        <div class="panel-header">
          <span>Total</span>
          <MoneyDisplay :value="totalPayable" class="font-bold" />
        </div>
      </div>
    </div>
  </div>
</template>
