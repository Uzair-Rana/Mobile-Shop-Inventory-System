import { defineStore } from 'pinia'
import { ref } from 'vue'
import { inventoryApi } from '@/api/inventory'
import { useUiStore } from './ui'

export const useInventoryStore = defineStore('inventory', () => {
    const ui = useUiStore()

    const products = ref([])
    const units = ref([])
    const accessories = ref([])
    const categories = ref([])
    const brands = ref([])
    const lowStockItems = ref([])
    const loading = ref(false)
    const pagination = ref({ count: 0, next: null, previous: null })

    async function fetchProducts(params = {}) {
        loading.value = true
        try {
            const res = await inventoryApi.listProducts(params)
            products.value = res.data.results ?? res.data
            pagination.value = { count: res.data.count, next: res.data.next, previous: res.data.previous }
        } catch (e) {
            ui.toastError(e.displayMessage || 'Failed to load products')
        } finally { loading.value = false }
    }

    async function fetchUnits(params = {}) {
        loading.value = true
        try {
            const res = await inventoryApi.listUnits(params)
            units.value = res.data.results ?? res.data
        } catch (e) {
            ui.toastError(e.displayMessage || 'Failed to load units')
        } finally { loading.value = false }
    }

    async function fetchAccessories(params = {}) {
        loading.value = true
        try {
            const res = await inventoryApi.listAccessories(params)
            accessories.value = res.data.results ?? res.data
        } catch (e) {
            ui.toastError(e.displayMessage || 'Failed to load accessories')
        } finally { loading.value = false }
    }

    async function fetchCategories() {
        const res = await inventoryApi.listCategories()
        categories.value = res.data.results ?? res.data
    }

    async function fetchBrands() {
        const res = await inventoryApi.listBrands()
        brands.value = res.data.results ?? res.data
    }

    async function fetchLowStock() {
        const res = await inventoryApi.listLowStock()
        lowStockItems.value = res.data.results ?? res.data
    }

    async function scanItem(query) {
        const res = await inventoryApi.scanLookup(query)
        return res.data  // { type: 'unit'|'accessory', ...product }
    }

    return {
        products, units, accessories, categories, brands, lowStockItems,
        loading, pagination,
        fetchProducts, fetchUnits, fetchAccessories, fetchCategories, fetchBrands,
        fetchLowStock, scanItem,
    }
})
