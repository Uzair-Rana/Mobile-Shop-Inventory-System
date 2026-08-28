// ─── Device / Inventory Status ────────────────────────────────────────────────
export const DEVICE_STATUS = {
    IN_STOCK: { value: 'in_stock', label: 'In Stock', badge: 'badge-green' },
    SOLD: { value: 'sold', label: 'Sold', badge: 'badge-gray' },
    IN_REPAIR: { value: 'in_repair', label: 'In Repair', badge: 'badge-yellow' },
    RESERVED: { value: 'reserved', label: 'Reserved', badge: 'badge-blue' },
    RETURNED: { value: 'returned', label: 'Returned', badge: 'badge-orange' },
    DEFECTIVE: { value: 'defective', label: 'Defective', badge: 'badge-red' },
    TRANSFERRED: { value: 'transferred', label: 'Transferred', badge: 'badge-purple' },
}

// ─── Repair Job Stages ────────────────────────────────────────────────────────
export const REPAIR_STATUS = {
    RECEIVED: { value: 'received', label: 'Received', badge: 'badge-blue' },
    DIAGNOSED: { value: 'diagnosed', label: 'Diagnosed', badge: 'badge-yellow' },
    WAITING_PARTS: { value: 'waiting_parts', label: 'Waiting Parts', badge: 'badge-orange' },
    IN_PROGRESS: { value: 'in_progress', label: 'In Progress', badge: 'badge-purple' },
    READY: { value: 'ready', label: 'Ready for Pickup', badge: 'badge-green' },
    DELIVERED: { value: 'delivered', label: 'Delivered', badge: 'badge-gray' },
    CANCELLED: { value: 'cancelled', label: 'Cancelled', badge: 'badge-red' },
    UNREPAIRABLE: { value: 'unrepairable', label: 'Unrepairable', badge: 'badge-red' },
}

// ─── Sale / Invoice Status ────────────────────────────────────────────────────
export const INVOICE_STATUS = {
    DRAFT: { value: 'draft', label: 'Draft', badge: 'badge-gray' },
    FINALIZED: { value: 'finalized', label: 'Finalized', badge: 'badge-green' },
    PARTIALLY_PAID: { value: 'partially_paid', label: 'Partially Paid', badge: 'badge-yellow' },
    PAID: { value: 'paid', label: 'Paid', badge: 'badge-green' },
    RETURNED: { value: 'returned', label: 'Returned', badge: 'badge-orange' },
    VOIDED: { value: 'voided', label: 'Voided', badge: 'badge-red' },
}

// ─── Installment Plan Status ──────────────────────────────────────────────────
export const INSTALLMENT_STATUS = {
    ACTIVE: { value: 'active', label: 'Active', badge: 'badge-green' },
    OVERDUE: { value: 'overdue', label: 'Overdue', badge: 'badge-red' },
    COMPLETED: { value: 'completed', label: 'Completed', badge: 'badge-gray' },
    DEFAULTED: { value: 'defaulted', label: 'Defaulted', badge: 'badge-red' },
    CANCELLED: { value: 'cancelled', label: 'Cancelled', badge: 'badge-yellow' },
}

// ─── Purchase Order Status ────────────────────────────────────────────────────
export const PO_STATUS = {
    DRAFT: { value: 'draft', label: 'Draft', badge: 'badge-gray' },
    ORDERED: { value: 'ordered', label: 'Ordered', badge: 'badge-blue' },
    PARTIAL: { value: 'partial', label: 'Partial', badge: 'badge-yellow' },
    RECEIVED: { value: 'received', label: 'Received', badge: 'badge-green' },
    CANCELLED: { value: 'cancelled', label: 'Cancelled', badge: 'badge-red' },
}

// ─── Payment Methods ──────────────────────────────────────────────────────────
export const PAYMENT_METHODS = [
    { value: 'cash', label: 'Cash' },
    { value: 'card', label: 'Card' },
    { value: 'bank_transfer', label: 'Bank Transfer' },
    { value: 'easypaisa', label: 'EasyPaisa' },
    { value: 'jazzcash', label: 'JazzCash' },
    { value: 'cheque', label: 'Cheque' },
    { value: 'installment', label: 'Installment' },
]

// ─── Sync States ──────────────────────────────────────────────────────────────
export const SYNC_STATE = {
    ONLINE: { value: 'online', label: 'Online', color: 'text-green-600', dot: 'bg-green-500' },
    OFFLINE: { value: 'offline', label: 'Offline', color: 'text-red-600', dot: 'bg-red-500' },
    SYNCING: { value: 'syncing', label: 'Syncing', color: 'text-blue-600', dot: 'bg-blue-500' },
    PENDING: { value: 'pending', label: 'Pending', color: 'text-yellow-600', dot: 'bg-yellow-500' },
    ERROR: { value: 'error', label: 'Sync Error', color: 'text-red-600', dot: 'bg-red-500' },
}

// ─── User Permissions (mirror your Django permission codenames) ───────────────
export const PERMISSIONS = {
    VIEW_COST: 'view_cost',
    VIEW_PROFIT: 'view_profit',
    VIEW_REPORTS: 'view_reports',
    MANAGE_USERS: 'manage_users',
    VOID_INVOICES: 'void_invoices',
    MANAGE_DISCOUNTS: 'manage_discounts',
    MANAGE_PURCHASE: 'manage_purchase',
    MANAGE_REPAIRS: 'manage_repairs',
    MANAGE_INSTALLMENTS: 'manage_installments',
}
