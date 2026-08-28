# Requirements Document

## Introduction

DEVNEST is a Mobile Retail ERP & POS frontend built with Vue 3, Pinia, Vue Router, Tailwind CSS, and Axios. It covers 13 functional modules: Auth & Shell, Dashboard, Inventory (Serialized Devices/IMEI and Accessories & Parts), Purchasing & Trade-In, POS / Sales, Repair / Lab Service, Installments & Khata, Cash & Expenses, Customers / CRM, Reports, Multi-Branch & Transfers, and Admin (Roles, Users, Audit). The backend (Django/DRF) is developed separately; all frontend work runs against an in-process mock API layer (MSW) that is swapped for real Axios calls via a single environment flag without any component changes.

Eight non-negotiable system-wide constraints must be satisfied across every module: money formatting, double-enforced permissions, finalized-record immutability, scanner focus preservation, Khata ledger balance integrity, destructive-action effect disclosure, mock/real API structural parity, and single-use step-up tokens.

---

## Glossary

- **System**: The DEVNEST ERP frontend application.
- **Router**: Vue Router — manages navigation and route guards.
- **Auth_Store**: Pinia `auth` store — holds user, token, permissions Set, and branch list.
- **Branch_Store**: Pinia `branch` store — holds `activeBranchId` and `branchList`.
- **Cart_Store**: Pinia `cart` store — holds POS cart items, tenders, trade-in, and discount state.
- **Cash_Session_Store**: Pinia `cashSession` store — holds session state machine.
- **Repair_Board_Store**: Pinia `repairBoard` store — holds kanban stage columns.
- **UI_Store**: Pinia `ui` store — holds toast, confirmDialog, and stepUpAuthDialog state.
- **Sync_Store**: Pinia `sync` store — holds network online status and pending request count.
- **PermGate**: Vue component `PermGate.vue` — renders slot only when the user holds the specified permission.
- **usePermissions**: Vue composable — exposes `can(codename)` and `canViewCost()` helpers.
- **useStepUpAuth**: Vue composable — triggers `StepUpAuthModal`, returns `Promise<boolean>`.
- **StepUpAuthModal**: Modal component that prompts for password re-verification before a privileged action.
- **Step_Up_Token**: A short-lived, single-use OTP returned by `POST /api/v1/auth/step-up/` and attached as `X-Step-Up-Token` to the subsequent privileged request.
- **ConfirmDialog**: UI component that displays a destructive-action confirmation with a mandatory `effect` string.
- **MoneyDisplay**: UI component that renders monetary values exclusively through `formatMoney()`.
- **formatMoney()**: Utility function `src/utils/money.js` — converts integer paise to a locale-formatted PKR string.
- **ScannerInput**: POS component with `data-no-scanner-refocus` guard logic.
- **BranchSelector**: Header component that writes to `Branch_Store.activeBranchId`.
- **Axios_Client**: `src/api/client.js` — Axios instance with token injection and `X-Branch-ID` request interceptor.
- **MSW**: Mock Service Worker — intercepts HTTP at Service Worker level in development.
- **VITE_USE_MOCK**: `.env` flag — `true` activates MSW mock layer; `false` routes to real backend.
- **ReceiptPrint**: POS component that renders 80mm thermal and A4 invoice layouts.
- **AppKanban**: Vue component for the drag-and-drop repair stage board.
- **AppTimeline**: Vue component for IMEI device lifecycle event log.
- **InstallmentPlanBuilder**: View that reactively computes installment schedule from sale parameters.
- **useAging**: Composable that classifies overdue installment plans into five time buckets.
- **ChartWithTable**: Dashboard component combining a vue-chartjs chart with a toggleable drill-down table.
- **AuditLog**: Read-only log of all system actions with actor, entity, action type, and before/after diff.
- **PermissionMatrix**: Admin UI — a grid of module rows × permission columns with checkbox cells.

---

## Requirements

### Requirement 1: Authentication & Application Shell

**User Story:** As a staff member, I want to log in securely and navigate a permission-aware shell, so that I can access only the modules and actions my role allows.

