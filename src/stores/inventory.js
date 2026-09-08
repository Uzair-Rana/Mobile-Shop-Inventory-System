import { defineStore } from 'pinia'
import { ref } from 'vue'
import { inventoryApi } from '@/api/inventory'
import { useUiStore } from './ui'

export const useInventoryStore = defineStore('inventory', () => {
    const ui = useUiStore()

    const loading = ref(false)
    const products = ref([])
    const units = ref([])
    const accessories = ref([])
    const lowStockItems = ref([])
    const categories = ref([])
    const brands = ref([])
    const pagination = ref({ count: 0, next: null, previous: null })

    function _unpack(data) {
        // DRF returns { count, results } or plain array
        if (Array.isArray(data)) return { results: data, count: data.length }
        return { results: data.results || [], count: data.count || 0 }
    }

    async function fetchProducts(params = {}) {
        loading.value = true
        try {
            const { data } = await inventoryApi.listProducts(params)
            const { results, count } = _unpack(data)
            products.value = results
            pagination.value = { count, next: data.next || null, previous: data.previous || null }
        } catch (e) {
            ui.toastError?.('Failed to load products')
        } finally {
            loading.value = false
        }
    }

    async function fetchUnits(params = {}) {
        loading.value = true
        try {
            const { data } = await inventoryApi.listUnits(params)
            const { results } = _unpack(data)
            units.value = results
        } catch { /* silent */ } finally { loading.value = false }
    }

    async function fetchAccessories(params = {}) {
        loading.value = true
        try {
            const { data } = await inventoryApi.listAccessories(params)
            const { results } = _unpack(data)
            accessories.value = results
        } catch { /* silent */ } finally { loading.value = false }
    }

    async function fetchCategories() {
        try {
            const { data } = await inventoryApi.listCategories()
            const { results } = _unpack(data)
            categories.value = results
        } catch { /* silent */ }
    }

    async function fetchBrands() {
        try {
            const { data } = await inventoryApi.listBrands()
            const { results } = _unpack(data)
            brands.value = results
        } catch { /* silent */ }
    }

    async function fetchLowStock(params = {}) {
        try {
            const { data } = await inventoryApi.listLowStock(params)
            const { results } = _unpack(data)
            lowStockItems.value = results
        } catch { /* silent */ }
    }

    async function scanItem(query) {
        const { data } = await inventoryApi.scanLookup(query)
        return data
    }

    return {
        products, units, accessories, lowStockItems,
        categories, brands, loading, pagination,
        fetchProducts, fetchUnits, fetchAccessories,
        fetchCategories, fetchBrands, fetchLowStock, scanItem,
    }
})
