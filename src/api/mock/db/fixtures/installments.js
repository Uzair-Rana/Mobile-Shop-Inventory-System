const today = new Date().toISOString().slice(0, 10)
const d = (offset) => {
    const dt = new Date()
    dt.setDate(dt.getDate() + offset)
    return dt.toISOString().slice(0, 10)
}

export const installmentPlanFixtures = [
    { id: 1, plan_number: 'INST-001', customer_id: 2, customer_name: 'Sara Malik', customer_phone: '03111234567', product_name: 'Apple iPhone 13', sale_amount: 185000, down_payment: 50000, markup_rate: 10, installment_count: 6, total_amount: 148500, paid_amount: 100000, remaining_amount: 48500, paid_count: 4, total_count: 6, status: 'active', next_due_date: d(5), created_at: '2026-03-01T10:00:00Z' },
    { id: 2, plan_number: 'INST-002', customer_id: 5, customer_name: 'Usman Tariq', customer_phone: '03451234567', product_name: 'Samsung Galaxy S23', sale_amount: 220000, down_payment: 70000, markup_rate: 12, installment_count: 6, total_amount: 168000, paid_amount: 56000, remaining_amount: 112000, paid_count: 2, total_count: 6, status: 'overdue', next_due_date: d(-15), created_at: '2026-04-01T10:00:00Z' },
    { id: 3, plan_number: 'INST-003', customer_id: 1, customer_name: 'Ahmed Ali', customer_phone: '03001234567', product_name: 'Xiaomi 13 Pro', sale_amount: 110000, down_payment: 30000, markup_rate: 8, installment_count: 4, total_amount: 86400, paid_amount: 86400, remaining_amount: 0, paid_count: 4, total_count: 4, status: 'completed', next_due_date: null, created_at: '2026-02-01T10:00:00Z' },
    { id: 4, plan_number: 'INST-004', customer_id: 8, customer_name: 'Zara Sheikh', customer_phone: '03771234567', product_name: 'Samsung Galaxy A54', sale_amount: 85000, down_payment: 25000, markup_rate: 10, installment_count: 3, total_amount: 66000, paid_amount: 0, remaining_amount: 66000, paid_count: 0, total_count: 3, status: 'active', next_due_date: d(12), created_at: '2026-08-01T10:00:00Z' },
    { id: 5, plan_number: 'INST-005', customer_id: 3, customer_name: 'Hamid Khan', customer_phone: '03211234567', product_name: 'Oppo Reno 8', sale_amount: 70000, down_payment: 20000, markup_rate: 10, installment_count: 5, total_amount: 55000, paid_amount: 0, remaining_amount: 55000, paid_count: 0, total_count: 5, status: 'overdue', next_due_date: d(-8), created_at: '2026-07-01T10:00:00Z' },
    { id: 6, plan_number: 'INST-006', customer_id: 6, customer_name: 'Rana Mobile', customer_phone: '03551234567', product_name: 'iPhone 14 ×5', sale_amount: 1150000, down_payment: 350000, markup_rate: 8, installment_count: 4, total_amount: 648000, paid_amount: 162000, remaining_amount: 486000, paid_count: 1, total_count: 4, status: 'active', next_due_date: d(20), created_at: '2026-08-10T10:00:00Z' },
]

export const installmentScheduleFixtures = {
    1: [
        { id: 1, plan_id: 1, installment_number: 1, due_date: '2026-04-01', amount: 24750, status: 'paid', paid_at: '2026-04-01T10:00:00Z' },
        { id: 2, plan_id: 1, installment_number: 2, due_date: '2026-05-01', amount: 24750, status: 'paid', paid_at: '2026-05-02T11:00:00Z' },
        { id: 3, plan_id: 1, installment_number: 3, due_date: '2026-06-01', amount: 24750, status: 'paid', paid_at: '2026-06-01T09:00:00Z' },
        { id: 4, plan_id: 1, installment_number: 4, due_date: '2026-07-01', amount: 24750, status: 'paid', paid_at: '2026-07-03T14:00:00Z' },
        { id: 5, plan_id: 1, installment_number: 5, due_date: d(5), amount: 24750, status: 'pending', paid_at: null },
        { id: 6, plan_id: 1, installment_number: 6, due_date: d(35), amount: 24750, status: 'pending', paid_at: null },
    ],
    2: [
        { id: 7, plan_id: 2, installment_number: 1, due_date: '2026-05-01', amount: 28000, status: 'paid', paid_at: '2026-05-01T10:00:00Z' },
        { id: 8, plan_id: 2, installment_number: 2, due_date: '2026-06-01', amount: 28000, status: 'paid', paid_at: '2026-06-05T12:00:00Z' },
        { id: 9, plan_id: 2, installment_number: 3, due_date: d(-15), amount: 28000, status: 'overdue', paid_at: null },
        { id: 10, plan_id: 2, installment_number: 4, due_date: d(15), amount: 28000, status: 'pending', paid_at: null },
        { id: 11, plan_id: 2, installment_number: 5, due_date: d(45), amount: 28000, status: 'pending', paid_at: null },
        { id: 12, plan_id: 2, installment_number: 6, due_date: d(75), amount: 28000, status: 'pending', paid_at: null },
    ],
}