#### Acceptance Criteria

1. WHEN a user submits valid credentials, THE Auth_Store SHALL store the returned `token`, `user`, and `permissions` set and redirect to the dashboard.
2. IF a user submits invalid credentials, THEN THE System SHALL display an error message and leave the user on the login page.
3. WHEN an unauthenticated user attempts to navigate to any protected route, THE Router SHALL redirect to the login page.
4. WHEN an authenticated user attempts to navigate to a route whose required permission is not in `Auth_Store.permissions`, THE Router SHALL redirect to the dashboard with an "Access Denied" toast.
5. WHILE a user is authenticated, THE AppTopBar SHALL display the active branch name and a `BranchSelector` dropdown.
6. WHEN a user selects a different branch in the `BranchSelector`, THE Branch_Store SHALL update `activeBranchId` and THE System SHALL reload all active list views.
7. WHILE the application is running, THE Sync_Store SHALL reflect network online status and pending request count in the `SyncIndicator`.
8. WHEN a privileged action requires re-verification, THE useStepUpAuth SHALL display the `StepUpAuthModal` and return a resolved `Promise<boolean>` indicating whether verification succeeded.
9. WHEN `StepUpAuthModal` verification succeeds, THE System SHALL attach the `Step_Up_Token` as `X-Step-Up-Token` on the immediately following privileged API call.
10. WHEN the privileged API call resolves (success or failure), THE useStepUpAuth SHALL clear the `Step_Up_Token` from memory immediately.
11. WHEN a 401 response is received by `Axios_Client`, THE System SHALL clear the auth token and redirect to the login page.

---

### Requirement 2: Dashboard

**User Story:** As a manager, I want an exception-first dashboard with KPI metrics and interactive charts, so that I can quickly identify problems and drill into details.

#### Acceptance Criteria

1. WHEN the dashboard loads, THE DashboardView SHALL render exception alerts before the KPI strip.
2. WHEN the dashboard loads, THE DashboardView SHALL display a KPI strip containing today's sales total, gross profit, repair jobs in progress, and overdue installment count — all monetary values formatted through `formatMoney()`.
3. WHEN a chart is displayed, THE ChartWithTable SHALL provide a toggle between chart view and drill-down table view showing the same underlying dataset.
4. WHEN a user clicks the table-view toggle, THE ChartWithTable SHALL render the data as a sortable table without fetching new data.
5. WHEN a user changes the date-range filter on any dashboard chart, THE ChartWithTable SHALL reload the chart data for the selected range.
6. WHERE a user does not have the `view_profit` permission, THE PermGate SHALL suppress rendering of gross-profit KPI and profit-related chart data.

---

### Requirement 3: Inventory — Serialized Devices (IMEI)

**User Story:** As an inventory manager, I want to track serialized devices by IMEI with full lifecycle history, so that I can manage stock accurately and detect anomalies.

#### Acceptance Criteria

1. WHEN a new device is added, THE System SHALL call `GET /api/v1/inventory/devices/check_duplicate/?imei=<imei>` before saving, and IF a duplicate IMEI is detected THEN THE System SHALL display a duplicate-warning modal and prevent the save until the user explicitly acknowledges.
2. WHEN a device detail page loads, THE AppTimeline SHALL render all lifecycle events in chronological order, each event showing timestamp, actor, and event type.
3. WHERE a timeline event type is `price_change` or `acquisition`, THE PermGate SHALL gate that event's display behind the `view_cost` permission.
4. WHEN a cost adjustment is submitted, THE useStepUpAuth SHALL require step-up re-authentication before calling `POST /api/v1/inventory/devices/:id/adjust_cost/`.
5. WHEN a device list is displayed, THE DeviceListView SHALL paginate results and filter by branch via the `X-Branch-ID` header injected by `Axios_Client`.

---

### Requirement 4: Inventory — Accessories & Parts

**User Story:** As a warehouse operator, I want to manage accessory stock levels with movement tracking and barcode labels, so that I have accurate counts and can label items for the shelf.

