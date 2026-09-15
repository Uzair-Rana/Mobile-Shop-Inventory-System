/**
 * Permission checking utilities for role-based access control
 */

const roleDefinitions = {
  owner: {
    name: 'Shop Owner / Super Admin',
    description: 'Unrestricted access to all modules',
  },
  cashier: {
    name: 'Salesperson / Cashier',
    description: 'Limited to POS, cash management, and customer inquiry',
  },
  technician: {
    name: 'Technician / Repair Desk',
    description: 'Limited to repair jobs and related functions',
  },
}

/**
 * Check if a user has a specific permission
 * @param {Object} user - User object with permissions array
 * @param {string} permission - Permission string to check (e.g., 'pos.create', 'sales.void')
 * @returns {boolean} True if user has permission
 */
export function hasPermission(user, permission) {
  if (!user) return false
  if (user.is_superuser) return true // Super admin has all permissions
  return user.permissions && user.permissions.includes(permission)
}

/**
 * Check if a user has ANY of the specified permissions
 * @param {Object} user - User object with permissions array
 * @param {string[]} permissions - Array of permission strings
 * @returns {boolean} True if user has at least one permission
 */
export function hasAnyPermission(user, permissions) {
  if (!user) return false
  if (user.is_superuser) return true
  return permissions.some(p => user.permissions?.includes(p))
}

/**
 * Check if a user has ALL of the specified permissions
 * @param {Object} user - User object with permissions array
 * @param {string[]} permissions - Array of permission strings
 * @returns {boolean} True if user has all permissions
 */
export function hasAllPermissions(user, permissions) {
  if (!user) return false
  if (user.is_superuser) return true
  return permissions.every(p => user.permissions?.includes(p))
}

/**
 * Get user role definition
 * @param {Object} user - User object with role
 * @returns {Object} Role definition
 */
export function getRoleDefinition(user) {
  return roleDefinitions[user?.role] || { name: 'Unknown', description: 'Unknown role' }
}

/**
 * Check if action is allowed for user role
 * Business logic checks beyond basic permissions
 */
export const accessControl = {
  // ── Inventory ──
  viewProductCost: (user) => hasPermission(user, 'inventory.view_cost'),
  createProduct: (user) => hasPermission(user, 'inventory.create'),
  editProduct: (user) => hasPermission(user, 'inventory.edit'),
  deleteProduct: (user) => hasPermission(user, 'inventory.delete'),

  // ── POS & Sales ──
  viewPOS: (user) => hasPermission(user, 'pos.view'),
  createPOSSale: (user) => hasPermission(user, 'pos.create'),
  voidSale: (user) => hasPermission(user, 'sales.void'),
  viewSaleCost: (user) => hasPermission(user, 'sales.view_cost'),
  exportSales: (user) => hasPermission(user, 'sales.export'),

  // ── Approvals ──
  approveVoid: (user) => hasPermission(user, 'approve_void'),
  approveReversal: (user) => hasPermission(user, 'approve_reversal'),
  approveDiscount: (user) => hasPermission(user, 'approve_discount'),

  // ── Reports ──
  viewProfitReport: (user) => hasPermission(user, 'reports.view_profit'),
  viewCostReport: (user) => hasPermission(user, 'reports.view_cost'),
  viewAuditLog: (user) => hasPermission(user, 'admin.view_audit_log'),

  // ── Cash Management ──
  reconcileCash: (user) => hasPermission(user, 'cash.session.reconcile'),

  // ── Repairs ──
  viewRepairs: (user) => hasPermission(user, 'repair.view'),
  createRepair: (user) => hasPermission(user, 'repair.create'),
  editRepair: (user) => hasPermission(user, 'repair.edit'),
  printServiceSlip: (user) => hasPermission(user, 'repair.service_slip_print'),
  allocateParts: (user) => hasPermission(user, 'repair.parts.allocate'),

  // ── Admin ──
  manageUsers: (user) => hasPermission(user, 'admin.manage_users'),
  manageRoles: (user) => hasPermission(user, 'admin.manage_roles'),
  viewAuditTrail: (user) => hasPermission(user, 'admin.view_audit_log'),
}

/**
 * Get user's accessible modules
 * @param {Object} user - User object
 * @returns {Object} Object with module access flags
 */
export function getAccessibleModules(user) {
  return {
    inventory: hasPermission(user, 'inventory.view'),
    pos: hasPermission(user, 'pos.view'),
    sales: hasPermission(user, 'sales.view'),
    purchases: hasPermission(user, 'purchase.view'),
    repairs: hasPermission(user, 'repair.view'),
    customers: hasPermission(user, 'customer.view'),
    installments: hasPermission(user, 'installment.view'),
    reports: hasPermission(user, 'reports.view'),
    admin: hasPermission(user, 'admin.view'),
    cash: hasPermission(user, 'cash.session.view'),

    // Visibility of sensitive data
    canViewCost: hasPermission(user, 'inventory.view_cost'),
    canViewProfit: hasPermission(user, 'reports.view_profit'),
    canViewAuditLog: hasPermission(user, 'admin.view_audit_log'),
  }
}

/**
 * Role-specific helpers
 */
export const roleHelpers = {
  isOwner: (user) => user?.is_superuser === true,
  isCashier: (user) => user?.role === 'cashier',
  isTechnician: (user) => user?.role === 'technician',
  isManager: (user) => user?.role === 'manager',
}
