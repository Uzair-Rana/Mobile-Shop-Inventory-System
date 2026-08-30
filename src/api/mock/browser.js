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

export const worker = setupWorker(
    ...authHandlers,
    ...branchHandlers,
    ...inventoryHandlers,
    ...salesHandlers,
    ...repairsHandlers,
    ...installmentsHandlers,
)