#### Acceptance Criteria

1. WHEN a stock adjustment is submitted for an accessory, THE System SHALL call `POST /api/v1/inventory/accessories/:id/adjust_stock/` and record a stock movement entry retrievable from `GET /api/v1/inventory/accessories/:id/movements/`.
2. WHEN the low-stock view loads, THE System SHALL call `GET /api/v1/inventory/low-stock/` and display all accessories whose quantity is at or below their reorder level.
3. WHEN a barcode scan is performed in any inventory lookup, THE System SHALL call `GET /api/v1/inventory/scan/?q=<barcode|imei>` and navigate to the matching item detail.
4. WHEN the barcode label print view loads, THE BarcodeLabelsView SHALL allow the user to select any combination of: Name, SKU, Price, Barcode, QR, Branch, and Category fields for inclusion on the label.
5. WHEN labels are printed, THE System SHALL render only the user-selected fields in the label preview and the print output, with barcodes generated via `jsbarcode` and QR codes via the `qrcode` package.
6. WHEN a monetary value (Price) is included in a barcode label, THE System SHALL render it through `formatMoney()`.

---

### Requirement 5: Purchasing & Trade-In

**User Story:** As a purchasing officer, I want to create purchase orders with partial receiving and intake used phones as acquisitions, so that I can accurately track incoming stock.

#### Acceptance Criteria

1. WHEN a purchase order is created, THE System SHALL call `POST /api/v1/purchases/orders/` and the order SHALL have an initial status of `open`.
2. WHEN a partial receiving is submitted for a purchase order, THE System SHALL call `POST /api/v1/purchases/orders/:id/receive/` with the received quantities, and the PO status SHALL remain `open` until all quantities are fully received.
3. WHEN all line-item quantities on a purchase order are fully received, THE System SHALL automatically transition the PO status to `closed`.
4. WHEN a used-phone acquisition is submitted, THE System SHALL call `POST /api/v1/purchases/acquisitions/` and create a device record with status `acquired`.
5. WHEN a trade-in is initiated inside the POS, THE TradeInPanel SHALL update `Cart_Store.tradeIn` with `{ unitId, imei, acceptedValue }` and the grand total SHALL be recalculated as: `subtotal + tax − invoiceDiscount − tradeIn.acceptedValue`.
6. WHEN a trade-in accepted value is displayed in the POS, THE System SHALL render it through `formatMoney()`.

---

### Requirement 6: POS / Sales

**User Story:** As a cashier, I want to process sales with split payments, discount approvals, and printed receipts, so that I can complete transactions accurately and provide customers with proof of purchase.

#### Acceptance Criteria

1. WHEN a cashier adds payment tenders, THE Cart_Store SHALL maintain `totalTendered` equal to the sum of all individual tender amounts, and `remainingDue` equal to `grandTotal − totalTendered`.
2. WHEN `totalTendered` exceeds `grandTotal`, THE Cart_Store SHALL compute `changeAmount` as `totalTendered − grandTotal`.
3. WHEN a discount amount exceeds `branchStore.settings.discountThreshold`, THE DiscountPanel SHALL block direct application and require step-up re-authentication via `useStepUpAuth` before the discount is applied.
4. WHEN a discount is below or equal to `branchStore.settings.discountThreshold`, THE DiscountPanel SHALL apply the discount directly without requiring approval.
5. WHEN a sale is finalized, THE System SHALL call `POST /api/v1/sales/invoices/:id/finalize/` and the invoice status SHALL become `finalized`.
6. WHEN an invoice has status `finalized`, `paid`, or `returned`, THE InvoiceDetailView SHALL replace the edit form with a correction-only interface — no editable fields SHALL be present.
7. WHEN a correction is initiated on a finalized invoice, THE System SHALL call `POST /api/v1/sales/invoices/:id/correct/` and create a linked correction record.
8. WHEN a receipt is printed, THE ReceiptPrint SHALL support both `80mm` thermal and `A4` layouts, selectable via the `layout` prop, and the correct CSS media rules SHALL hide all non-print content.
9. WHEN a scanner input is active in POS and a user clicks on any input element bearing the `data-no-scanner-refocus` attribute, THE ScannerInput SHALL NOT transfer focus to that element and SHALL retain scanner focus.
10. WHEN any monetary value is displayed in the POS (line items, subtotal, tax, discount, grand total, change), THE System SHALL render it through `formatMoney()`.
11. WHEN a void action is initiated for an invoice, THE ConfirmDialog SHALL display the financial effect (e.g., total voided amount and inventory restoration) before the user confirms.

