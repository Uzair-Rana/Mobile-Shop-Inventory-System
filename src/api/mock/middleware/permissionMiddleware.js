/**
 * Permission middleware for enforcing role-based access control
 * This middleware checks user permissions for each API request
 */

import { HttpResponse } from 'msw'
import { hasPermission, roleHelpers } from '../db/permissions.js'

/**
 * Create a permission check function
 * @param {string|string[]} requiredPermissions - Permission(s) required
 * @returns {Function} Middleware function
 */
export function requirePermission(requiredPermissions) {
  return (user) => {
    if (!user) return false
    if (user.is_superuser) return true

    const permissions = Array.isArray(requiredPermissions)
      ? requiredPermissions
      : [requiredPermissions]

    return permissions.some(p => user.permissions?.includes(p))
  }
}

/**
 * Create a forbidden response
 * @param {string} message - Error message
 * @returns {HttpResponse} 403 Forbidden response
 */
export function forbiddenResponse(message = 'Permission denied') {
  return HttpResponse.json(
    {
      detail: message,
      code: 'permission_denied',
    },
    { status: 403 }
  )
}

/**
 * Check permission and return error if not allowed
 * @param {Object} user - User object
 * @param {string|string[]} permissions - Required permission(s)
 * @returns {null|HttpResponse} null if allowed, HttpResponse if denied
 */
export function checkPermission(user, permissions) {
  const check = requirePermission(permissions)
  if (!check(user)) {
    return forbiddenResponse('You do not have permission to perform this action')
  }
  return null
}

/**
 * Check if user can view cost/profit data
 */
export function canViewCost(user) {
  return hasPermission(user, 'inventory.view_cost') || roleHelpers.isOwner(user)
}

export function checkCostAccess(user) {
  if (!canViewCost(user)) {
    return forbiddenResponse('You do not have permission to view cost information')
  }
  return null
}

/**
 * Enforce role-specific access
 */
export const roleEnforcement = {
  // Owner has unrestricted access
  ownerOnly: (user) => roleHelpers.isOwner(user),

  // Cashier can only view their own sales/cash
  cashierOnly: (user) => roleHelpers.isCashier(user),

  // Technician can only access repair functions
  technicianOnly: (user) => roleHelpers.isTechnician(user),

  // Only Owner/Manager can view profit
  managerAbove: (user) => {
    return roleHelpers.isOwner(user) || user?.role === 'manager'
  },
}

/**
 * Filter response data based on user permissions
 * Removes sensitive fields for users without appropriate permissions
 */
export function filterSensitiveData(data, user) {
  if (!data) return data

  const filtered = { ...data }

  // Hide cost fields from non-cost-viewing users
  if (!canViewCost(user)) {
    if (Array.isArray(filtered)) {
      return filtered.map(item => {
        const { cost_price, wholesale_cost, purchase_cost, ...rest } = item
        return rest
      })
    } else {
      const { cost_price, wholesale_cost, purchase_cost, ...rest } = filtered
      return rest
    }
  }

  return filtered
}

/**
 * Filter array response based on user permissions
 */
export function filterArrayResponse(items, user, filterFn) {
  if (!Array.isArray(items)) return items
  return items.map(item => filterSensitiveData(item, user))
}
