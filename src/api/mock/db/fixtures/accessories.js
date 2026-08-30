export const accessoryFixtures = [
    { id: 1, name: 'Samsung Type-C Charger 25W', sku: 'ACC-CHR-001', category: 'Chargers', brand: 'Samsung', sell_price: 1800, cost_price: 900, stock_qty: 8, reorder_level: 10, branch_id: 1, last_movement: '2026-08-20T10:00:00Z' },
    { id: 2, name: 'iPhone Lightning Cable 1m', sku: 'ACC-CBL-001', category: 'Cables', brand: 'Apple', sell_price: 1200, cost_price: 500, stock_qty: 3, reorder_level: 5, branch_id: 1, last_movement: '2026-08-25T09:00:00Z' },
    { id: 3, name: 'Tempered Glass Samsung A54', sku: 'ACC-TG-001', category: 'Accessories', brand: 'Generic', sell_price: 300, cost_price: 80, stock_qty: 22, reorder_level: 10, branch_id: 1, last_movement: '2026-08-27T11:00:00Z' },
    { id: 4, name: 'Silicone Case iPhone 13', sku: 'ACC-CSE-001', category: 'Cases', brand: 'Apple', sell_price: 800, cost_price: 250, stock_qty: 1, reorder_level: 5, branch_id: 1, last_movement: '2026-08-10T08:00:00Z' },
    { id: 5, name: 'Wireless Earbuds Galaxy', sku: 'ACC-EAR-001', category: 'Audio', brand: 'Samsung', sell_price: 4500, cost_price: 2200, stock_qty: 6, reorder_level: 4, branch_id: 1, last_movement: '2026-08-22T14:00:00Z' },
    { id: 6, name: 'Screen Protector Xiaomi 12', sku: 'ACC-TG-002', category: 'Accessories', brand: 'Generic', sell_price: 250, cost_price: 60, stock_qty: 0, reorder_level: 8, branch_id: 1, last_movement: '2026-07-01T10:00:00Z' },
    { id: 7, name: 'USB-C Hub 4-in-1', sku: 'ACC-HUB-001', category: 'Accessories', brand: 'Baseus', sell_price: 2200, cost_price: 1100, stock_qty: 4, reorder_level: 3, branch_id: 2, last_movement: '2026-08-18T12:00:00Z' },
    { id: 8, name: 'Power Bank 10000mAh', sku: 'ACC-PB-001', category: 'Power', brand: 'Anker', sell_price: 3500, cost_price: 1800, stock_qty: 9, reorder_level: 5, branch_id: 1, last_movement: '2026-08-26T15:00:00Z' },
    { id: 9, name: 'Cleaning Kit Universal', sku: 'ACC-CLN-001', category: 'Accessories', brand: 'Generic', sell_price: 400, cost_price: 120, stock_qty: 2, reorder_level: 5, branch_id: 1, last_movement: '2026-06-15T10:00:00Z' },
    { id: 10, name: 'Fast Charge Adapter 65W', sku: 'ACC-CHR-002', category: 'Chargers', brand: 'Baseus', sell_price: 2800, cost_price: 1400, stock_qty: 14, reorder_level: 6, branch_id: 2, last_movement: '2026-08-28T09:00:00Z' },
    { id: 11, name: 'Back Cover Oppo Reno 8', sku: 'ACC-CSE-002', category: 'Cases', brand: 'Generic', sell_price: 350, cost_price: 100, stock_qty: 0, reorder_level: 4, branch_id: 1, last_movement: '2026-05-20T10:00:00Z' },
    { id: 12, name: 'Battery Samsung A54 OEM', sku: 'ACC-BAT-001', category: 'Parts', brand: 'Samsung', sell_price: 2500, cost_price: 1200, stock_qty: 5, reorder_level: 3, branch_id: 1, last_movement: '2026-08-15T11:00:00Z' },
    { id: 13, name: 'Screen Assembly iPhone 13', sku: 'ACC-SCR-001', category: 'Parts', brand: 'Apple', sell_price: 18000, cost_price: 9000, stock_qty: 2, reorder_level: 2, branch_id: 1, last_movement: '2026-08-20T10:00:00Z' },
    { id: 14, name: 'Type-C Magnetic Cable', sku: 'ACC-CBL-002', category: 'Cables', brand: 'Baseus', sell_price: 900, cost_price: 350, stock_qty: 18, reorder_level: 8, branch_id: 1, last_movement: '2026-08-27T16:00:00Z' },
    { id: 15, name: 'Selfie Ring Light Clip', sku: 'ACC-MISC-001', category: 'Accessories', brand: 'Generic', sell_price: 600, cost_price: 180, stock_qty: 0, reorder_level: 3, branch_id: 1, last_movement: '2026-04-10T10:00:00Z' },
]

export const movementFixtures = [
    { id: 1, accessory_id: 1, date: '2026-08-20T10:00:00Z', type: 'purchase', qty_change: +20, reason: 'PO-003 received', actor: 'admin' },
    { id: 2, accessory_id: 1, date: '2026-08-22T14:00:00Z', type: 'sale', qty_change: -5, reason: 'Invoice INV-0010', actor: 'cashier' },
    { id: 3, accessory_id: 1, date: '2026-08-25T11:00:00Z', type: 'sale', qty_change: -7, reason: 'Invoice INV-0015', actor: 'cashier' },
    { id: 4, accessory_id: 2, date: '2026-08-10T09:00:00Z', type: 'purchase', qty_change: +10, reason: 'Direct purchase', actor: 'manager' },
    { id: 5, accessory_id: 2, date: '2026-08-25T09:00:00Z', type: 'sale', qty_change: -7, reason: 'Invoice INV-0012', actor: 'cashier' },
    { id: 6, accessory_id: 6, date: '2026-07-01T10:00:00Z', type: 'sale', qty_change: -8, reason: 'Invoice INV-0003', actor: 'cashier' },
]