---

### Requirement 7: Repair / Lab Service

**User Story:** As a repair technician, I want to manage repair jobs through a visual kanban board with parts tracking and customer approvals, so that I can handle repairs efficiently from intake to delivery.

#### Acceptance Criteria

1. WHEN the repair board loads, THE RepairBoardView SHALL display repair jobs in ten stage columns: `received`, `diagnosing`, `awaiting_approval`, `waiting_parts`, `in_repair`, `qc`, `repaired`, `unrepairable`, `ready`, `delivered`.
2. WHEN a technician drags a repair job card to a different column, THE Repair_Board_Store SHALL call `POST /api/v1/repairs/jobs/:id/update_status/` optimistically, updating the UI immediately and rolling back on API error.
3. WHEN a repair requires customer approval (stage `awaiting_approval`), THE RepairDetailView SHALL display an approval-prompt interface and only advance the job after the approval is recorded.
4. WHEN parts are consumed on a repair job, THE System SHALL decrement accessory stock accordingly via the inventory adjustment API.
5. WHEN a repair job is delivered, THE System SHALL call `POST /api/v1/repairs/jobs/:id/deliver/` and settle any outstanding payment balance.
6. WHEN a destructive status change (e.g., marking `unrepairable`) is confirmed, THE ConfirmDialog SHALL display the operational effect before the user confirms.

---

### Requirement 8: Installments & Khata

**User Story:** As a finance officer, I want to build installment plans, track overdue accounts by aging bucket, and view customer ledgers, so that I can manage credit sales and follow up on overdue payments.

#### Acceptance Criteria

1. WHEN a user inputs sale amount, down payment, markup rate, and installment count in the plan builder, THE InstallmentPlanBuilder SHALL reactively recompute: `financedAmount = saleAmount − downPayment`, `totalPayable = financedAmount × (1 + markupRate / 100)`, `installmentAmount = totalPayable / installmentCount`, and display a live preview table of all installment due dates and amounts.
2. WHEN the installment count does not divide `totalPayable` evenly, THE InstallmentPlanBuilder SHALL apply the remainder to the last installment.
3. WHEN the overdue aging view loads, THE useAging SHALL classify overdue plans into five buckets: `1–7d`, `8–30d`, `31–60d`, `61–90d`, `90d+`, and THE OverdueAgingView SHALL display count and total amount per bucket.
4. THE CustomerDetailView and CustomerLedgerView SHALL NOT contain any `<input>`, `<select>`, or `<textarea>` element that writes to or modifies a customer's running balance.
5. WHEN the customer ledger is displayed, THE System SHALL compute the running balance as the cumulative sum of debit and credit entries from `GET /api/v1/customers/:id/ledger/`.
6. WHEN installment amounts are displayed, THE System SHALL render them through `formatMoney()`.

---

### Requirement 9: Cash & Expenses

**User Story:** As a cashier, I want to open and close cash sessions with variance tracking and record expenses, so that I can reconcile daily cash accurately.

#### Acceptance Criteria

