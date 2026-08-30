<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMockDataStore } from '@/stores/mockData'
import { useUiStore } from '@/stores/ui'
import { formatDate } from '@/utils/date'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppModal from '@/components/ui/AppModal.vue'

const mock   = useMockDataStore()
const router = useRouter()
const ui     = useUiStore()

const showCreate = ref(false)
const saving     = ref(false)
const form       = ref({ from_branch_id: 1, to_branch_id: 2, notes: '' })

const statusMap = {
  pending:    { label: 'Pending',    badge: 'badge-yellow' },
  dispatched: { label: 'Dispatched', badge: 'badge-blue' },
  received:   { label: 'Received',   badge: 'badge-green' },
  cancelled:  { label: 'Cancelled',  badge: 'badge-red' },
}

const transfers = computed(() =>
  [...mock.transfers].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
)

async function createTransfer() {
  saving.value = true
  await new Promise(r => setTimeout(r, 100))
  const fromB = mock.branches.find(b => b.id === Number(form.value.from_branch_id))
  const toB   = mock.branches.find(b => b.id === Number(form.value.to_branch_id))
  mock.addTransfer({
    transfer_number: `TRF-${String(mock.transfers.length + 1).padStart(3, '0')}`,
    from_branch_id: Number(form.value.from_branch_id),
    from_branch_name: fromB?.name || '',
    to_branch_id: Number(form.value.to_branch_id),
    to_branch_name: toB?.name || '',
    status: 'pending',
    line_count: 0,
    created_by: 'admin',
    dispatched_at: null,
    received_at: null,
    notes: form.value.notes,
  })
  ui.toastSuccess('Transfer created')
  showCreate.value = false
  saving.value = false
}
</script>

<template>
  <div class="space-y-3">
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-bold text-gray-900">Stock Transfers</h2>
      <AppButton variant="primary" @click="showCreate = true">+ New Transfer</AppButton>
    </div>

    <div class="card overflow-hidden">
      <table class="table-base">
        <thead>
          <tr>
            <th>Transfer #</th><th>From</th><th>To</th><th>Lines</th><th>Status</th><th>Date</th><th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in transfers" :key="t.id" class="cursor-pointer" @click="router.push(`/transfers/${t.id}`)">
            <td class="px-3 py-2.5 font-mono text-blue-700">{{ t.transfer_number }}</td>
            <td class="px-3 py-2.5">{{ t.from_branch_name }}</td>
            <td class="px-3 py-2.5">{{ t.to_branch_name }}</td>
            <td class="px-3 py-2.5 text-center">{{ t.line_count }}</td>
            <td class="px-3 py-2.5">
              <AppBadge :label="statusMap[t.status]?.label || t.status" :variant="statusMap[t.status]?.badge || 'badge-gray'" />
            </td>
            <td class="px-3 py-2.5 text-xs text-gray-500">{{ formatDate(t.created_at) }}</td>
            <td class="px-3 py-2.5">
              <RouterLink :to="`/transfers/${t.id}`" class="text-xs text-blue-600 hover:underline" @click.stop>View</RouterLink>
            </td>
          </tr>
          <tr v-if="!transfers.length">
            <td colspan="7" class="py-8 text-center text-xs text-gray-400">No transfers</td>
          </tr>
        </tbody>
      </table>
    </div>

    <AppModal :open="showCreate" title="New Transfer" size="sm" @close="showCreate = false">
      <div class="space-y-3">
        <div>
          <label class="label">From Branch</label>
          <select v-model="form.from_branch_id" class="input" data-no-scanner-refocus>
            <option v-for="b in mock.branches" :key="b.id" :value="b.id">{{ b.name }}</option>
          </select>
        </div>
        <div>
          <label class="label">To Branch</label>
          <select v-model="form.to_branch_id" class="input" data-no-scanner-refocus>
            <option v-for="b in mock.branches" :key="b.id" :value="b.id">{{ b.name }}</option>
          </select>
        </div>
        <div>
          <label class="label">Notes</label>
          <input v-model="form.notes" type="text" class="input" placeholder="Optional note" data-no-scanner-refocus />
        </div>
      </div>
      <template #footer>
        <AppButton variant="secondary" @click="showCreate = false">Cancel</AppButton>
        <AppButton variant="primary" :loading="saving" @click="createTransfer">Create</AppButton>
      </template>
    </AppModal>
  </div>
</template>
