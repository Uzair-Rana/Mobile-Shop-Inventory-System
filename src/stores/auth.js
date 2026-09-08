import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'

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

    const canViewCost = computed(() => hasPermission('view_cost'))
    const canViewProfit = computed(() => hasPermission('view_profit'))
    const canVoidInvoices = computed(() => hasPermission('void_invoices'))
    const canManageUsers = computed(() => hasPermission('manage_users'))
    const canManageDiscounts = computed(() => hasPermission('discount_override'))

    async function login(credentials) {
        loading.value = true
        error.value = null
        try {
            const { data } = await authApi.login(credentials)

            token.value = data.token
            localStorage.setItem('devnest_token', data.token)
            user.value = data.user
            localStorage.setItem('devnest_user', JSON.stringify(data.user))

            // Persist first branch for X-Branch-ID header
            const firstBranch = data.user?.branches?.[0]
            if (firstBranch) {
                localStorage.setItem('devnest_branch_id', String(firstBranch))
            }
        } catch (e) {
            error.value = e.displayMessage || 'Login failed'
            throw e
        } finally {
            loading.value = false
        }
    }

    async function fetchMe() {
        try {
            const { data } = await authApi.me()
            user.value = data
            localStorage.setItem('devnest_user', JSON.stringify(data))
        } catch {
            // Token expired or invalid — clear session
            token.value = null
            user.value = null
            localStorage.removeItem('devnest_token')
            localStorage.removeItem('devnest_user')
            localStorage.removeItem('devnest_branch_id')
        }
    }

    async function logout() {
        try {
            await authApi.logout()
        } catch { /* ignore — clear locally regardless */ }
        token.value = null
        user.value = null
        localStorage.removeItem('devnest_token')
        localStorage.removeItem('devnest_user')
        localStorage.removeItem('devnest_branch_id')
    }

    async function init() {
        if (!token.value) return   // No stored token — stay on login page

        // Restore user from localStorage instantly (avoids flash)
        const stored = localStorage.getItem('devnest_user')
        if (stored) {
            try { user.value = JSON.parse(stored) } catch { /* ignore */ }
        }

        // Then validate with the server in the background
        await fetchMe()
    }

    return {
        user, token, loading, error,
        isLoggedIn, permissions,
        canViewCost, canViewProfit, canVoidInvoices, canManageUsers, canManageDiscounts,
        hasPermission, login, logout, fetchMe, init,
    }
})
