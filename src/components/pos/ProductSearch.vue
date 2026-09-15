<script setup>
import { ref, computed, onMounted } from 'vue'
import { useInventoryStore } from '@/stores/inventory'
import { useCartStore } from '@/stores/cart'
import { useUiStore } from '@/stores/ui'
import { inventoryApi } from '@/api/inventory'
import { formatMoney } from '@/utils/money'
import AppButton from '@/components/ui/AppButton.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'

const inv = useInventoryStore()
const cart = useCartStore()
const ui = useUiStore()

const searchQuery = ref('')
const selectedCategory = ref('')
const selectedBrand = ref('')
const searchResults = ref([])
const loading = ref(false)
const showFilters = ref(false)

let searchTimer = null

onMounted(async () => {
  await inv.fetchCategories()
  await inv.fetchBrands()
})

const categoryOptions = computed(() => [
  { value: '', label: 'All Categories' },
  ...inv.categories.map(c => ({ value: c.id, label: c.name }))
])

const brandOptions = computed(() => [
  { value: '', label: 'All Brands' },
  ...inv.brands.map(b => ({ value: b.id, label: b.name }))
])

async function performSearch() {
  if (searchQuery.value.length === 0 && !selectedCategory.value && !selectedBrand.value) {
    searchResults.value = []
    return
  }

  loading.value = true
  try {
    const params = {}
    if (searchQuery.value) params.search = searchQuery.value
    if (selectedCategory.value) params.category_id = selectedCategory.value
    if (selectedBrand.value) params.brand_id = selectedBrand.value

    const { data } = await inventoryApi.listProducts(params)
    const results = Array.isArray(data) ? data : (data.results || [])
    searchResults.value = results
  } catch (e) {
    ui.toastError?.('Search failed')
    searchResults.value = []
  } finally {
    loading.value = false
  }
}

function onSearchInput() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(performSearch, 300)
}

function onFilterChange() {
  performSearch()
}

function addToCart(product) {
  const price = Number(product.price ?? product.sell_price ?? product.selling_price ?? 0)
  if (price === 0) {
    ui.toastWarn?.('Product price not set')
    return
  }

  cart.addItem({
    product_id: product.product_id ?? product.id,
    unit_id: product.unit_id ?? null,
    name: product.name,
    sku: product.sku,
    imei: product.imei ?? null,   // devices pass IMEI → added as a unit; accessories stay null
    price: price
  })
  ui.toastSuccess?.(`${product.name} added to cart`)
}

function getProductImage(product) {
  return product.image || product.photo || null
}
</script>

<template>
  <div class="card p-3 space-y-3">
    <!-- Search Header -->
    <div class="flex items-center justify-between">
      <p class="label">Search Products</p>
      <button
        class="text-xs text-gray-500 hover:text-gray-700"
        @click="showFilters = !showFilters"
        data-no-scanner-refocus
      >
        {{ showFilters ? '▼' : '▶' }} Filters
      </button>
    </div>

    <!-- Search Input -->
    <input
      v-model="searchQuery"
      type="text"
      class="input text-sm w-full"
      placeholder="Search by product name, SKU…"
      autocomplete="off"
      data-no-scanner-refocus
      @input="onSearchInput"
    />

    <!-- Filters (Collapsible) -->
    <div v-if="showFilters" class="space-y-2 pt-2 border-t border-gray-200">
      <div>
        <label class="text-xs text-gray-600 block mb-1">Category</label>
        <select
          v-model="selectedCategory"
          class="input text-sm w-full"
          data-no-scanner-refocus
          @change="onFilterChange"
        >
          <option v-for="opt in categoryOptions" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </option>
        </select>
      </div>
      <div>
        <label class="text-xs text-gray-600 block mb-1">Brand/Company</label>
        <select
          v-model="selectedBrand"
          class="input text-sm w-full"
          data-no-scanner-refocus
          @change="onFilterChange"
        >
          <option v-for="opt in brandOptions" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </option>
        </select>
      </div>
    </div>

    <!-- Search Results -->
    <div class="max-h-64 overflow-y-auto space-y-2">
      <div v-if="loading" class="text-sm text-gray-500 py-2">Searching…</div>
      <div v-else-if="searchResults.length === 0 && searchQuery" class="text-sm text-gray-500 py-2">
        No products found
      </div>
      <div
        v-for="product in searchResults"
        :key="product.id"
        class="flex items-start gap-2 p-2 bg-gray-50 rounded border border-gray-200 hover:bg-blue-50 hover:border-blue-300 transition-colors"
      >
        <!-- Product info -->
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-900 truncate">{{ product.name }}</p>
          <div class="flex items-center gap-2 mt-0.5 flex-wrap">
            <span class="text-xs text-gray-500">{{ product.sku }}</span>
            <span v-if="product.category_name" class="text-xs bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded">
              {{ product.category_name }}
            </span>
            <span v-if="product.brand_name" class="text-xs bg-gray-200 text-gray-700 px-1.5 py-0.5 rounded">
              {{ product.brand_name }}
            </span>
          </div>
        </div>

        <!-- Price + Add button -->
        <div class="flex flex-col items-end gap-1 shrink-0">
          <span class="text-sm font-semibold text-gray-900 money">
            <MoneyDisplay :value="product.price || product.selling_price || 0" />
          </span>
          <AppButton
            size="sm"
            variant="primary"
            data-no-scanner-refocus
            @click="addToCart(product)"
          >
            Add
          </AppButton>
        </div>
      </div>
    </div>
  </div>
</template>
