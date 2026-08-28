# Implementation Tasks

## Task Dependency Graph

```
T1 (Foundation) → T2 (Mock Layer) → T3 (Auth & Shell) → T4 (Dashboard)
                                  → T5 (New UI Primitives)
T3, T5 → T6 (Inventory IMEI)
T3, T5 → T7 (Inventory Accessories)
T3, T5 → T8 (POS Extended)
T3, T5 → T9 (Repairs)
T3, T5 → T10 (Purchases)
T3, T5 → T11 (Installments)
T3, T5 → T12 (Cash)
T3, T5 → T13 (Customers)
T6, T7, T8, T9, T10, T11, T12, T13 → T14 (Reports)
T6, T7 → T15 (Transfers)
T14, T15 → T16 (Admin)
T8 → T17 (Print & Receipt)
T16 → T18 (Integration & Build)
```

---

## Task 1: Foundation — Dependencies, Config & Env

- [ ] Install missing npm packages: `msw`, `vue-chartjs`, `chart.js`, `jsbarcode`, `qrcode`
- [ ] Add `VITE_USE_MOCK=true` to `.env` and `VITE_USE_MOCK=false` to `.env.production`
- [ ] Update `vite.config.js` to copy MSW service worker to `public/` via `vite-plugin-mkcert` or a Vite copy hook
- [ ] Update `jsconfig.json` paths if needed for new directories
- [ ] Run `npm run build` to confirm zero errors after dependency additions

---

## Task 2: Mock API Layer

- [ ] Create `src/api/mock/db/createStore.js` — generic in-memory store with `create`, `list`, `get`, `update`, `delete`, `paginate(page, size)` methods
- [ ] Create fixture files:
  - `src/api/mock/db/fixtures/users.js` — 3 users: admin, manager, cashier with different permission sets
  - `src/api/mock/db/fixtures/branches.js` — 2 branches: Main Store, Warehouse
  - `src/api/mock/db/fixtures/devices.js` — 10 IMEI devices across brands/models/statuses
  - `src/api/mock/db/fixtures/accessories.js` — 15 accessories with varying stock levels (some below reorder)
  - `src/api/mock/db/fixtures/invoices.js` — 20 invoices in various statuses
  - `src/api/mock/db/fixtures/repairs.js` — 12 repair jobs spread across all 10 stages
  - `src/api/mock/db/fixtures/customers.js` — 8 customers with ledger entries
  - `src/api/mock/db/fixtures/installments.js` — 6 plans, 2 overdue
  - `src/api/mock/db/fixtures/purchases.js` — 5 purchase orders
  - `src/api/mock/db/fixtures/cash.js` — 1 open session with inflows/outflows
- [ ] Create `src/api/mock/db/index.js` — seeds all fixtures into `createStore` instances, exports `db`
- [ ] Create MSW handler files (one per domain):
  - `src/api/mock/handlers/auth.js` — login, logout, me, step-up
  - `src/api/mock/handlers/branches.js` — list branches
  - `src/api/mock/handlers/inventory.js` — devices CRUD + timeline + cost-adjust + duplicate-check + accessories CRUD + stock-adjust + movements + low-stock + scan
  - `src/api/mock/handlers/sales.js` — invoices CRUD + finalize + void + correct + daily-summary
  - `src/api/mock/handlers/repairs.js` — jobs CRUD + update-status + deliver + board
  - `src/api/mock/handlers/purchases.js` — orders CRUD + receive + acquisitions
  - `src/api/mock/handlers/installments.js` — plans CRUD + collect + schedule + overdue + aging
  - `src/api/mock/handlers/customers.js` — CRUD + ledger + history + duplicate-check + search
  - `src/api/mock/handlers/cash.js` — sessions + inflow + outflow + expenses
  - `src/api/mock/handlers/reports.js` — all 10 report endpoints + export stubs
  - `src/api/mock/handlers/transfers.js` — CRUD + dispatch + receive
  - `src/api/mock/handlers/admin.js` — users + roles + audit-log
- [ ] Create `src/api/mock/index.js` — imports all handlers, creates and exports MSW `worker`
- [ ] Update `src/main.js` to conditionally start MSW worker when `VITE_USE_MOCK === 'true'`
- [ ] Verify mock layer: start dev server, confirm Axios calls return seeded data in the browser network tab

---

## Task 3: Auth & Shell — Branch Selector, Step-Up Auth, Route Guard Updates

