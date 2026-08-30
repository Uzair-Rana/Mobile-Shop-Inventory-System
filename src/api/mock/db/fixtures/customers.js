export const customerFixtures = [
    { id: 1, name: 'Ahmed Ali', phone: '03001234567', email: 'ahmed@email.com', cnic: '3520112345671', address: 'Gulberg, Lahore', credit_limit: 50000, outstanding_balance: 0, total_spent: 220000, invoice_count: 3, repair_count: 1, created_at: '2026-01-15T10:00:00Z' },
    { id: 2, name: 'Sara Malik', phone: '03111234567', email: 'sara@email.com', cnic: '3520112345672', address: 'DHA, Lahore', credit_limit: 100000, outstanding_balance: 35000, total_spent: 185000, invoice_count: 2, repair_count: 0, created_at: '2026-02-20T10:00:00Z' },
    { id: 3, name: 'Hamid Khan', phone: '03211234567', email: '', cnic: '3520112345673', address: 'Johar Town', credit_limit: 20000, outstanding_balance: 0, total_spent: 45000, invoice_count: 1, repair_count: 2, created_at: '2026-03-10T10:00:00Z' },
    { id: 4, name: 'Nida Fatima', phone: '03021234567', email: 'nida@email.com', cnic: '3520112345674', address: 'Model Town', credit_limit: 0, outstanding_balance: 0, total_spent: 38000, invoice_count: 2, repair_count: 0, created_at: '2026-04-05T10:00:00Z' },
    { id: 5, name: 'Usman Tariq', phone: '03451234567', email: 'usman@email.com', cnic: '', address: 'Iqbal Town', credit_limit: 30000, outstanding_balance: 28000, total_spent: 92000, invoice_count: 4, repair_count: 1, created_at: '2026-04-18T10:00:00Z' },
    { id: 6, name: 'Rana Mobile', phone: '03551234567', email: 'rana@wholesale.com', cnic: '3520112345676', address: 'Hall Road', credit_limit: 500000, outstanding_balance: 125000, total_spent: 750000, invoice_count: 12, repair_count: 0, created_at: '2026-01-01T10:00:00Z', wholesale_tier: 'Tier A' },
    { id: 7, name: 'Faisal Hussain', phone: '03661234567', email: '', cnic: '3520112345677', address: 'Cantt', credit_limit: 0, outstanding_balance: 0, total_spent: 17000, invoice_count: 1, repair_count: 3, created_at: '2026-05-22T10:00:00Z' },
    { id: 8, name: 'Zara Sheikh', phone: '03771234567', email: 'zara@email.com', cnic: '3520112345678', address: 'Wapda Town', credit_limit: 15000, outstanding_balance: 0, total_spent: 55000, invoice_count: 2, repair_count: 0, created_at: '2026-06-10T10:00:00Z' },
]

export const ledgerFixtures = {
    1: [
        { id: 1, date: '2026-07-20T14:00:00Z', description: 'Invoice #INV-0001', reference: 'INV-0001', debit: 220000, credit: 0, running_balance: -220000 },
        { id: 2, date: '2026-07-20T14:05:00Z', description: 'Payment — Cash', reference: 'PMT-001', debit: 0, credit: 220000, running_balance: 0 },
    ],
    5: [
        { id: 3, date: '2026-07-01T10:00:00Z', description: 'Invoice #INV-0005', reference: 'INV-0005', debit: 35000, credit: 0, running_balance: -35000 },
        { id: 4, date: '2026-07-15T12:00:00Z', description: 'Partial payment', reference: 'PMT-004', debit: 0, credit: 7000, running_balance: -28000 },
    ],
}
