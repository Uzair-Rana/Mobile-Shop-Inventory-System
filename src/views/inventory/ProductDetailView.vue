<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { inventoryApi } from '@/api/inventory'
import { usePermissions } from '@/composables/usePermissions'
import { formatDate } from '@/utils/date'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppButton from '@/components/ui/AppButton.vue'
import { DEVICE_STATUS } from '@/utils/constants'

const route  = useRoute()
const router = useRouter()
const perms  = usePermissions()

const product = ref(null)
const units   = ref([])
const loading = ref(true)

onMounted(async () => {
  const [pRes, uRes] = await Promise.all([
    inventoryApi.getProduct(route.params.id),
    inventoryApi.listUnits({ product: route.params.id, page_size: 50 }),
  ])
  product.value = pRes.data
  units.value   = uRes.data.results ?? uRes.data
  loading.value = false
})

function statusObj(val) {
  return Object.values(DEVICE_STATUS).find(s => s.value === val) || { label: val, badge: 'badge-gray' }
}
</script>

<template>
  <div v-if="!loading && product" class="space-y-6">
    <!-- Header -->
    <div class="flex items-start justify-between">
      <div>
        <h2 class="text-xl font-bold text-gray-900">{{ product.name }}</h2>
        <p class="text-sm text-gray-500 mt-0.5">SKU: {{ product.sku }} &nbsp;·&nbsp; {{ product.brand_name }} &nbsp;·&nbsp; {{ product.category_name }}</p>
      </div>
      <AppButton variant="secondary" @click="router.back()">← Back</AppButton>
    </div>

    <!-- Detail cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="card p-4">
        <p class="text-xs text-gray-500 uppercase tracking-wide">Sell Price</p>
        <MoneyDisplay :value="product.sell_price" class="text-xl font-bold text-gray-900 block mt-1" />
      </div>
      <div class="card p-4">
        <p class="text-xs text-gray-500 uppercase tracking-wide">Cost Price</p>
        <MoneyDisplay :value="product.cost_price" :mask="!perms.canViewCost.value" class="text-xl font-bold text-gray-900 block mt-1" />
      </div>
      <div class="card p-4">
        <p class="text-xs text-gray-500 uppercase tracking-wide">Stock</p>
        <p class="text-xl font-bold text-gray-900 mt-1">{{ product.stock_qty ?? '—' }}</p>
      </div>
      <div class="card p-4">
        <p class="text-xs text-gray-500 uppercase tracking-wide">Reorder At</p>
        <p class="text-xl font-bold text-gray-900 mt-1">{{ product.reorder_level }}</p>
      </div>
    </div>

    <!-- IMEI units table -->
    <div class="card">
      <div class="px-4 py-3 border-b border-gray-100 font-semibold text-sm">IMEI / Serial Units ({{ units.length }})</div>
      <table class="table-base">
        <thead><tr>
          <th>IMEI / Serial</th><th>Status</th><th>Received</th><th>Sold</th>
        </tr></thead>
        <tbody>
          <tr v-for="u in units" :key="u.id">
            <td class="font-mono text-xs">{{ u.imei }}</td>
            <td><AppBadge :status="statusObj(u.status)" /></td>
            <td>{{ formatDate(u.received_at) }}</td>
            <td>{{ formatDate(u.sold_at) }}</td>
          </tr>
          <tr v-if="units.length === 0">
            <td colspan="4" class="py-8 text-center text-gray-400 text-sm">No units in stock</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
  <div v-else class="text-center py-20 text-gray-400">Loading…</div>
</template>