- [ ] Create `src/stores/branch.js` — `activeBranchId`, `branchList`, `fetchBranches()`, `switchBranch(id)`
- [ ] Update `src/api/client.js` request interceptor to inject `X-Branch-ID` header from `branchStore.activeBranchId`
- [ ] Create `src/api/branches.js` — `list()` wrapping `GET /api/v1/branches/`
- [ ] Update `src/stores/auth.js` — load branch list after `fetchMe()`, store in auth store, initialize `branch` store
- [ ] Create `src/components/layout/BranchSelector.vue` — dropdown in top bar showing branch name, writes to `branchStore`; emits `branchChanged` watched by list views
- [ ] Update `src/components/layout/AppTopBar.vue` — integrate `BranchSelector` between page title and sync indicator
- [ ] Update `src/stores/ui.js` — add `stepUpAuthDialog` state: `{ open, action, resolve }`
- [ ] Create `src/components/layout/StepUpAuthModal.vue` — password field + Verify button, calls `POST /api/v1/auth/step-up/`, resolves the Promise stored in `ui.stepUpAuthDialog`
- [ ] Create `src/composables/useStepUpAuth.js` — `requireStepUp(action)` opens modal, returns `Promise<boolean>`, clears token after use
- [ ] Create `src/composables/useBranch.js` — thin wrapper over `branchStore`
- [ ] Update `src/router/index.js`:
  - Add all new routes from design §1.3 (cash, devices, board, acquisitions, aging, plan builder, transfers, new report routes, audit, correction)
  - Add `StepUpAuthModal` to `App.vue` alongside `ToastContainer` and `ConfirmDialog`
- [ ] Update `src/App.vue` to render `StepUpAuthModal`

---

## Task 4: Dashboard — Exception Rail, KPI Strip, Charts

- [ ] Install `vue-chartjs` and `chart.js` (already in T1 — verify installed)
- [ ] Create `src/composables/useChartData.js` — `useChartData(fetchFn, { transform })` returns `{ chartData, tableRows, loading, load }`
- [ ] Create `src/components/charts/LineChart.vue` — `vue-chartjs` Line wrapper, accepts `chartData` prop
- [ ] Create `src/components/charts/BarChart.vue` — `vue-chartjs` Bar wrapper
- [ ] Create `src/components/charts/DonutChart.vue` — `vue-chartjs` Doughnut wrapper
- [ ] Create `src/components/charts/ChartWithTable.vue` — chart/table toggle, export CSV button, uses `useChartData`
- [ ] Create `src/components/ui/PermGate.vue` — `<PermGate perm="codename"><slot/></PermGate>` using `usePermissions().can()`
- [ ] Rewrite `src/views/dashboard/DashboardView.vue`:
  - Exception rail (sync error, overdue installments, ready-repairs, low stock) — leads the page, collapses when empty
  - KPI strip: sales, cash-in, gross profit (`<PermGate perm="view_profit">`), cash variance, open repairs, overdue plans
  - Charts row: `LineChart` (daily sales trend), `DonutChart` (revenue by category), `BarChart` (top brands — `<PermGate perm="view_reports">`)
  - Two-column working area: recent invoices table + pending repairs table
- [ ] Update `src/api/sales.js` to add `getDailySummary`, ensure daily-summary endpoint is called on dashboard mount

---

## Task 5: New UI Primitives

- [ ] Create `src/components/ui/AppTabs.vue` — `tabs: [{ key, label }]`, active tab v-model, renders slot keyed by active tab
- [ ] Create `src/components/ui/AppDateRange.vue` — from/to date inputs, emits `{ from, to }`, validates from ≤ to
- [ ] Create `src/components/ui/AppFileUpload.vue` — drag-drop zone + click-to-browse, accepts file types prop, previews images, emits `File` objects
- [ ] Create `src/components/ui/AppTimeline.vue` — vertical event list with icon per event type, timestamp, actor; cost events wrapped in `<PermGate perm="view_cost">`
- [ ] Create `src/components/ui/AppKanban.vue` — flex-row of columns, HTML5 draggable cards, emits `('move', { itemId, fromCol, toCol })`, keyboard-accessible (arrow key column movement)
- [ ] Create `src/components/ui/AppPrintFrame.vue` — hidden `div#print-target`, exposes slot; `usePrint().print(layout)` sets layout class and calls `window.print()`
- [ ] Create `src/composables/usePrint.js` — sets `data-print-layout` attribute on `#print-target`, triggers `window.print()`
- [ ] Add `@media print` rules to `src/assets/main.css` for `#print-target`, `.print-80mm`, `.print-a4`

