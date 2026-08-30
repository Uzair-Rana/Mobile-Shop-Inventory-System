export const deviceFixtures = [
    { id: 1, imei1: '352099001761481', imei2: '352099001761482', serial: 'SN00100001', brand: 'Samsung', model: 'Galaxy A54', condition: 'Grade A', pta_status: 'PTA Approved', lifecycle_state: 'in_stock', branch_id: 1, cost_price: 65000, sell_price: 85000, created_at: '2026-07-10T10:00:00Z' },
    { id: 2, imei1: '352099001761483', imei2: null, serial: 'SN00100002', brand: 'Apple', model: 'iPhone 13', condition: 'Grade A', pta_status: 'PTA Approved', lifecycle_state: 'in_stock', branch_id: 1, cost_price: 155000, sell_price: 185000, created_at: '2026-07-12T11:00:00Z' },
    { id: 3, imei1: '352099001761484', imei2: null, serial: 'SN00100003', brand: 'Xiaomi', model: 'Redmi Note 12', condition: 'Grade B', pta_status: 'Non-PTA', lifecycle_state: 'in_stock', branch_id: 1, cost_price: 28000, sell_price: 38000, created_at: '2026-07-15T09:00:00Z' },
    { id: 4, imei1: '352099001761485', imei2: '352099001761486', serial: 'SN00100004', brand: 'Samsung', model: 'Galaxy S23', condition: 'Grade A', pta_status: 'PTA Approved', lifecycle_state: 'sold', branch_id: 1, cost_price: 185000, sell_price: 220000, created_at: '2026-07-20T08:00:00Z' },
    { id: 5, imei1: '352099001761487', imei2: null, serial: 'SN00100005', brand: 'Oppo', model: 'Reno 8', condition: 'Grade A', pta_status: 'PTA Approved', lifecycle_state: 'in_stock', branch_id: 2, cost_price: 52000, sell_price: 70000, created_at: '2026-07-22T14:00:00Z' },
    { id: 6, imei1: '352099001761488', imei2: null, serial: 'SN00100006', brand: 'Vivo', model: 'Y21', condition: 'Grade C', pta_status: 'Non-PTA', lifecycle_state: 'in_repair', branch_id: 1, cost_price: 18000, sell_price: 25000, created_at: '2026-08-01T10:00:00Z' },
    { id: 7, imei1: '352099001761489', imei2: null, serial: 'SN00100007', brand: 'Apple', model: 'iPhone 14', condition: 'Grade A', pta_status: 'PTA Approved', lifecycle_state: 'in_stock', branch_id: 1, cost_price: 195000, sell_price: 230000, created_at: '2026-08-05T09:00:00Z' },
    { id: 8, imei1: '352099001761490', imei2: '352099001761491', serial: 'SN00100008', brand: 'Samsung', model: 'Galaxy A34', condition: 'Grade A', pta_status: 'Non-PTA', lifecycle_state: 'reserved', branch_id: 1, cost_price: 48000, sell_price: 62000, created_at: '2026-08-10T11:00:00Z' },
    { id: 9, imei1: '352099001761492', imei2: null, serial: 'SN00100009', brand: 'Huawei', model: 'Nova 10', condition: 'Grade B', pta_status: 'PTA Approved', lifecycle_state: 'in_stock', branch_id: 2, cost_price: 72000, sell_price: 90000, created_at: '2026-08-12T13:00:00Z' },
    { id: 10, imei1: '352099001761493', imei2: null, serial: 'SN00100010', brand: 'Xiaomi', model: '13 Pro', condition: 'Grade A', pta_status: 'PTA Approved', lifecycle_state: 'in_stock', branch_id: 1, cost_price: 88000, sell_price: 110000, created_at: '2026-08-15T10:00:00Z' },
]

export const deviceTimelineFixtures = {
    1: [
        { id: 1, device_id: 1, type: 'acquisition', timestamp: '2026-07-10T10:00:00Z', actor: 'admin', title: 'Acquired from supplier', detail: 'Purchase Order #PO-001, Cost: Rs. 65,000' },
        { id: 2, device_id: 1, type: 'inspection', timestamp: '2026-07-10T11:00:00Z', actor: 'manager', title: 'Inspection passed — Grade A', detail: 'Screen: OK, Battery: 95%, Body: No damage' },
        { id: 3, device_id: 1, type: 'price_change', timestamp: '2026-07-15T09:00:00Z', actor: 'admin', title: 'Sell price updated', detail: 'Old: Rs. 80,000 → New: Rs. 85,000, Reason: Market adjustment' },
    ],
    4: [
        { id: 4, device_id: 4, type: 'acquisition', timestamp: '2026-07-20T08:00:00Z', actor: 'admin', title: 'Acquired from supplier', detail: 'Purchase Order #PO-002' },
        { id: 5, device_id: 4, type: 'sale', timestamp: '2026-08-01T14:00:00Z', actor: 'cashier', title: 'Sold — Invoice #INV-0001', detail: 'Customer: Ahmed Ali, Amount: Rs. 220,000' },
    ],
}
