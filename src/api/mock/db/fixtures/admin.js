export const roleFixtures = [
    {
        id: 1, name: 'Administrator', description: 'Full system access',
        permissions: [
            'dashboard.view', 'inventory.view', 'inventory.create', 'inventory.edit',
            'inventory.view_cost', 'pos.view', 'pos.create', 'sales.void', 'sales.export',
            'repairs.view', 'repairs.create', 'repairs.edit', 'repairs.approve',
            'purchases.view', 'purchases.create', 'purchases.edit',
            'installments.view', 'installments.create', 'installments.edit',
            'cash.view', 'cash.create', 'customers.view', 'customers.create', 'customers.edit',
            'reports.view', 'reports.export', 'reports.view_profit',
            'transfers.view', 'transfers.create', 'transfers.approve',
            'admin.view', 'admin.configure',
        ],
    },
    {
        id: 2, name: 'Branch Manager', description: 'Branch operations + reports',
        permissions: [
            'dashboard.view', 'inventory.view', 'inventory.create', 'inventory.edit',
            'pos.view', 'pos.create', 'sales.void',
            'repairs.view', 'repairs.create', 'repairs.edit', 'repairs.approve',
            'purchases.view', 'purchases.create',
            'installments.view', 'installments.create',
            'cash.view', 'cash.create', 'customers.view', 'customers.create', 'customers.edit',
            'reports.view', 'reports.view_profit',
            'transfers.view', 'transfers.create',
        ],
    },
    {
        id: 3, name: 'Cashier', description: 'POS and sales only',
        permissions: [
            'dashboard.view', 'inventory.view',
            'pos.view', 'pos.create',
            'repairs.view', 'customers.view', 'customers.create',
            'cash.view', 'cash.create',
        ],
    },
    {
        id: 4, name: 'Technician', description: 'Repairs only',
        permissions: [
            'dashboard.view', 'inventory.view',
            'repairs.view', 'repairs.create', 'repairs.edit',
        ],
    },
]

export const auditLogFixtures = [
    { id: 1, timestamp: '2026-08-28T10:30:00Z', actor: 'admin', action: 'update', entity_type: 'Device', entity_id: '7', changes: { cost_price: { before: 190000, after: 195000 }, reason: 'Supplier price increase' } },
    { id: 2, timestamp: '2026-08-28T10:15:00Z', actor: 'cashier', action: 'create', entity_type: 'Invoice', entity_id: '10', changes: { status: { before: null, after: 'draft' } } },
    { id: 3, timestamp: '2026-08-28T09:45:00Z', actor: 'manager', action: 'void', entity_type: 'Invoice', entity_id: '9', changes: { status: { before: 'finalized', after: 'voided' }, reason: 'Customer changed mind' } },
    { id: 4, timestamp: '2026-08-28T09:00:00Z', actor: 'admin', action: 'login', entity_type: 'User', entity_id: '1', changes: {} },
    { id: 5, timestamp: '2026-08-27T16:00:00Z', actor: 'manager', action: 'update', entity_type: 'RepairJob', entity_id: '9', changes: { status: { before: 'repaired', after: 'ready' } } },
    { id: 6, timestamp: '2026-08-27T14:00:00Z', actor: 'admin', action: 'create', entity_type: 'PurchaseOrder', entity_id: '5', changes: { status: { before: null, after: 'draft' } } },
    { id: 7, timestamp: '2026-08-27T11:00:00Z', actor: 'cashier', action: 'create', entity_type: 'CashSession', entity_id: '1', changes: { status: { before: 'closed', after: 'open' }, opening_amount: 10000 } },
    { id: 8, timestamp: '2026-08-26T15:00:00Z', actor: 'admin', action: 'update', entity_type: 'Role', entity_id: '3', changes: { permissions: { before: ['pos.view'], after: ['pos.view', 'pos.create'] } } },
]
