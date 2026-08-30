export const transferFixtures = [
    { id: 1, transfer_number: 'TRF-001', from_branch_id: 1, from_branch_name: 'Main Store', to_branch_id: 2, to_branch_name: 'Warehouse', status: 'received', line_count: 2, created_by: 'admin', created_at: '2026-08-15T10:00:00Z', dispatched_at: '2026-08-15T14:00:00Z', received_at: '2026-08-16T10:00:00Z', notes: 'Stock rebalance' },
    { id: 2, transfer_number: 'TRF-002', from_branch_id: 2, from_branch_name: 'Warehouse', to_branch_id: 1, to_branch_name: 'Main Store', status: 'dispatched', line_count: 1, created_by: 'admin', created_at: '2026-08-27T09:00:00Z', dispatched_at: '2026-08-27T11:00:00Z', received_at: null, notes: 'Urgent request' },
    { id: 3, transfer_number: 'TRF-003', from_branch_id: 1, from_branch_name: 'Main Store', to_branch_id: 2, to_branch_name: 'Warehouse', status: 'pending', line_count: 3, created_by: 'manager', created_at: '2026-08-28T09:00:00Z', dispatched_at: null, received_at: null, notes: '' },
]
