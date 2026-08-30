<script setup>
import { ref, computed } from 'vue'
import { useMockDataStore } from '@/stores/mockData'
import { useUiStore } from '@/stores/ui'
import { formatDate } from '@/utils/date'
import { formatMoney } from '@/utils/money'
import AppButton from '@/components/ui/AppButton.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppModal from '@/components/ui/AppModal.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'

const mock = useMockDataStore()
const ui   = useUiStore()

const search   = ref('')
const filterCat= ref('')
const showForm = ref(false)
const saving   = ref(false)

const categories = ['Utilities', 'Supplies', 'Maintenance', 'Marketing', 'Rent', 'Salary', 'Transport', 'Other']
const sources    = ['cash', 'bank', 'cheque']

const form = ref({ date: new Date().toISOString().slice(0, 10), category: 'Supplies', amount: '', payment_source: 'cash', notes: '', approval_state: 'pending' })

const filtered = computed(() => {
  let list = [...mock.expenses].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(e => e.category.toLowerCase().includes(q) || e.notes?.toLowerCase().includes(q))
  }
  if (filterCat.value) list = list.filter(e => e.category === filterCat.value)
  return list
})

const expCats = computed(() => [...new Set(mock.expenses.map(e => e.category))])

function approvalBadge(state) {
  return state === 'approved' ? 'badge-green' : state === 'pending' ? 'badge-yellow' : 'badge-red'
}

async function handleSave() {
  if (!form.value.amount || !form.value.category) { ui.toastWarn('Fill required fields'); return }
  saving.value = true
  await new Promise(r => setTimeout(r, 100))
  mock.addExpense({ ...form.value, branch_id: 1 })
  ui.toastSuccess('Expense recorded')
  showForm.value = false
  form.value = { date: new Date().toISOString().slice(0, 10), category: 'Supplies', amount: '', payment_source: 'cash', notes: '', approval_state: 'pending' }
  saving.value = false
}
</script>

<template>
  <div class="space-y-3">
    <div class="flex items-center gap-2 flex-wrap">
      <input v-model="search" type="search" class="input max-w-xs" placeholder="Search expenses…" data-no-scanner-refocus />
      <select v-model="filterCat" class="input w-36" data-no-scanner-refocus>
        <option value="">All Categories</option>
        <option v-for="c in expCats" :key="c" :value="c">{{ c }}</option>
      </select>
      <div class="flex-1" />
      <AppButton variant="primary" @click="showForm = true">+ New Expense</AppButton>
    </div>

    <div class="card overflow-hidden">
      <table class="table-base">
        <thead>
          <tr>
            <th>Date</th><th>Category</th><th>Notes</th><th>Source</th><th>Status</th><th class="text-right">Amount</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="e in filtered" :key="e.id">
            <td class="px-3 py-2 text-sm">{{ formatDate(e.date) }}</td>
            <td class="px-3 py-2 font-medium">{{ e.category }}</td>
            <td class="px-3 py-2 text-xs text-gray-500 max-w-xs truncate">{{ e.notes || '—' }}</td>
            <td class="px-3 py-2 text-xs text-gray-500 capitalize">{{ e.payment_source }}</td>
            <td class="px-3 py-2">
              <AppBadge :label="e.approval_state" :variant="approvalBadge(e.approval_state)" />
            </td>
            <td class="px-3 py-2 text-right font-medium"><MoneyDisplay :value="e.amount" /></td>
          </tr>
          <tr v-if="!filtered.length">
            <td colspan="6" class="py-8 text-center text-xs text-gray-400">No expenses found</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- New Expense Modal -->
    <AppModal :open="showForm" title="New Expense" size="sm" @close="showForm = false">
      <div class="space-y-3">
        <div>
          <label class="label">Date</label>
          <input v-model="form.date" type="date" class="input" data-no-scanner-refocus />
        </div>
        <div>
          <label class="label">Category *</label>
          <select v-model="form.category" class="input" data-no-scanner-refocus>
            <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
        <div>
          <label class="label">Amount (Rs.) *</label>
          <input v-model.number="form.amount" type="number" min="0" class="input" data-no-scanner-refocus />
        </div>
        <div>
          <label class="label">Payment Source</label>
          <select v-model="form.payment_source" class="input" data-no-scanner-refocus>
            <option v-for="s in sources" :key="s" :value="s" class="capitalize">{{ s }}</option>
          </select>
        </div>
        <div>
          <label class="label">Notes</label>
          <input v-model="form.notes" type="text" class="input" placeholder="What was this for?" data-no-scanner-refocus />
        </div>
      </div>
      <template #footer>
        <AppButton variant="secondary" @click="showForm = false">Cancel</AppButton>
        <AppButton variant="primary" :loading="saving" @click="handleSave">Save Expense</AppButton>
      </template>
    </AppModal>
  </div>
</template>
