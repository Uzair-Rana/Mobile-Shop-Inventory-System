<script setup>
import { ref, computed } from 'vue'
import { useCashSessionStore, CASH_SESSION_STATUS } from '@/stores/cashSession'
import { useUiStore } from '@/stores/ui'
import { formatMoney } from '@/utils/money'
import { formatDateTime } from '@/utils/date'
import AppButton from '@/components/ui/AppButton.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import AppBadge from '@/components/ui/AppBadge.vue'

const session = useCashSessionStore()
const ui = useUiStore()

const openingAmount = ref(10000)
const countAmount   = ref(0)
const outflowCategory = ref('Expense')
const outflowAmount   = ref(0)
const outflowNote     = ref('')

function handleOpen() {
  if (!openingAmount.value) { ui.toastWarn('Enter opening amount'); return }
  session.openSession(openingAmount.value)
}

function handleAddOutflow() {
  if (!outflowAmount.value) { ui.toastWarn('Enter amount'); return }
  session.addOutflow({ category: outflowCategory.value, amount: outflowAmount.value, note: outflowNote.value })
  outflowAmount.value = 0
  outflowNote.value   = ''
  ui.toastSuccess('Outflow recorded')
}

function handleSubmitCount() {
  if (!countAmount.value) { ui.toastWarn('Enter counted amount'); return }
  session.submitCount(countAmount.value)
}

const varianceClass = computed(() => {
  if (session.variance === null) return 'text-gray-900'
  if (session.variance > 0) return 'text-green-600'
  if (session.variance < 0) return 'text-red-600'
  return 'text-gray-900'
})
</script>

