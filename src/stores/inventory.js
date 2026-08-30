import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useMockDataStore } from './mockData'
import { useUiStore } from './ui'

export const useInventoryStore = defineStore('inventory', () => {
    const mock = useMockDataStore()
    const ui = useUiStore()

    const loading = ref(false)

    // Expose mock data reactively
    const products = computed(() => mock.devices)
    const devices = computed(() => mock.devices)
    const accessories = computed(() => mock.accessories)
    const units = computed(() => mock.devices)
    const lowStockItems = computed(() =>
        mock.accessories.filter(a => a.stock_qty <= a.reorder_level)
    )

    const pagination = ref({ count: 0, next: null, previous: null })
    const categories = ref([...new Set(mock.accessories.map(a => a.category).filter(Boolean))])
    const brands = ref([...new Set(mock.devices.map(d => d.brand).filter(Boolean))])

    async function fetchProducts(params = {}) {
        loading.value = true
        await new Promise(r => setTimeout(r, 50))
        loading.value = false
    }

    async function fetchUnits(params = {}) {
        loading.value = true
        await new Promise(r => setTimeout(r, 50))
        loading.value = false
    }

    async function fetchAccessories(params = {}) {
        loading.value = true
        await new Promise(r => setTimeout(r, 50))
        loading.value = false
    }

    async function fetchCategories() { }
    async function fetchBrands() { }
    async function fetchLowStock() { }

    /** Scan lookup: tries IMEI then SKU */
    async function scanItem(query) {
        await new Promise(r => setTimeout(r, 80))
        return mock.scanItem(query)
    }

    return {
        products, units, accessories, devices,
        categories, brands, lowStockItems,
        loading, pagination,
        fetchProducts, fetchUnits, fetchAccessories,
        fetchCategories, fetchBrands, fetchLowStock, scanItem,
    }
})
