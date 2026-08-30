const today = new Date().toISOString().slice(0, 10)

export const invoiceFixtures = [
    { id: 1, invoice_number: 'INV-0001', customer_id: 1, customer_name: 'Ahmed Ali', status: 'paid', payment_method: 'cash', grand_total: 220000, subtotal: 220000, tax_amount: 0, invoice_discount: 0, amount_paid: 220000, balance_due: 0, created_at: `${today}T08:30:00Z`, line_count: 1 },
    { id: 2, invoice_number: 'INV-0002', customer_id: 2, customer_name: 'Sara Malik', status: 'partially_paid', payment_method: 'split', grand_total: 185000, subtotal: 185000, tax_amount: 0, invoice_discount: 0, amount_paid: 150000, balance_due: 35000, created_at: `${today}T09:15:00Z`, line_count: 1 },
    { id: 3, invoice_number: 'INV-0003', customer_id: null, customer_name: null, status: 'paid', payment_method: 'cash', grand_total: 600, subtotal: 600, tax_amount: 0, invoice_discount: 0, amount_paid: 600, balance_due: 0, created_at: `${today}T09:45:00Z`, line_count: 2 },
    { id: 4, invoice_number: 'INV-0004', customer_id: 3, customer_name: 'Hamid Khan', status: 'finalized', payment_method: 'card', grand_total: 45000, subtotal: 45000, tax_amount: 0, invoice_discount: 0, amount_paid: 45000, balance_due: 0, created_at: `${today}T10:20:00Z`, line_count: 1 },
    { id: 5, invoice_number: 'INV-0005', customer_id: 5, customer_name: 'Usman Tariq', status: 'partially_paid', payment_method: 'khata', grand_total: 35000, subtotal: 35000, tax_amount: 0, invoice_discount: 0, amount_paid: 0, balance_due: 35000, created_at: '2026-07-01T10:00:00Z', line_count: 1 },
    { id: 6, invoice_number: 'INV-0006', customer_id: 4, customer_name: 'Nida Fatima', status: 'paid', payment_method: 'cash', grand_total: 38000, subtotal: 38000, tax_amount: 0, invoice_discount: 0, amount_paid: 38000, balance_due: 0, created_at: '2026-08-10T11:00:00Z', line_count: 1 },
    { id: 7, invoice_number: 'INV-0007', customer_id: 6, customer_name: 'Rana Mobile', status: 'paid', payment_method: 'bank_transfer', grand_total: 660000, subtotal: 660000, tax_amount: 0, invoice_discount: 40000, amount_paid: 660000, balance_due: 0, created_at: '2026-08-15T14:00:00Z', line_count: 3 },
    { id: 8, invoice_number: 'INV-0008', customer_id: 8, customer_name: 'Zara Sheikh', status: 'returned', payment_method: 'cash', grand_total: 0, subtotal: 55000, tax_amount: 0, invoice_discount: 0, amount_paid: 0, balance_due: 0, created_at: '2026-08-18T09:00:00Z', line_count: 1 },
    { id: 9, invoice_number: 'INV-0009', customer_id: 7, customer_name: 'Faisal Hussain', status: 'voided', payment_method: 'cash', grand_total: 0, subtotal: 17000, tax_amount: 0, invoice_discount: 0, amount_paid: 0, balance_due: 0, created_at: '2026-08-20T10:00:00Z', line_count: 1 },
    { id: 10, invoice_number: 'INV-0010', customer_id: 1, customer_name: 'Ahmed Ali', status: 'draft', payment_method: 'cash', grand_total: 9000, subtotal: 9000, tax_amount: 0, invoice_discount: 0, amount_paid: 0, balance_due: 9000, created_at: `${today}T11:30:00Z`, line_count: 3 },
]

export const invoiceLineFixtures = {
    1: [{ id: 1, invoice_id: 1, product_name: 'Samsung Galaxy S23', type: 'unit', unit_id: 4, imei: '352099001761485', qty: 1, unit_price: 220000, discount_abs: 0, discount_pct: 0, line_total: 220000 }],
    2: [{ id: 2, invoice_id: 2, product_name: 'Apple iPhone 13', type: 'unit', unit_id: 2, imei: '352099001761483', qty: 1, unit_price: 185000, discount_abs: 0, discount_pct: 0, line_total: 185000 }],
    3: [
        { id: 3, invoice_id: 3, product_name: 'Tempered Glass Samsung A54', type: 'accessory', unit_id: null, imei: null, qty: 1, unit_price: 300, discount_abs: 0, discount_pct: 0, line_total: 300 },
        { id: 4, invoice_id: 3, product_name: 'Type-C Magnetic Cable', type: 'accessory', unit_id: null, imei: null, qty: 1, unit_price: 900, discount_abs: 600, discount_pct: 0, line_total: 300 },
    ],
}