<template>
  <div class="space-y-4 max-w-3xl">
    <h2 class="text-xl font-bold text-gray-900">Cash Session</h2>

    <!-- CLOSED: Open Session form -->
    <div v-if="session.status === CASH_SESSION_STATUS.CLOSED" class="card p-6 space-y-4">
      <div class="flex items-center gap-3">
        <div class="h-10 w-10 rounded-full bg-gray-100 flex items-center justify-center">
          <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m0 0h.01M12 6v6m0 0h.01"/>
          </svg>
        </div>
        <div>
          <p class="font-semibold text-gray-900">No Active Session</p>
          <p class="text-sm text-gray-500">Open a cash drawer to start tracking</p>
        </div>
      </div>

      <div class="max-w-xs">
        <label class="label">Opening Cash Amount (Rs.)</label>
        <input v-model.number="openingAmount" type="number" min="0" step="100" class="input" data-no-scanner-refocus />
      </div>

      <AppButton variant="primary" @click="handleOpen">Open Session</AppButton>
    </div>

    <!-- OPEN: Running session -->
    <template v-if="session.status === CASH_SESSION_STATUS.OPEN">
      <!-- Summary stats -->
      <div class="grid grid-cols-3 gap-3">
        <div class="stat-cell">
          <span class="stat-label">Opening</span>
          <MoneyDisplay :value="session.activeSession?.opening_amount" class="stat-value" />
        </div>
        <div class="stat-cell">
          <span class="stat-label">Expected Cash</span>
          <MoneyDisplay :value="session.expectedCash" class="stat-value text-green-700" />
        </div>
        <div class="stat-cell">
          <span class="stat-label">Outflows</span>
          <MoneyDisplay :value="session.sessionOutflows.reduce((s, o) => s + o.amount, 0)" class="stat-value text-red-600" />
        </div>
      </div>

      <!-- Inflows table -->
      <div class="card overflow-hidden">
        <div class="panel-header">
          <span>Cash In</span>
          <span class="badge badge-green">{{ session.sessionInflows.length }} entries</span>
        </div>
        <table class="table-base">
          <thead><tr><th>Category</th><th>Note</th><th>Time</th><th class="text-right">Amount</th></tr></thead>
          <tbody>
            <tr v-for="entry in session.sessionInflows" :key="entry.id">
              <td class="px-3 py-2">{{ entry.category }}</td>
              <td class="px-3 py-2 text-gray-500 text-xs">{{ entry.note }}</td>
              <td class="px-3 py-2 text-xs text-gray-400">{{ formatDateTime(entry.created_at) }}</td>
              <td class="px-3 py-2 text-right font-medium text-green-700"><MoneyDisplay :value="entry.amount" /></td>
            </tr>
            <tr v-if="!session.sessionInflows.length">
              <td colspan="4" class="py-4 text-center text-xs text-gray-400">No inflows yet</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Add outflow -->
      <div class="card p-3">
        <p class="label mb-2">Record Outflow / Expense</p>
        <div class="flex gap-2 items-end flex-wrap">
          <div>
            <label class="label">Category</label>
            <select v-model="outflowCategory" class="input w-32" data-no-scanner-refocus>
              <option>Expense</option><option>Petty Cash</option><option>Supplier</option><option>Other</option>
            </select>
          </div>
          <div>
            <label class="label">Amount</label>
            <input v-model.number="outflowAmount" type="number" min="0" class="input w-28" data-no-scanner-refocus />
          </div>
          <div class="flex-1 min-w-32">
            <label class="label">Note</label>
            <input v-model="outflowNote" type="text" class="input" placeholder="What was it for?" data-no-scanner-refocus />
          </div>
          <AppButton variant="secondary" @click="handleAddOutflow">Add</AppButton>
        </div>
      </div>

      <!-- Outflows table -->
      <div v-if="session.sessionOutflows.length" class="card overflow-hidden">
        <div class="panel-header">
          <span>Cash Out</span>
          <span class="badge badge-red">{{ session.sessionOutflows.length }}</span>
        </div>
        <table class="table-base">
          <thead><tr><th>Category</th><th>Note</th><th>Actor</th><th class="text-right">Amount</th></tr></thead>
          <tbody>
            <tr v-for="entry in session.sessionOutflows" :key="entry.id">
              <td class="px-3 py-2">{{ entry.category }}</td>
              <td class="px-3 py-2 text-gray-500 text-xs">{{ entry.note }}</td>
              <td class="px-3 py-2 text-xs text-gray-400">{{ entry.actor }}</td>
              <td class="px-3 py-2 text-right font-medium text-red-600"><MoneyDisplay :value="entry.amount" /></td>
            </tr>
          </tbody>
        </table>
      </div>

      <AppButton variant="warn" @click="session.submitCount(session.expectedCash)">Proceed to Close Session</AppButton>
    </template>

    <!-- PENDING_COUNT: Enter physical count -->
    <template v-if="session.status === CASH_SESSION_STATUS.PENDING_COUNT">
      <div class="card p-6 space-y-4">
        <h3 class="font-semibold text-gray-900">Count Physical Cash</h3>
        <div class="grid grid-cols-3 gap-3">
          <div class="stat-cell">
            <span class="stat-label">Expected</span>
            <MoneyDisplay :value="session.expectedCash" class="stat-value" />
          </div>
          <div class="stat-cell">
            <span class="stat-label">Counted</span>
            <MoneyDisplay :value="session.countedAmount" class="stat-value" />
          </div>
          <div class="stat-cell">
            <span class="stat-label">Variance</span>
            <MoneyDisplay :value="session.variance" class="stat-value" :class="varianceClass" />
          </div>
        </div>

        <div class="max-w-xs">
          <label class="label">Physical Count (Rs.)</label>
          <input v-model.number="countAmount" type="number" min="0" step="100" class="input" data-no-scanner-refocus />
        </div>

        <div class="flex gap-2">
          <AppButton variant="secondary" @click="session.cancelCount">Back</AppButton>
          <AppButton variant="primary" @click="handleSubmitCount">Submit Count</AppButton>
        </div>
      </div>
    </template>

    <!-- RECONCILED: Closed -->
    <template v-if="session.status === CASH_SESSION_STATUS.RECONCILED">
      <div class="card p-6 space-y-4">
        <div class="flex items-center gap-3">
          <div class="h-10 w-10 rounded-full bg-green-100 flex items-center justify-center">
            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/>
            </svg>
          </div>
          <div>
            <p class="font-semibold text-gray-900">Session Closed</p>
            <p class="text-sm text-gray-500">Cash drawer reconciled</p>
          </div>
        </div>
        <div class="grid grid-cols-3 gap-3">
          <div class="stat-cell">
            <span class="stat-label">Expected</span>
            <MoneyDisplay :value="session.expectedCash" class="stat-value" />
          </div>
          <div class="stat-cell">
            <span class="stat-label">Counted</span>
            <MoneyDisplay :value="session.activeSession?.counted_amount" class="stat-value" />
          </div>
          <div class="stat-cell">
            <span class="stat-label">Variance</span>
            <MoneyDisplay :value="session.activeSession?.variance" class="stat-value" :class="varianceClass" />
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