1. WHEN a cash session is opened, THE Cash_Session_Store SHALL transition from `CLOSED` to `OPEN` state and call `POST /api/v1/cash/sessions/open/` with the opening amount.
2. WHEN a session close is initiated, THE Cash_Session_Store SHALL transition to `PENDING_COUNT` state and prompt the cashier to enter the physically counted amount.
3. WHEN a counted amount is submitted, THE Cash_Session_Store SHALL compute `variance = countedAmount − expectedAmount` and transition to `RECONCILED` state.
4. WHEN the session is confirmed closed, THE Cash_Session_Store SHALL call `POST /api/v1/cash/sessions/close/` and transition to `CLOSED` (archived) state.
5. WHEN an expense entry is submitted, THE System SHALL call `POST /api/v1/cash/expenses/` with category, amount, and note.
6. IF an expense amount exceeds the branch approval threshold, THEN THE System SHALL require step-up re-authentication via `useStepUpAuth` before submitting.
7. WHEN cash amounts are displayed (opening amount, inflows, outflows, variance, closing count), THE System SHALL render them through `formatMoney()`.

---

### Requirement 10: Customers / CRM

**User Story:** As a sales associate, I want to manage customer profiles with duplicate prevention, credit-limit enforcement at POS, and communication history, so that I can provide consistent service and control credit risk.

#### Acceptance Criteria

1. WHEN a new customer is being created or updated, THE System SHALL call `GET /api/v1/customers/check_duplicate/?name=&phone=` and IF a potential duplicate is detected THEN THE System SHALL display a duplicate-warning modal before allowing the save to proceed.
2. WHEN a POS transaction is being finalized for a customer whose outstanding balance plus the current cart total exceeds their `creditLimit`, THE System SHALL block checkout and display a credit-limit exceeded message.
3. WHEN the customer detail page loads, THE CustomerDetailView SHALL display a communication history tab showing all past interactions retrieved from `GET /api/v1/customers/:id/history/`.
4. WHEN customer monetary values are displayed (balance, credit limit, transaction amounts), THE System SHALL render them through `formatMoney()`.

---

### Requirement 11: Reports

**User Story:** As a manager, I want to generate, filter, and export 10 different report types, so that I can analyze business performance and share data with stakeholders.

#### Acceptance Criteria

1. THE System SHALL provide the following ten report types: Sales Summary, Profit & Loss, Inventory Valuation, IMEI History, Repairs, Installments, Customer Ledger, Staff Performance, Dead Stock, and Cash Report.
2. WHEN a report is opened, THE System SHALL accept `date_from`, `date_to`, and `branch` filter parameters and call the corresponding report endpoint with those parameters.
3. WHEN filter parameters are changed, THE System SHALL reload the report data without a full page refresh.
4. WHEN a user triggers CSV export for a report, THE System SHALL call `GET /api/v1/reports/:slug/export/` and download the resulting CSV blob.
5. WHERE a user does not hold the permission required for a specific report, THE PermGate SHALL suppress rendering of that report's navigation link and view content.
6. WHERE a user does not hold the `view_profit` permission, THE PermGate SHALL suppress rendering of profit and cost columns in all report views.
7. WHEN monetary values are displayed in any report, THE System SHALL render them through `formatMoney()`.

---

### Requirement 12: Multi-Branch & Transfers

**User Story:** As a branch manager, I want to transfer stock between branches with an approval workflow, so that I can redistribute inventory while maintaining an auditable approval trail.

#### Acceptance Criteria

1. WHEN a branch is selected via `BranchSelector`, THE Branch_Store SHALL update `activeBranchId` and THE Axios_Client SHALL inject the new value as `X-Branch-ID` on all subsequent API requests.
2. WHEN the active branch changes, THE System SHALL reload all active list views to reflect the new branch context.
3. WHEN a stock transfer is created, THE System SHALL call `POST /api/v1/transfers/` and the transfer SHALL have initial status `pending`.
4. WHEN a transfer is dispatched by the sending branch, THE System SHALL call `POST /api/v1/transfers/:id/dispatch/` and transition the status to `dispatched`.
5. WHEN a transfer is received by the destination branch, THE System SHALL call `POST /api/v1/transfers/:id/receive/` and transition the status to `received`.
6. WHEN a destructive transfer action (cancel or force-close) is confirmed, THE ConfirmDialog SHALL display the inventory effect (items and quantities affected) before the user confirms.

---

