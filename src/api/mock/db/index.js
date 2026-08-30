import { createStore } from './createStore.js'
import { userFixtures } from './fixtures/users.js'
import { branchFixtures } from './fixtures/branches.js'
import { deviceFixtures, deviceTimelineFixtures } from './fixtures/devices.js'
import { accessoryFixtures, movementFixtures } from './fixtures/accessories.js'
import { customerFixtures, ledgerFixtures } from './fixtures/customers.js'
import { invoiceFixtures, invoiceLineFixtures } from './fixtures/invoices.js'
import { repairFixtures, repairStatusLogFixtures } from './fixtures/repairs.js'
import { installmentPlanFixtures, installmentScheduleFixtures } from './fixtures/installments.js'
import { purchaseOrderFixtures, poLineFixtures } from './fixtures/purchases.js'
import { cashSessionFixtures, cashInflowFixtures, cashOutflowFixtures, expenseFixtures } from './fixtures/cash.js'
import { transferFixtures } from './fixtures/transfers.js'
import { roleFixtures, auditLogFixtures } from './fixtures/admin.js'

export const db = {
    users: createStore(userFixtures),
    branches: createStore(branchFixtures),
    devices: createStore(deviceFixtures),
    deviceTimelines: deviceTimelineFixtures,   // static lookup by device_id
    accessories: createStore(accessoryFixtures),
    movements: createStore(movementFixtures),
    customers: createStore(customerFixtures),
    ledgers: ledgerFixtures,            // static lookup by customer_id
    invoices: createStore(invoiceFixtures),
    invoiceLines: invoiceLineFixtures,       // static lookup by invoice_id
    repairs: createStore(repairFixtures),
    repairLogs: repairStatusLogFixtures,   // static lookup by repair_id
    plans: createStore(installmentPlanFixtures),
    schedules: installmentScheduleFixtures, // static lookup by plan_id
    purchaseOrders: createStore(purchaseOrderFixtures),
    poLines: poLineFixtures,            // static lookup by po_id
    cashSessions: createStore(cashSessionFixtures),
    cashInflows: createStore(cashInflowFixtures),
    cashOutflows: createStore(cashOutflowFixtures),
    expenses: createStore(expenseFixtures),
    transfers: createStore(transferFixtures),
    roles: createStore(roleFixtures),
    auditLogs: createStore(auditLogFixtures),
}

/** Simple text search across multiple fields */
export function searchIn(rows, query, fields) {
    if (!query) return rows
    const q = query.toLowerCase()
    return rows.filter(r => fields.some(f => String(r[f] ?? '').toLowerCase().includes(q)))
}

/** Parse ?page and ?page_size from a URL */
export function parsePagination(url) {
    const page = parseInt(url.searchParams.get('page') || '1')
    const pageSize = parseInt(url.searchParams.get('page_size') || '25')
    return { page, pageSize }
}

/** Build DRF-style paginated response */
export function paginated(rows, page, pageSize) {
    const count = rows.length
    const start = (page - 1) * pageSize
    const results = rows.slice(start, start + pageSize)
    return {
        count,
        next: start + pageSize < count ? `?page=${page + 1}` : null,
        previous: page > 1 ? `?page=${page - 1}` : null,
        results,
    }
}
