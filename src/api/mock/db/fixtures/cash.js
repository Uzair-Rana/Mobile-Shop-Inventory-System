const today = new Date().toISOString().slice(0, 10)

export const cashSessionFixtures = [
    {
        id: 1,
        branch_id: 1,
        status: 'open',
        opened_by: 'cashier',
        opening_amount: 10000,
        expected_closing: 28500,
        counted_amount: null,
        variance: null,
        opened_at: `${today}T08:00:00Z`,
        closed_at: null,
    },
]

export const cashInflowFixtures = [
    { id: 1, session_id: 1, category: 'Sales', amount: 220000, note: 'Invoice INV-0001', created_at: `${today}T08:35:00Z`, actor: 'cashier' },
    { id: 2, session_id: 1, category: 'Sales', amount: 600, note: 'Invoice INV-0003', created_at: `${today}T09:50:00Z`, actor: 'cashier' },
    { id: 3, session_id: 1, category: 'Sales', amount: 45000, note: 'Invoice INV-0004', created_at: `${today}T10:25:00Z`, actor: 'cashier' },
    { id: 4, session_id: 1, category: 'Repair', amount: 1200, note: 'REP-010 delivery', created_at: `${today}T11:00:00Z`, actor: 'cashier' },
]

export const cashOutflowFixtures = [
    { id: 1, session_id: 1, category: 'Expense', amount: 500, note: 'Tea/refreshments', created_at: `${today}T10:00:00Z`, actor: 'manager' },
    { id: 2, session_id: 1, category: 'Petty Cash', amount: 800, note: 'Printer paper', created_at: `${today}T11:30:00Z`, actor: 'manager' },
]

export const expenseFixtures = [
    { id: 1, date: '2026-08-28', category: 'Utilities', branch_id: 1, amount: 8500, payment_source: 'cash', approval_state: 'approved', notes: 'Electricity bill Aug', created_at: '2026-08-28T09:00:00Z' },
    { id: 2, date: '2026-08-27', category: 'Supplies', branch_id: 1, amount: 1200, payment_source: 'cash', approval_state: 'approved', notes: 'Stationery', created_at: '2026-08-27T11:00:00Z' },
    { id: 3, date: '2026-08-26', category: 'Maintenance', branch_id: 1, amount: 3500, payment_source: 'bank', approval_state: 'pending', notes: 'AC servicing', created_at: '2026-08-26T14:00:00Z' },
    { id: 4, date: '2026-08-25', category: 'Marketing', branch_id: 1, amount: 12000, payment_source: 'bank', approval_state: 'approved', notes: 'Facebook ads campaign', created_at: '2026-08-25T10:00:00Z' },
    { id: 5, date: '2026-08-20', category: 'Rent', branch_id: 1, amount: 85000, payment_source: 'cheque', approval_state: 'approved', notes: 'August rent', created_at: '2026-08-20T09:00:00Z' },
]