---

## Task 6: Inventory — Serialized Devices (IMEI)

- [ ] Create `src/api/inventory.js` additions — `listDevices(params)`, `getDevice(id)`, `createDevice(data)`, `updateDevice(id, data)`, `getDeviceTimeline(id)`, `adjustDeviceCost(id, data)`, `checkDuplicate(imei)`
- [ ] Update `src/stores/inventory.js` — add `devices`, `fetchDevices(params)`, `devicePagination`
- [ ] Create `src/views/inventory/DeviceListView.vue`:
  - Search/filter bar: IMEI, brand, model, condition, PTA status, lifecycle state, branch
  - `AppTable` with columns: IMEI, Product, Brand, Condition, PTA Status, Lifecycle State, Cost (PermGate), Sell Price, Actions
  - Pagination via `usePagination`
  - Watch `branchStore.activeBranchId` to reload
- [ ] Create `src/views/inventory/DeviceDetailView.vue`:
  - Identity card: IMEI1, IMEI2, serial, barcode, brand, model
  - Condition/network/PTA fields panel
  - Commercial panel (`<PermGate perm="view_cost">`) — cost price + cost-adjustment button
  - Cost-adjustment sub-form: new cost, reason — requires `useStepUpAuth('cost_adjustment')` before submit
  - `AppTimeline` with full lifecycle events; cost events behind `view_cost` PermGate
- [ ] Create `src/views/inventory/DeviceAddView.vue`:
  - `ScannerInput` for IMEI entry — fires `checkDuplicate` on scan
  - Duplicate-warning modal with override + reason capture
  - Full device form (brand, model, condition, PTA, cost, sell price)
  - Validation: IMEI format (15 digits), required fields
- [ ] Update `src/views/inventory/InventoryLayout.vue` tabs to include Devices tab

---

## Task 7: Inventory — Accessories, Stock Movements & Labels

- [ ] Create `src/api/inventory.js` additions — `getAccessoryMovements(id, params)` if not already present
- [ ] Create `src/views/inventory/AccessoryDetailView.vue`:
  - Detail header: name, SKU, branch quantities
  - Stock movement history table via `AppTable` (date, type, qty_change, reason, actor)
  - Stock adjustment panel (inline, not modal)
- [ ] Update `src/views/inventory/AccessoryListView.vue`:
  - Add low-stock badge/row highlight when `stock_qty <= reorder_level`
  - Add dead-stock indicator when no movement in configurable window (default 90 days)
- [ ] Create `src/views/inventory/BarcodeLabelsView.vue`:
  - Field selection checkboxes: Name, SKU, Price, Barcode, QR, Branch, Category
  - Quantity per item input
  - 4-per-row label preview grid rendered live
  - Barcode via `JsBarcode`, QR via `qrcode` — both client-side, no server dependency
  - Print button using `usePrint()`
- [ ] Add route `/inventory/labels` to router
- [ ] Add Labels tab to `InventoryLayout.vue`

---

## Task 8: POS / Sales — Split Payments, Trade-In, Discount Approval, Receipt Print

- [ ] Update `src/stores/cart.js`:
  - Replace `paymentMethod` + `amountReceived` with `tenders: []`
  - Add computed `totalTendered`, `remainingDue`, `changeAmount`
  - Add `tradeIn: null`, `setTradeIn(unit)`, `clearTradeIn()`
  - Update `grandTotal` computation: `subtotal + tax − invoiceDiscount − (tradeIn?.acceptedValue ?? 0)`
  - Update `checkout()` payload to send `tenders` array instead of single payment method
- [ ] Create `src/components/pos/PaymentPanel.vue`:
  - Tender list: each row = method selector + amount input + remove button
  - Add tender button
  - Running display: Tendered / Grand Total / Remaining Due / Change
  - All amounts via `MoneyDisplay`
  - Payment methods from `PAYMENT_METHODS` constant
- [ ] Create `src/components/pos/DiscountPanel.vue`:
  - Discount amount input
  - Reads `branchStore.settings.discountThreshold`
  - When amount > threshold: disables direct apply, shows approval prompt, calls `useStepUpAuth('discount_override')`
  - Emits `('applied', amount)` on success
