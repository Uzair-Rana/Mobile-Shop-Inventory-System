import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
    // ── No login gate: auto-set a superuser session so the app loads directly ──
    const _defaultUser = {
        id: 1,
        username: 'admin',
        full_name: 'Administrator',
        role_display: 'Admin',
        is_superuser: true,
        permissions: [],   // superuser bypasses all checks
        branches: [1],
    }

    const user = ref(JSON.parse(localStorage.getItem('devnest_user') || 'null') || _defaultUser)
    const token = ref(localStorage.getItem('devnest_token') || 'local-session')
    const loading = ref(false)
    const error = ref(null)

    // Always logged in — no redirect to /login
    const isLoggedIn = computed(() => true)
    const permissions = computed(() => new Set(user.value?.permissions || []))

    function hasPermission(perm) {
        if (!user.value) return true       // fail-open locally
        if (user.value.is_superuser) return true
        return permissions.value.has(perm)
    }

    const canViewCost = computed(() => true)
    const canViewProfit = computed(() => true)
    const canVoidInvoices = computed(() => true)
    const canManageUsers = computed(() => true)
    const canManageDiscounts = computed(() => true)

    async function init() {
        // Persist defaults so X-Branch-ID gets set
        if (!localStorage.getItem('devnest_user')) {
            localStorage.setItem('devnest_user', JSON.stringify(_defaultUser))
        }
        if (!localStorage.getItem('devnest_token')) {
            localStorage.setItem('devnest_token', 'local-session')
        }
        if (!localStorage.getItem('devnest_branch_id')) {
            localStorage.setItem('devnest_branch_id', '1')
        }
    }

    async function logout() {
        // No-op in no-login mode — just reload
        window.location.reload()
    }

    return {
        user, token, loading, error,
        isLoggedIn, permissions,
        canViewCost, canViewProfit, canVoidInvoices, canManageUsers, canManageDiscounts,
        hasPermission, init, logout,
    }
})
