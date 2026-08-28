<script setup>
import { ref, onMounted, watch } from 'vue'
import { inventoryApi } from '@/api/inventory'
import { useUiStore } from '@/stores/ui'
import { useConfirm } from '@/composables/useConfirm'
import { usePermissions } from '@/composables/usePermissions'
import { usePagination } from '@/composables/usePagination'
import { formatMoney } from '@/utils/money'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import AppTable from '@/components/ui/AppTable.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppPagination from '@/components/ui/AppPagination.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppInput from '@/components/ui/AppInput.vue'

const ui    = useUiStore()
const { confirm } = useConfirm()
const perms = usePermissions()
const pg    = usePagination({ pageSize: 30 })

const items       = ref([])
const loading     = ref(false)
const search      = ref('')
const showAdjust  = ref(false)
const adjustItem  = ref(null)
const adjustQty   = ref(0)
const adjustNote  = ref('')
const adjusting   = ref(false)

const columns = [
  { key: 'name',       label: 'Name',      sortable: true },
  { key: 'sku',        label: 'SKU' },
  { key: 'stock_qty',  label: 'Stock',     align: 'right' },
  { key: 'reorder',    label: 'Reorder',   align: 'right' },
  { key: 'sell_price', label: 'Sell Price', align: 'right' },
  { key: 'cost_price', label: 'Cost',      align: 'right' },
  { key: 'actions',    label: '' },
]

async function load() {
  loading.value = true
  try {
    const res = await inventoryApi.listAccessories({ search: search.value, ...pg.queryParams.value })
    items.value = res.data.results ?? res.data
    pg.setFromResponse({ count: res.data.count ?? items.value.length })
  } finally { loading.value = false }
}

watch([search, () => pg.currentPage.value], load)
onMounted(load)

function openAdjust(item) {
  adjustItem.value = item
  adjustQty.value  = 0
  adjustNote.value = ''
  showAdjust.value = true
}

async function submitAdjust() {
  if (!adjustQty.value) { ui.toastWarn('Quantity cannot be zero'); return }
  const newQty = adjustItem.value.stock_qty + adjustQty.value
  const ok = await confirm({
    title:        'Adjust Stock',
    message:      `Set "${adjustItem.value.name}" stock from ${adjustItem.value.stock_qty} → ${newQty}`,
    effect:       adjustQty.value < 0
      ? `This will reduce stock by ${Math.abs(adjustQty.value)} units.`
      : `This will add ${adjustQty.value} units to inventory.`,
    confirmLabel: 'Confirm Adjustment',
    confirmClass: 'btn-primary',
  })
  if (!ok) return
  adjusting.value = true
  try {
    await inventoryApi.adjustStock(adjustItem.value.id, { qty_change: adjustQty.value, note: adjustNote.value })
    ui.toastSuccess('Stock adjusted')
    showAdjust.value = false
    load()
  } catch (e) {
    ui.toastError(e.displayMessage || 'Adjustment failed')
  } finally { adjusting.value = false }
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-3">
      <input v-model="search" type="search" class="input max-w-xs" placeholder="Search accessories…" />
      <div class="flex-1" />
      <AppButton variant="primary">+ Add Accessory</AppButton>
    </div>

    <AppTable :columns="columns" :loading="loading" empty-message="No accessories found">
      <tr v-for="item in items" :key="item.id">
        <td class="px-3 py-2.5 font-medium text-gray-900">{{ item.name }}</td>
        <td class="px-3 py-2.5 font-mono text-xs text-gray-500">{{ item.sku }}</td>
        <td class="px-3 py-2.5 text-right">
          <span :class="item.stock_qty <= item.reorder_level ? 'text-red-600 font-semibold' : ''">
            {{ item.stock_qty }}
          </span>
        </td>
        <td class="px-3 py-2.5 text-right text-gray-500">{{ item.reorder_level }}</td>
        <td class="px-3 py-2.5 text-right"><MoneyDisplay :value="item.sell_price" /></td>
        <td class="px-3 py-2.5 text-right"><MoneyDisplay :value="item.cost_price" :mask="!perms.canViewCost.value" /></td>
        <td class="px-3 py-2.5 text-right">
          <button class="text-xs text-blue-600 hover:underline mr-3" @click="openAdjust(item)">Adjust</button>
          <button class="text-xs text-gray-500 hover:underline">Edit</button>
        </td>
      </tr>
    </AppTable>

    <AppPagination v-bind="{ currentPage: pg.currentPage.value, totalPages: pg.totalPages.value, totalCount: pg.totalCount.value, pageSize: pg.pageSize.value }" @page="pg.goTo" />

    <!-- Stock Adjustment Modal -->
    <AppModal :open="showAdjust" :title="`Adjust Stock — ${adjustItem?.name}`" size="sm" @close="showAdjust = false">
      <div class="space-y-4">
        <p class="text-sm text-gray-600">Current stock: <strong>{{ adjustItem?.stock_qty }}</strong></p>
        <AppInput
          v-model="adjustQty"
          label="Quantity Change"
          type="number"
          hint="Positive to add, negative to remove"
          :error="adjustQty === 0 ? '' : ''"
        />
        <AppInput v-model="adjustNote" label="Reason / Note" placeholder="e.g. physical count, damaged goods…" />
        <div v-if="adjustQty !== 0" class="text-sm font-medium" :class="adjustQty > 0 ? 'text-green-700' : 'text-red-600'">
          New stock will be: {{ (adjustItem?.stock_qty || 0) + Number(adjustQty) }}
        </div>
      </div>
      <template #footer>
        <AppButton variant="secondary" @click="showAdjust = false">Cancel</AppButton>
        <AppButton variant="primary" :loading="adjusting" @click="submitAdjust">Apply</AppButton>
      </template>
    </AppModal>
  </div>
</template>
