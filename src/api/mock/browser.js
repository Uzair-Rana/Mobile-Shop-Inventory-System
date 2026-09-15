/**
 * MSW browser worker — aggregates all mock handlers.
 * Started in main.js before the Vue app mounts.
 */
import { setupWorker } from 'msw/browser'
import { authHandlers } from './handlers/auth.js'
import { branchHandlers } from './handlers/branches.js'
import { inventoryHandlers } from './handlers/inventory.js'
import { salesHandlers } from './handlers/sales.js'
import { repairsHandlers } from './handlers/repairs.js'
import { installmentsHandlers } from './handlers/installments.js'
import { customersHandlers } from './handlers/customers.js'
import { suppliersHandlers } from './handlers/suppliers.js'
import { purchasesHandlers } from './handlers/purchases.js'
import { transfersHandlers } from './handlers/transfers.js'
import { cashHandlers } from './handlers/cash.js'
import { settingsHandlers } from './handlers/settings.js'
import { adminHandlers } from './handlers/admin.js'
import { reportsHandlers } from './handlers/reports.js'

export const worker = setupWorker(
    ...authHandlers,
    ...branchHandlers,
    ...inventoryHandlers,
    ...salesHandlers,
    ...repairsHandlers,
    ...installmentsHandlers,
    ...customersHandlers,
    ...suppliersHandlers,
    ...purchasesHandlers,
    ...transfersHandlers,
    ...cashHandlers,
    ...settingsHandlers,
    ...adminHandlers,
    ...reportsHandlers,
)
