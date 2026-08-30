<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMockDataStore } from '@/stores/mockData'
import { useUiStore } from '@/stores/ui'
import { useConfirm } from '@/composables/useConfirm'
import { formatDate, formatDateTime } from '@/utils/date'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'

const route  = useRoute()
const router = useRouter()
const mock   = useMockDataStore()
const ui     = useUiStore()
const { confirm } = useConfirm()

const transfer = ref(null)

onMounted(() => {
  transfer.value = mock.getTransfer(route.params.id)
  if (!transfer.value) router.replace('/transfers')
})

const statusMap = {
  pending:    { label: 'Pending',    badge: 'badge-yellow' },
  dispatched: { label: 'Dispatched', badge: 'badge-blue' },
  received:   { label: 'Received',   badge: 'badge-green' },
  cancelled:  { label: 'Cancelled',  badge: 'badge-red' },
}

async function handleDispatch() {
  const ok = await confirm({
    title:  'Dispatch Transfer',
    message: `Dispatch ${transfer.value.transfer_number} from ${transfer.value.from_branch_name}?`,
    effect: 'Items will be deducted from origin branch inventory.',
    confirmLabel: 'Dispatch',
    confirmClass: 'btn-primary',
  })
  if (!ok) return
  mock.updateTransfer(transfer.value.id, {
    status: 'dispatched',
    dispatched_at: new Date().toISOString(),
  })
  transfer.value = mock.getTransfer(transfer.value.id)
  ui.toastSuccess('Transfer dispatched')
}

async function handleReceive() {
  const ok = await confirm({
    title:  'Receive Transfer',
    message: `Confirm receipt at ${transfer.value.to_branch_name}?`,
    effect: 'Items will be added to destination branch inventory.',
    confirmLabel: 'Receive',
    confirmClass: 'btn-primary',
  })
  if (!ok) return
  mock.updateTransfer(transfer.value.id, {
    status: 'received',
    received_at: new Date().toISOString(),
  })
  transfer.value = mock.getTransfer(transfer.value.id)
  ui.toastSuccess('Transfer received')
}
</script>

<template>
  <div v-if="transfer" class="space-y-4 max-w-3xl">
    <div class="flex items-start justify-between flex-wrap gap-3">
      <div>
        <div class="flex items-center gap-3">
          <h2 class="text-xl font-bold text-gray-900">{{ transfer.transfer_number }}</h2>
          <AppBadge
            :label="statusMap[transfer.status]?.label || transfer.status"
            :variant="statusMap[transfer.status]?.badge || 'badge-gray'"
          />
        </div>
        <p class="text-sm text-gray-500 mt-1">
          {{ transfer.from_branch_name }} → {{ transfer.to_branch_name }}
          &nbsp;·&nbsp; Created by {{ transfer.created_by }}
        </p>
      </div>
      <div class="flex gap-2">
        <AppButton v-if="transfer.status === 'pending'" variant="primary" @click="handleDispatch">Dispatch</AppButton>
        <AppButton v-if="transfer.status === 'dispatched'" variant="primary" @click="handleReceive">Mark Received</AppButton>
        <AppButton variant="ghost" @click="router.back()">← Back</AppButton>
      </div>
    </div>

    <!-- Timeline -->
    <div class="card p-4 space-y-2">
      <p class="text-xs font-semibold uppercase text-gray-500 tracking-wide">Status History</p>
      <div class="space-y-1.5 text-xs">
        <div class="flex items-center gap-2">
          <span class="badge badge-gray">Created</span>
          <span class="text-gray-500">{{ formatDateTime(transfer.created_at) }} by {{ transfer.created_by }}</span>
        </div>
        <div v-if="transfer.dispatched_at" class="flex items-center gap-2">
          <span class="badge badge-blue">Dispatched</span>
          <span class="text-gray-500">{{ formatDateTime(transfer.dispatched_at) }}</span>
        </div>
        <div v-if="transfer.received_at" class="flex items-center gap-2">
          <span class="badge badge-green">Received</span>
          <span class="text-gray-500">{{ formatDateTime(transfer.received_at) }}</span>
        </div>
      </div>
    </div>

    <!-- Notes -->
    <div v-if="transfer.notes" class="card p-4">
      <p class="text-xs font-semibold uppercase text-gray-500 tracking-wide mb-1">Notes</p>
      <p class="text-sm text-gray-700">{{ transfer.notes }}</p>
    </div>

    <!-- Items placeholder -->
    <div class="card p-4">
      <p class="text-xs font-semibold uppercase text-gray-500 tracking-wide mb-2">Items</p>
      <p class="text-sm text-gray-400 italic">Line items would be listed here when items are added to the transfer.</p>
    </div>
  </div>
  <div v-else class="text-center py-20 text-gray-400">Loading…</div>
</template>