- [ ] Create `src/components/pos/TradeInPanel.vue`:
  - IMEI search/scan input
  - Device lookup via `GET /api/v1/inventory/scan/`
  - Shows device details + accepted value input
  - Emits `('trade-in-set', { unitId, imei, acceptedValue })`
- [ ] Create `src/components/pos/ReceiptPrint.vue`:
  - `layout` prop: `'80mm' | 'A4'`
  - `invoice` prop: full invoice object
  - 80mm layout: centered header, line items, IMEI per serialized item, totals, tenders, change, warranty/return policy text
  - A4 layout: letterhead with company logo placeholder, formal invoice layout
  - Uses `AppPrintFrame` + `usePrint()`
- [ ] Update `src/views/pos/PosView.vue`:
  - Replace payment section with `PaymentPanel`
  - Add `DiscountPanel` for invoice-level discount
  - Add Trade-In tab/toggle in left panel — renders `TradeInPanel`
  - Post-sale: show `ReceiptPrint` instead of current minimal receipt modal, with 80mm/A4 toggle
- [ ] Create `src/views/sales/InvoiceCorrectionView.vue`:
  - Loads original invoice (read-only display)
  - Correction type selector: Return / Exchange / Void
  - Per-type form:
    - Return: line item qty selection, refund method, restock/quarantine/write-off outcome
    - Exchange: return lines + new cart items (links back to POS for new items)
    - Void: reason field
  - All corrections show `ConfirmDialog` with financial effect before submit
  - Calls `POST /api/v1/sales/invoices/:id/correct/`
- [ ] Add route `/sales/invoices/:id/correct` to router

---

## Task 9: Repairs — Kanban Board, Parts Consumption, Approvals

- [ ] Create `src/stores/repairBoard.js`:
  - `STAGES` ordered array
  - `columns: Record<string, RepairJob[]>`
  - `loadBoard(branchId)` — calls `GET /api/v1/repairs/board/`
  - `moveJob(jobId, fromStage, toStage)` — optimistic update, rollback on error
- [ ] Add `src/api/repairs.js` additions — `getBoard()` if not present
- [ ] Create `src/views/repairs/RepairBoardView.vue`:
  - Uses `AppKanban` with `repairBoard.store` columns
  - Card shows: job #, device model, customer name, status badge, days-open counter
  - Column count badge per stage
  - On card move: calls `repairBoard.moveJob`, shows toast on success/rollback
  - Keyboard accessible
- [ ] Update `src/views/repairs/RepairDetailView.vue`:
  - Add parts-consumption panel: search accessory by name/SKU, add quantity consumed, calls stock-adjust API
  - Add customer approval panel when status is `awaiting_approval`: capture approval type (in-person / phone / declined)
  - Delivery screen: outstanding balance summary, payment collection input, calls `deliver` API
  - All destructive status changes go through `ConfirmDialog` with effect string
- [ ] Add route `/repairs/board` to router; add Board tab to repairs layout/nav

---

## Task 10: Purchasing & Trade-In (Acquisition Flow)

- [ ] Update `src/views/purchases/PurchaseDetailView.vue`:
  - Partial receiving: per-line received quantity inputs (≤ ordered qty), discrepancy notes
  - Serialized receiving tab: `ScannerInput` for IMEI scan, builds list of received IMEIs
  - Auto-transitions PO to `closed` when all qty received
- [ ] Create `src/views/purchases/AcquisitionView.vue` (used-phone intake):
  - Seller identity section: name, phone, CNIC — with note that this is a policy-gated collection
  - Inspection checklist: power on, screen, back glass, buttons, IMEI match (checkboxes)
  - Condition notes textarea
  - Photo capture / upload (via `AppFileUpload`, feature-flagged by branch setting)
  - Data-risk notice acknowledgment checkbox (required before submit)
  - Quarantine flag toggle with reason field
  - Printable declaration form via `usePrint()`
  - Submits to `POST /api/v1/purchases/acquisitions/`
- [ ] Add route `/purchases/acquisitions/new` to router

---

## Task 11: Installments — Plan Builder, Aging View, Khata Guard

- [ ] Create `src/views/installments/InstallmentPlanBuilderView.vue`:
  - Inputs: sale amount, down payment, markup rate (%), installment count, first due date
  - All reactive — use `watch` or `computed` for live recalculation
  - Computed: `financedAmount`, `totalPayable`, `installmentAmount`, remainder on last
  - Live preview table: row per installment with due date, amount
  - All amounts via `MoneyDisplay`
  - Submit: calls `POST /api/v1/installments/plans/`
