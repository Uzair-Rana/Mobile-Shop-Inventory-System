export const purchaseOrderFixtures = [
    { id: 1, po_number: 'PO-001', supplier_id: 1, supplier_name: 'Telemart Distributors', status: 'received', total_amount: 65000, amount_paid: 65000, line_count: 1, created_at: '2026-07-10T09:00:00Z', expected_delivery: '2026-07-12T00:00:00Z', notes: 'First batch Samsung' },
    { id: 2, po_number: 'PO-002', supplier_id: 1, supplier_name: 'Telemart Distributors', status: 'received', total_amount: 220000, amount_paid: 220000, line_count: 1, created_at: '2026-07-20T09:00:00Z', expected_delivery: '2026-07-22T00:00:00Z', notes: '' },
    { id: 3, po_number: 'PO-003', supplier_id: 2, supplier_name: 'Lahore Mobile Hub', status: 'partial', total_amount: 45000, amount_paid: 20000, line_count: 3, created_at: '2026-08-15T09:00:00Z', expected_delivery: '2026-08-20T00:00:00Z', notes: 'Mixed accessories' },
    { id: 4, po_number: 'PO-004', supplier_id: 1, supplier_name: 'Telemart Distributors', status: 'ordered', total_amount: 195000, amount_paid: 0, line_count: 1, created_at: '2026-08-25T10:00:00Z', expected_delivery: '2026-09-02T00:00:00Z', notes: 'iPhone 14 batch' },
    { id: 5, po_number: 'PO-005', supplier_id: 3, supplier_name: 'Baseus Pakistan', status: 'draft', total_amount: 28000, amount_paid: 0, line_count: 4, created_at: '2026-08-28T09:00:00Z', expected_delivery: null, notes: 'Accessories restock' },
]

export const poLineFixtures = {
    3: [
        { id: 1, po_id: 3, product_id: 1, product_name: 'Samsung Type-C Charger 25W', qty_ordered: 20, qty_received: 8, unit_cost: 900, received: false },
        { id: 2, po_id: 3, product_id: 2, product_name: 'iPhone Lightning Cable 1m', qty_ordered: 15, qty_received: 0, unit_cost: 500, received: false },
        { id: 3, po_id: 3, product_id: 14, product_name: 'Type-C Magnetic Cable', qty_ordered: 25, qty_received: 18, unit_cost: 350, received: false },
    ],
    4: [
        { id: 4, po_id: 4, product_id: 7, product_name: 'Apple iPhone 14', qty_ordered: 1, qty_received: 0, unit_cost: 195000, received: false },
    ],
}
