<script setup>
import { ref, onMounted, watch } from 'vue'
import { useInventoryStore } from '@/stores/inventory'
import { usePagination } from '@/composables/usePagination'
import { usePermissions } from '@/composables/usePermissions'
import { formatMoney } from '@/utils/money'
import AppTable from '@/components/ui/AppTable.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppPagination from '@/components/ui/AppPagination.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import ProductFormModal from './ProductFormModal.vue'

const inv   = useInventoryStore()
const pg    = usePagination({ pageSize: 25 })
const perms = usePermissions()

const search      = ref('')
const sortKey     = ref('name')
const sortDir     = ref('asc')
const showForm    = ref(false)
const editProduct = ref(null)

const columns = [
  { key: 'name',        label: 'Product Name', sortable: true },
  { key: 'brand',       label: 'Brand' },
  { key: 'category',    label: 'Category' },
  { key: 'sku',         label: 'SKU' },
  { key: 'stock',       label: 'Stock',   align: 'right' },
  { key: 'sell_price',  label: 'Sell Price', align: 'right' },
  { key: 'cost_price',  label: 'Cost Price', align: 'right' },
  { key: 'actions',     label: '' },
]

async function load() {
  const ordering = sortDir.value === 'desc' ? `-${sortKey.value}` : sortKey.value
  await inv.fetchProducts({
    search: search.value,
    ordering,
    ...pg.queryParams.value,
  })
  pg.setFromResponse({ count: inv.pagination.count })
}

function handleSort(key) {
  if (sortKey.value === key) sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  else { sortKey.value = key; sortDir.value = 'asc' }
}

watch([search, () => pg.currentPage.value, sortKey, sortDir], load)
onMounted(load)

function openNew() { editProduct.value = null; showForm.value = true }
function openEdit(p) { editProduct.value = p; showForm.value = true }
function onSaved() { showForm.value = false; load() }
</script>

<template>
  <div class="space-y-4">
    <!-- Toolbar -->
    <div class="flex items-center gap-3">
      <input
        v-model="search"
        type="search"
        class="input max-w-xs"
        placeholder="Search products…"
      />
      <div class="flex-1" />
      <AppButton variant="primary" @click="openNew">+ Add Product</AppButton>
    </div>

    <!-- Table -->
    <AppTable
      :columns="columns"
      :loading="inv.loading"
      empty-message="No products found"
      :sort-key="sortKey"
      :sort-dir="sortDir"
      @sort="handleSort"
    >
      <tr v-for="p in inv.products" :key="p.id" class="cursor-pointer hover:bg-gray-50">
        <td class="px-3 py-2.5">
          <RouterLink :to="`/inventory/products/${p.id}`" class="font-medium text-blue-700 hover:underline">
            {{ p.name }}
          </RouterLink>
        </td>
        <td class="px-3 py-2.5 text-gray-600">{{ p.brand_name || '—' }}</td>
        <td class="px-3 py-2.5 text-gray-600">{{ p.category_name || '—' }}</td>
        <td class="px-3 py-2.5 font-mono text-xs text-gray-500">{{ p.sku }}</td>
        <td class="px-3 py-2.5 text-right">
          <span :class="p.stock_qty <= p.reorder_level ? 'text-red-600 font-semibold' : 'text-gray-700'">
            {{ p.stock_qty ?? '—' }}
          </span>
        </td>
        <td class="px-3 py-2.5 text-right">
          <MoneyDisplay :value="p.sell_price" />
        </td>
        <td class="px-3 py-2.5 text-right">
          <MoneyDisplay :value="p.cost_price" :mask="!perms.canViewCost.value" />
        </td>
        <td class="px-3 py-2.5 text-right">
          <button class="text-xs text-blue-600 hover:underline" @click.stop="openEdit(p)">Edit</button>
        </td>
      </tr>
    </AppTable>

    <AppPagination
      :current-page="pg.currentPage.value"
      :total-pages="pg.totalPages.value"
      :total-count="pg.totalCount.value"
      :page-size="pg.pageSize.value"
      @page="pg.goTo"
    />

    <ProductFormModal
      :open="showForm"
      :product="editProduct"
      @close="showForm = false"
      @saved="onSaved"
    />
  </div>
</template>