- [ ] Create `src/composables/useAging.js`:
  - Accepts `Ref<InstallmentPlan[]>`
  - Returns `buckets` computed with 5 ranges: `1–7d`, `8–30d`, `31–60d`, `61–90d`, `90d+`
  - Each bucket: `{ label, count, totalAmount }`
- [ ] Create `src/views/installments/OverdueAgingView.vue`:
  - Calls `GET /api/v1/installments/aging/`
  - Uses `useAging` to compute buckets
  - Bucket summary cards + expandable table per bucket
  - All amounts via `MoneyDisplay`
- [ ] Update `src/views/installments/InstallmentDetailView.vue`:
  - Recovery entry: partial payment amount + allocation note
  - Plan state badge for each installment row (Pending / Partially Paid / Paid / Overdue / Rescheduled / Waived)
- [ ] Audit `src/views/customers/CustomerDetailView.vue` and `CustomerLedgerView.vue`:
  - Assert zero `<input>` / `<select>` / `<textarea>` elements write to running balance
  - Running balance is always computed from ledger entries
- [ ] Add routes `/installments/new` and `/installments/aging` to router

---

## Task 12: Cash & Expenses — Session State Machine

- [ ] Create `src/stores/cashSession.js`:
  - States: `CLOSED | OPEN | PENDING_COUNT | RECONCILED`
  - `openSession(openingAmount)` — POST + transition to OPEN
  - `addInflow(entry)`, `addOutflow(entry)`
  - `submitCount(countedAmount)` — computes `variance = counted - expected`, transitions to RECONCILED
  - `confirmClose()` — POST close, transitions to CLOSED
  - `fetchCurrentSession()` — GET current, hydrates state
- [ ] Create `src/api/cash.js` if not present — all cash/expense endpoints
- [ ] Create `src/views/cash/CashSessionView.vue`:
  - State-aware UI: shows open form when CLOSED, running totals when OPEN, count form when PENDING_COUNT, reconciliation summary when RECONCILED
  - Opening amount input → Open Session button
  - Inflow/Outflow quick-entry panel with category + amount + note
  - Closing count: physically counted amount input, variance display (red if negative)
  - Confirm Close button with `ConfirmDialog` showing variance effect
  - All amounts via `MoneyDisplay`
- [ ] Create `src/views/cash/ExpenseListView.vue`:
  - Expense table with filters: date range, category, branch, approval state
  - New expense form (inline or modal): date, category, branch, amount, payment source, attachment (`AppFileUpload`), approval state
  - If amount exceeds threshold: `useStepUpAuth('expense_approval')` required before submit
- [ ] Add routes `/cash` and `/cash/expenses` to router
- [ ] Add Cash section to `AppSidebar` nav

---

## Task 13: Customers / CRM — Duplicate Warning, Credit Limit, Ledger

- [ ] Update `src/views/customers/CustomerListView.vue`:
  - Duplicate-warning modal on create: call `check_duplicate` before save, show matching record if found
- [ ] Update `src/views/customers/CustomerDetailView.vue`:
  - Add `AppTabs`: Profile | Purchases | Repairs | Installments | Ledger | Communications
  - Ledger tab: read-only table (Date | Description | Reference | Debit | Credit | Balance) — no edit inputs
  - Running balance computed from entries
  - Communications tab: history list from `GET /api/v1/customers/:id/history/`
  - Wholesale price tier display (`<PermGate perm="view_cost">`)
- [ ] Update `src/stores/cart.js` checkout guard:
  - Before finalize, check `customer.outstanding_balance + grandTotal > customer.credit_limit`
  - If exceeded: block checkout, show credit-limit exceeded message, require manager step-up to override
- [ ] Add `CustomerLedgerView.vue` as standalone report page (for Reports → Customer Ledger)

---

## Task 14: Reports — All 10 Types

- [ ] Create `src/views/reports/ImeiHistoryView.vue` — device IMEI with full lifecycle events per device
- [ ] Create `src/views/reports/StaffReportView.vue` — `<PermGate perm="view_reports">`, sales/repair counts per staff member
- [ ] Create `src/views/reports/DeadStockView.vue` — accessories with no movement in configurable window
- [ ] Create `src/views/reports/CashReportView.vue` — cash sessions, variance totals
- [ ] Create `src/views/reports/CustomerLedgerView.vue` — customer selector + ledger table
- [ ] Update all existing report views (`SalesReportView`, `ProfitReportView`, `InventoryReportView`, `RepairReportView`, `InstallmentReportView`) to:
  - Use `AppDateRange` for date filter
  - Add branch filter
  - Wrap cost/profit columns in `<PermGate>`
  - Add CSV export button calling `GET /api/v1/reports/:slug/export/`
