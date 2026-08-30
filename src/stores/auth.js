import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { PERMISSIONS } from '@/utils/constants'
import { userFixtures } from '@/api/mock/db/fixtures/users'
import { branchFixtures } from '@/api/mock/db/fixtures/branches'

export const useAuthStore = defineStore('auth', () => {
    const user = ref(null)
    const token = ref(localStorage.getItem('devnest_token') || null)
    const loading = ref(false)
    const error = ref(null)

    const isLoggedIn = computed(() => !!token.value && !!user.value)
    const permissions = computed(() => new Set(user.value?.permissions || []))

    const activeBranch = computed(() => {
        if (!user.value) return null
        const branchId = user.value.branches?.[0] || 1
        return branchFixtures.find(b => b.id === branchId) || branchFixtures[0]
    })

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

    /** Mock login — checks against userFixtures */
    async function login(credentials) {
        loading.value = true
        error.value = null
        try {
            // Simulate network delay
            await new Promise(r => setTimeout(r, 200))

            const found = userFixtures.find(u =>
                u.username === credentials.username &&
                u.password === credentials.password &&
                u.is_active !== false
            )

            if (!found) {
                const err = new Error('Invalid credentials')
                err.displayMessage = 'Invalid username or password.'
                throw err
            }

            const mockToken = `mock_token_${found.id}_${Date.now()}`
            token.value = mockToken
            localStorage.setItem('devnest_token', mockToken)

            // Store user without password
            const { password: _pw, ...safeUser } = found
            user.value = safeUser
            localStorage.setItem('devnest_user', JSON.stringify(safeUser))

        } catch (e) {
            error.value = e.displayMessage || 'Login failed'
            throw e
        } finally {
            loading.value = false
        }
    }

    /** Switch active mock user (for demo role switcher) */
    function switchUser(userId) {
        const found = userFixtures.find(u => u.id === Number(userId))
        if (!found) return
        const { password: _pw, ...safeUser } = found
        user.value = safeUser
        localStorage.setItem('devnest_user', JSON.stringify(safeUser))
        const mockToken = `mock_token_${found.id}_${Date.now()}`
        token.value = mockToken
        localStorage.setItem('devnest_token', mockToken)
    }

    async function fetchMe() {
        // In mock mode, restore from localStorage or auto-login as first user
        const stored = localStorage.getItem('devnest_user')
        if (stored) {
            try { user.value = JSON.parse(stored) } catch { /* ignore */ }
        }
        // No stored session — auto-login as superuser for demo
        if (!user.value) {
            const { password: _pw, ...safeUser } = userFixtures[0]
            user.value = safeUser
            const mockToken = `mock_token_${safeUser.id}_${Date.now()}`
            token.value = mockToken
            localStorage.setItem('devnest_token', mockToken)
            localStorage.setItem('devnest_user', JSON.stringify(safeUser))
        }
    }

    async function logout() {
        token.value = null
        user.value = null
        localStorage.removeItem('devnest_token')
        localStorage.removeItem('devnest_user')
    }

    async function init() {
        // Always ensure a user is set — auto-login if nothing in storage
        try { await fetchMe() } catch { /* ignore */ }
    }

    return {
        user, token, loading, error,
        isLoggedIn, permissions, activeBranch,
        canViewCost, canViewProfit, canVoidInvoices, canManageUsers, canManageDiscounts,
        hasPermission, login, logout, fetchMe, init, switchUser,
    }
})
