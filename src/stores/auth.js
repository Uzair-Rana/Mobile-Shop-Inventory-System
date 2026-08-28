import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import { PERMISSIONS } from '@/utils/constants'

export const useAuthStore = defineStore('auth', () => {
    const user = ref(null)
    const token = ref(localStorage.getItem('devnest_token') || null)
    const loading = ref(false)
    const error = ref(null)

    const isLoggedIn = computed(() => !!token.value && !!user.value)
    const permissions = computed(() => new Set(user.value?.permissions || []))

    function hasPermission(perm) {
        if (!user.value) return false
        if (user.value.is_superuser) return true
        return permissions.value.has(perm)
    }

    const canViewCost = computed(() => hasPermission(PERMISSIONS.VIEW_COST))
    const canViewProfit = computed(() => hasPermission(PERMISSIONS.VIEW_PROFIT))
    const canVoidInvoices = computed(() => hasPermission(PERMISSIONS.VOID_INVOICES))
    const canManageUsers = computed(() => hasPermission(PERMISSIONS.MANAGE_USERS))
    const canManageDiscounts = computed(() => hasPermission(PERMISSIONS.MANAGE_DISCOUNTS))

    async function login(credentials) {
        loading.value = true
        error.value = null
        try {
            const res = await authApi.login(credentials)
            token.value = res.data.token
            localStorage.setItem('devnest_token', token.value)
            await fetchMe()
        } catch (e) {
            error.value = e.displayMessage || 'Login failed'
            throw e
        } finally {
            loading.value = false
        }
    }

    async function fetchMe() {
        const res = await authApi.me()
        user.value = res.data
    }

    async function logout() {
        try { await authApi.logout() } catch { /* ignore */ }
        token.value = null
        user.value = null
        localStorage.removeItem('devnest_token')
    }

    async function init() {
        if (token.value && !user.value) {
            try { await fetchMe() } catch { await logout() }
        }
    }

    return {
        user, token, loading, error,
        isLoggedIn, permissions,
        canViewCost, canViewProfit, canVoidInvoices, canManageUsers, canManageDiscounts,
        hasPermission, login, logout, fetchMe, init,
    }
})