- [ ] Update `src/views/reports/ReportsLayout.vue` — add tabs for all 10 report types
- [ ] Add all new report routes to router

---

## Task 15: Multi-Branch Transfers

- [ ] Create `src/api/transfers.js` — `list(params)`, `create(data)`, `get(id)`, `dispatch(id)`, `receive(id)`
- [ ] Create `src/views/transfers/TransferListView.vue`:
  - Table with filters: status, source branch, destination branch, date range
  - Status badges: Pending / Dispatched / Received / Cancelled
  - Create Transfer button
- [ ] Create `src/views/transfers/TransferDetailView.vue`:
  - Transfer header: source → destination, status, created by
  - Line items: item/IMEI, qty, received qty
  - Action buttons by status:
    - Pending → Dispatch (with confirm + effect: "X items will leave [Branch A]")
    - Dispatched → Receive (with confirm + effect: "X items will enter [Branch B]")
  - All destructive actions use `ConfirmDialog` with inventory effect
- [ ] Add transfers section to `AppSidebar` nav
- [ ] Add transfer routes to router

---

## Task 16: Admin — Permission Matrix, User Management, Audit Log

- [ ] Update `src/views/settings/UsersSettingsView.vue`:
  - Add user creation form (username, password, role, branch access)
  - Deactivate user with `ConfirmDialog` + `useStepUpAuth('user_deactivate')`
- [ ] Rewrite `src/views/settings/RolesSettingsView.vue`:
  - Full permission matrix grid: 11 module rows × 9 permission columns
  - Each cell is a checkbox
  - Save role requires `useStepUpAuth('permission_change')` before calling `PATCH /api/v1/admin/roles/:id/`
- [ ] Create `src/views/settings/AuditLogView.vue`:
  - Read-only table: Timestamp | Actor | Action | Entity Type | Entity ID | Changes
  - Zero create/edit/delete affordances
  - Filters: actor, entity type, entity ID, action, date range (`AppDateRange`)
  - Changes cell: collapsed by default, expandable to show before/after field diff
- [ ] Update `src/views/settings/SettingsLayout.vue` — add Audit Log tab (gated by admin permission)

---

## Task 17: Invoice Print — 80mm Thermal & A4

- [ ] Finalize `src/components/pos/ReceiptPrint.vue`:
  - 80mm layout: 80mm-wide column, 10px font, company name/address centered, divider line, per-item rows (product name | qty × price | line total), IMEI per serialized item, totals block, tenders block, change, return policy text, invoice barcode via JsBarcode
  - A4 layout: letterhead, formal table, full address blocks, totals, signatures area
  - Both layouts hidden outside print via `@media print`
  - `layout` prop switches which layout renders inside `#print-target`
- [ ] Finalize `@media print` CSS in `src/assets/main.css` — hide body children, show only `#print-target`
- [ ] Test both print layouts in browser print preview

---

## Task 18: Integration, Route Audit & Build Verification

- [ ] Audit all 13 modules against requirements.md — check every acceptance criterion has a corresponding UI element or behavior
- [ ] Audit `ConfirmDialog` usage — every `btn-danger` action must pass a non-null `effect` prop; add `console.error` warning in dev if missing
- [ ] Audit all money values — grep templates and computed properties for raw `.toFixed`, `parseFloat` display, or unformatted number bindings; replace with `MoneyDisplay` or `formatMoney()`
- [ ] Audit all `<input>` / `<select>` / `<textarea>` in `CustomerDetailView` and `CustomerLedgerView` — verify zero balance-edit fields
- [ ] Audit finalized invoice views — verify `isEditable` guards are present and no edit inputs render when status is `finalized`, `paid`, or `returned`
- [ ] Run `npm run build` — fix all compile errors and warnings
- [ ] Smoke test mock layer — navigate every route, verify no blank views or console errors
- [ ] Verify `VITE_USE_MOCK=false` build compiles without mock imports leaking into production bundle (check that MSW import is inside a dynamic `import()` gated by the env flag)
