/**
 * usePermissions — reactive permission checks.
 * Wraps the auth store so components don't need to import the store directly.
 *
 * Usage:
 *   const { can, canViewCost } = usePermissions()
 *   v-if="canViewCost"
 *   v-if="can('void_invoices')"
 */
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

export function usePermissions() {
    const auth = useAuthStore()

    function can(permission) {
        return auth.hasPermission(permission)
    }

    return {
        can,
        canViewCost: computed(() => auth.canViewCost),
        canViewProfit: computed(() => auth.canViewProfit),
        canVoidInvoices: computed(() => auth.canVoidInvoices),
        canManageUsers: computed(() => auth.canManageUsers),
        canManageDiscounts: computed(() => auth.canManageDiscounts),
        isSuperuser: computed(() => !!auth.user?.is_superuser),
    }
}