### Requirement 13: Admin — Roles, Users & Audit

**User Story:** As a system administrator, I want to manage users, configure role permissions via a matrix, and review an immutable audit log, so that I can maintain access control and accountability.

#### Acceptance Criteria

1. WHEN an administrator opens the roles editor, THE RolesSettingsView SHALL display a permission matrix with module rows (Dashboard, Inventory, POS, Repairs, Purchases, Installments, Cash, Customers, Reports, Transfers, Admin) and permission columns (view, create, edit, approve, void, export, view_cost, view_profit, configure), with each cell as a checkbox.
2. WHEN a permission checkbox is toggled in the matrix, THE System SHALL update the role's flat `permissions` array and call `PATCH /api/v1/admin/roles/:id/` to persist the change.
3. WHEN any role or user configuration change is submitted, THE useStepUpAuth SHALL require step-up re-authentication before calling the admin API.
4. WHEN a user is deactivated, THE System SHALL call `POST /api/v1/admin/users/:id/deactivate/` and the deactivated user SHALL be prevented from logging in.
5. WHEN the audit log view loads, THE AuditLogView SHALL display a read-only table with columns: Timestamp, Actor, Action, Entity Type, Entity ID, and Changes — with no create, edit, or delete controls present.
6. WHEN the audit log is filtered, THE System SHALL accept actor, entity type, entity ID, action, and date-range parameters and call `GET /api/v1/admin/audit-log/` with those parameters.
7. WHEN a changes cell in the audit log is expanded, THE System SHALL display the before/after diff of all changed fields for that entry.

---

### Requirement 14: System-Wide Non-Negotiable Constraints

**User Story:** As a system architect, I want universal constraints enforced across every module, so that money values are always accurate, permissions always enforced, and the system is safe to operate against both mock and real APIs.

#### Acceptance Criteria

1. THE System SHALL render every monetary value exclusively through `formatMoney()` — raw JavaScript `number` or `float` values SHALL NOT appear in any template, computed property result, or rendered DOM node representing money.
2. THE System SHALL double-enforce every permission: THE Router SHALL block navigation for routes requiring a permission the user does not hold, AND THE PermGate / usePermissions SHALL suppress rendering of UI elements gated by that permission.
3. WHEN a permission change occurs for the current user mid-session, THE System SHALL re-fetch `GET /api/v1/auth/me/` and update `Auth_Store.permissions` before re-rendering permission-gated content.
4. WHEN any invoice, receipt, or settlement record reaches a finalized state (`finalized`, `paid`, or `returned`), THE System SHALL remove all edit-capable input elements from the view and present only correction or reversal flow controls.
5. WHEN an active scanner input is present in POS and a user interaction would normally shift focus to an input element carrying `data-no-scanner-refocus`, THE ScannerInput's `handleBodyClick` handler SHALL NOT redirect focus away from the scanner input.
6. THE CustomerDetailView and CustomerLedgerView SHALL contain zero `<input>`, `<select>`, or `<textarea>` elements that write to or modify the Khata running balance.
7. WHEN any destructive action (void, return, adjustment, transfer cancellation, deletion) is triggered, THE ConfirmDialog SHALL display a non-null `effect` string describing the financial or inventory consequence before the user confirms, and IF the `effect` prop is omitted for a danger-class action THEN THE System SHALL emit a `console.error` warning in development mode.
8. WHEN `VITE_USE_MOCK` is toggled between `true` and `false`, THE System SHALL require zero changes to store actions or view components — mock handlers SHALL return JSON with the same schema as the corresponding DRF serializer contracts.
9. WHEN a `Step_Up_Token` is returned by `POST /api/v1/auth/step-up/`, THE useStepUpAuth SHALL use it exactly once as `X-Step-Up-Token` on the immediately following privileged API call, and SHALL clear it from memory immediately after that call resolves regardless of success or failure.
10. WHEN a `Step_Up_Token` has been cleared after use, THE System SHALL NOT attach any step-up token header to subsequent API calls unless a new step-up verification is completed.
