/**
 * Router guards for role-based access control
 * Enforces route-level permission checks
 */

import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'

/**
 * Check if user has required permission(s)
 */
function hasPermission(user, permissions) {
  if (!user) return false
  if (user.is_superuser) return true
  const perms = Array.isArray(permissions) ? permissions : [permissions]
  return perms.some(p => user.permissions?.includes(p))
}

/**
 * Main route guard
 */
export async function setupRouteGuards(router) {
  router.beforeEach((to, from, next) => {
    const auth = useAuthStore()
    const ui = useUiStore()
    const user = auth.user

    // Routes that don't require authentication
    if (to.meta.public) {
      next()
      return
    }

    // Check authentication
    if (!user) {
      next('/login')
      return
    }

    // Check role-based access
    if (to.meta.requiresPermission) {
      const required = to.meta.requiresPermission
      if (!hasPermission(user, required)) {
        ui.toastError?.('You do not have permission to access this page')
        next(from.path || '/dashboard')
        return
      }
    }

    // Enforce role-specific module access
    const routeModuleMap = {
      '/pos': 'pos.view',
      '/sales': 'sales.view',
      '/inventory': 'inventory.view',
      '/purchases': 'purchase.view',
      '/repairs': 'repair.view',
      '/customers': 'customer.view',
      '/installments': 'installment.view',
      '/cash': 'cash.session.view',
      '/reports': 'reports.view',
      '/admin': 'admin.view',
      '/settings': 'admin.configure',
    }

    // Check if route requires specific module access
    for (const [path, permission] of Object.entries(routeModuleMap)) {
      if (to.path.startsWith(path)) {
        if (!hasPermission(user, permission)) {
          ui.toastError?.(`Access denied. This role cannot access ${path.slice(1)} module.`)
          next('/dashboard')
          return
        }
        break
      }
    }

    next()
  })

  router.afterEach((to, from) => {
    // You can add analytics, logging, etc. here
  })
}

/**
 * Route-level permission metadata helper
 */
export const routePermissions = {
  // Inventory routes
  inventoryProducts: 'inventory.view',
  inventoryDevices: 'inventory.view',

  // POS routes
  pos: 'pos.view',

  // Sales routes
  sales: 'sales.view',
  salesVoid: 'sales.void',

  // Repair routes
  repairs: 'repair.view',
  repairBoard: 'repair.view',

  // Customer routes
  customers: 'customer.view',

  // Reports
  reports: 'reports.view',
  profitReports: 'reports.view_profit',
  auditLog: 'admin.view_audit_log',

  // Admin routes
  admin: 'admin.view',
  userManagement: 'admin.manage_users',
  roleManagement: 'admin.manage_roles',
}
