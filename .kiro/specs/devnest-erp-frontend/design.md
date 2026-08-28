# DEVNEST ERP Frontend — Technical Design

## Overview

Full Vue 3 frontend for a Mobile Retail ERP & POS platform covering 13 modules. The backend (Django/DRF) is not yet ready; all component work runs against an in-process **mock API layer** that is swapped out for real Axios calls via a single env flag.

---

## 1. High-Level Design

### 1.1 Directory Structure

```
src/
├── api/
│   ├── client.js             # Axios instance, token injection, 401 redirect
│   ├── mock/
│   │   ├── index.js          # Mount/unmount MSW worker or in-memory adapter
│   │   ├── handlers/         # One file per domain (auth, inventory, sales …)
│   │   │   ├── auth.js
│   │   │   ├── inventory.js
│   │   │   ├── sales.js
│   │   │   ├── repairs.js
│   │   │   ├── installments.js
│   │   │   ├── purchases.js
│   │   │   ├── customers.js
│   │   │   ├── cash.js
│   │   │   ├── reports.js
│   │   │   ├── branches.js
│   │   │   └── admin.js
│   │   └── db/               # In-memory fixture data (seeded once at startup)
│   │       ├── users.js
│   │       ├── devices.js
│   │       ├── accessories.js
│   │       ├── invoices.js
│   │       └── …
│   ├── auth.js
│   ├── inventory.js
│   ├── sales.js
│   ├── repairs.js
│   ├── installments.js
│   ├── purchases.js
│   ├── customers.js
│   ├── cash.js
│   ├── reports.js
│   ├── branches.js
│   └── admin.js
│
├── assets/
│   └── main.css              # Tailwind v4 + design system tokens
│
├── components/
│   ├── layout/
│   │   ├── AppShell.vue
│   │   ├── AppSidebar.vue
│   │   ├── AppTopBar.vue
│   │   ├── BranchSelector.vue   # NEW — header branch switcher
│   │   ├── SyncIndicator.vue
│   │   └── StepUpAuthModal.vue  # NEW — re-auth gate for privileged actions
│   │
│   ├── ui/                   # existing base components + additions:
│   │   ├── AppButton.vue
│   │   ├── AppInput.vue
│   │   ├── AppSelect.vue
│   │   ├── AppBadge.vue
│   │   ├── AppModal.vue
│   │   ├── AppTable.vue
│   │   ├── AppPagination.vue
│   │   ├── MoneyDisplay.vue
│   │   ├── ConfirmDialog.vue
│   │   ├── ToastContainer.vue
│   │   ├── AppTabs.vue          # NEW — horizontal tab bar
│   │   ├── AppDateRange.vue     # NEW — from/to date picker pair
│   │   ├── AppFileUpload.vue    # NEW — drag-drop + preview
│   │   ├── AppTimeline.vue      # NEW — lifecycle event log
│   │   ├── AppKanban.vue        # NEW — repair stage board
│   │   ├── AppPrintFrame.vue    # NEW — iframe-based print wrapper
│   │   └── PermGate.vue         # NEW — v-if wrapper by permission codename
│   │
│   ├── charts/
│   │   ├── LineChart.vue        # vue-chartjs wrapper
│   │   ├── BarChart.vue
│   │   ├── DonutChart.vue
│   │   └── ChartWithTable.vue   # chart + drill-down table toggle
│   │
│   └── pos/
│       ├── ScannerInput.vue
│       ├── CartItem.vue
│       ├── CartTotals.vue
│       ├── PaymentPanel.vue     # NEW — multi-tender split payment
│       ├── DiscountPanel.vue    # NEW — threshold approval prompt
│       ├── TradeInPanel.vue     # NEW — trade-in inside sale flow
│       └── ReceiptPrint.vue     # NEW — 80mm / A4 print layout switcher
│
├── composables/
│   ├── useScanner.js
│   ├── usePermissions.js
│   ├── usePagination.js
│   ├── useConfirm.js
│   ├── useForm.js
│   ├── useStepUpAuth.js         # NEW — triggers StepUpAuthModal, returns Promise<bool>
│   ├── useBranch.js             # NEW — active branch from branchStore
│   ├── usePrint.js              # NEW — wraps AppPrintFrame, triggers window.print()
│   ├── useChartData.js          # NEW — fetches + normalises chart data, exposes tableRows
│   └── useAging.js              # NEW — overdue installment aging bucket calc
│
├── router/
│   └── index.js                 # extends existing route tree (see §1.3)
│
├── stores/
│   ├── auth.js                  # existing — add branch list + active branch
│   ├── cart.js                  # existing — add split-payment tenders, trade-in
│   ├── sync.js                  # existing
│   ├── ui.js                    # existing — add stepUpAuth dialog state
│   ├── inventory.js             # existing — extend for IMEI devices + accessories
│   ├── branch.js                # NEW
│   ├── cashSession.js           # NEW
│   └── repairBoard.js           # NEW — kanban column state
│
└── views/
    ├── auth/          LoginView.vue
    ├── dashboard/     DashboardView.vue           (exception-first, charts)
    ├── pos/           PosView.vue                 (extended: split pay, trade-in, print)
    ├── inventory/
    │   ├── InventoryLayout.vue
    │   ├── DeviceListView.vue                     (IMEI devices)
    │   ├── DeviceDetailView.vue
    │   ├── DeviceAddView.vue
    │   ├── AccessoryListView.vue
    │   ├── AccessoryDetailView.vue
    │   └── BarcodeLabelsView.vue
    ├── sales/
    │   ├── InvoiceListView.vue
    │   ├── InvoiceDetailView.vue
    │   └── InvoiceCorrectionView.vue              (return/exchange/void)
    ├── repairs/
    │   ├── RepairListView.vue
    │   ├── RepairBoardView.vue                    (kanban)
    │   ├── RepairDetailView.vue
    │   └── RepairNewView.vue
    ├── purchases/
    │   ├── PurchaseListView.vue
    │   ├── PurchaseNewView.vue
    │   ├── PurchaseDetailView.vue
    │   └── AcquisitionView.vue                    (used-phone intake)
    ├── installments/
    │   ├── InstallmentListView.vue
    │   ├── InstallmentDetailView.vue
    │   ├── InstallmentPlanBuilderView.vue
    │   └── OverdueAgingView.vue
    ├── cash/
    │   ├── CashSessionView.vue
    │   └── ExpenseListView.vue
    ├── customers/
    │   ├── CustomerListView.vue
    │   └── CustomerDetailView.vue
    ├── reports/
    │   ├── ReportsLayout.vue
    │   ├── SalesReportView.vue
    │   ├── ProfitReportView.vue
    │   ├── InventoryReportView.vue
    │   ├── ImeiHistoryView.vue
    │   ├── RepairReportView.vue
    │   ├── InstallmentReportView.vue
    │   ├── CustomerLedgerView.vue
    │   ├── StaffReportView.vue
    │   ├── DeadStockView.vue
    │   └── CashReportView.vue
    ├── transfers/
    │   ├── TransferListView.vue
    │   └── TransferDetailView.vue
    └── settings/
        ├── SettingsLayout.vue
        ├── CompanySettingsView.vue
        ├── UsersSettingsView.vue
        ├── RolesSettingsView.vue
        ├── TaxSettingsView.vue
        └── AuditLogView.vue
```

---

### 1.2 Mock API Architecture

**Strategy:** Use [MSW (Mock Service Worker)](https://mswjs.io/) in browser mode during development. MSW intercepts `fetch`/XHR at the Service Worker level — Axios calls pass through unchanged, so zero changes to production API code when switching.

```
┌──────────────────────────────────────────┐
│  Vue App                                 │
│  ┌─────────────────────────────────────┐ │
│  │ api/client.js (Axios)               │ │
│  │   → all real URL calls              │ │
│  └────────────────┬────────────────────┘ │
└───────────────────┼──────────────────────┘
                    │ HTTP to localhost:8000
         ┌──────────┴──────────┐
         │  VITE_USE_MOCK=true │
         │  MSW Service Worker │  ← intercepts, never hits network
         │  src/api/mock/      │
         └─────────────────────┘
         ┌──────────────────────┐
         │  VITE_USE_MOCK=false │
         │  → real backend      │
         └──────────────────────┘
```

**Toggle in `src/main.js`:**
```js
if (import.meta.env.VITE_USE_MOCK === 'true') {
  const { worker } = await import('./api/mock/index.js')
  await worker.start({ onUnhandledRequest: 'bypass' })
}
```

**Handler pattern (`src/api/mock/handlers/sales.js`):**
```js
import { http, HttpResponse } from 'msw'
import { db } from '../db/index.js'

export const salesHandlers = [
  http.get('/api/v1/sales/invoices/', ({ request }) => {
    const url = new URL(request.url)
    const page = parseInt(url.searchParams.get('page') || '1')
    const results = db.invoices.paginate(page, 25)
    return HttpResponse.json(results)
  }),
  http.post('/api/v1/sales/invoices/', async ({ request }) => {
    const body = await request.json()
    const invoice = db.invoices.create(body)
    return HttpResponse.json(invoice, { status: 201 })
  }),
]
```

**In-memory DB (`src/api/mock/db/index.js`):**
```js
// Minimal factory — each entity gets create/list/get/update/delete + paginate
export const db = {
  invoices: createStore(invoiceFixtures),
  devices:  createStore(deviceFixtures),
  // …
}
```

---

### 1.3 Route Tree Additions

```
/cash                        → CashSessionView
/cash/expenses               → ExpenseListView
/inventory/devices           → DeviceListView
/inventory/devices/new       → DeviceAddView
/inventory/devices/:id       → DeviceDetailView
/inventory/labels            → BarcodeLabelsView
/repairs/board               → RepairBoardView  (kanban)
/purchases/acquisitions/new  → AcquisitionView
/installments/aging          → OverdueAgingView
/installments/new            → InstallmentPlanBuilderView
/transfers                   → TransferListView
/transfers/:id               → TransferDetailView
/reports/imei-history        → ImeiHistoryView
/reports/staff               → StaffReportView
/reports/dead-stock          → DeadStockView
/reports/cash                → CashReportView
/reports/customer-ledger     → CustomerLedgerView
/settings/audit              → AuditLogView
/sales/invoices/:id/correct  → InvoiceCorrectionView
```

---

### 1.4 Branch Awareness

Every API call that is branch-scoped injects `X-Branch-ID` via the Axios request interceptor:

```js
// src/api/client.js — added to request interceptor
import { useBranchStore } from '@/stores/branch'
const branch = useBranchStore()
if (branch.activeBranchId) {
  config.headers['X-Branch-ID'] = branch.activeBranchId
}
```

The `BranchSelector` component in the top bar writes to `branchStore.activeBranchId`. On change it triggers a `branchChanged` event that all list views listen to via a `watch` on `branchStore.activeBranchId`.

---

### 1.5 Pinia Store Responsibilities

| Store | Owns |
|---|---|
| `auth` | user, token, permissions Set, branch list, active branch |
| `branch` | activeBranchId, branchList, switcher open state |
| `cart` | items, customer, tenders (split payments), trade-in item, invoiceDiscount, notes |
| `sync` | networkOnline, pendingRequests, hasError |
| `ui` | toasts, confirmDialog, stepUpAuthDialog, sidebarOpen, globalLoading |
| `inventory` | products, units (IMEI), accessories, lowStockItems, pagination |
| `cashSession` | isOpen, openingAmount, sessionId, inflows, outflows, closingCount |
| `repairBoard` | columns (ordered stage list), jobsByColumn, dragState |

---

### 1.6 Permission Gate Pattern

**`PermGate.vue`** — renders slot only if user has permission:
```html
<PermGate perm="view_profit">
  <MoneyDisplay :value="grossProfit" />
</PermGate>
```

**In JS:**
```js
const { can, canViewCost } = usePermissions()
if (!can('void_invoices')) router.push('/dashboard')
```

**Step-up re-auth** for privileged actions (price override, discount > threshold, cost adjustment, refund, permission change):
```js
const { requireStepUp } = useStepUpAuth()
const allowed = await requireStepUp('cost_adjustment')
if (!allowed) return
```

---

### 1.7 Chart Integration

**Library:** `vue-chartjs` (wraps Chart.js, smaller bundle than ApexCharts, no CDN dep).

**`ChartWithTable.vue`** — every chart ships with a table toggle:
```
┌─────────────────────────────────┐
│ [Chart] [Table]   ← tab toggle  │
│                                  │
│  <LineChart />  or  <table />    │
│                                  │
│  [Export CSV]                    │
└─────────────────────────────────┘
```

```js
// useChartData.js
export function useChartData(fetchFn, { transform }) {
  const raw       = ref(null)
  const loading   = ref(false)
  const chartData = computed(() => transform.forChart(raw.value))
  const tableRows = computed(() => transform.forTable(raw.value))
  async function load(params) { loading.value = true; raw.value = (await fetchFn(params)).data; loading.value = false }
  return { chartData, tableRows, loading, load }
}
```

---

## 2. Low-Level Design

### 2.1 Key Composable Signatures

```ts
// useStepUpAuth.js
function useStepUpAuth(): {
  requireStepUp(action: string): Promise<boolean>
}

// useBranch.js
function useBranch(): {
  activeBranchId: Ref<number | null>
  branchName: ComputedRef<string>
  switchBranch(id: number): void
  branches: Ref<Branch[]>
}

// usePrint.js
function usePrint(): {
  printRef: Ref<HTMLElement | null>   // attach to the element to print
  print(layout: '80mm' | 'A4'): void
}

// useAging.js
function useAging(plans: Ref<InstallmentPlan[]>): {
  buckets: ComputedRef<{ label: string; count: number; amount: number }[]>
  // buckets: ['1–7d', '8–30d', '31–60d', '61–90d', '90d+']
}

// useChartData.js
function useChartData<T>(
  fetchFn: (params: object) => Promise<AxiosResponse<T>>,
  options: { transform: { forChart(raw: T): ChartData; forTable(raw: T): Row[] } }
): { chartData: ComputedRef<ChartData>; tableRows: ComputedRef<Row[]>; loading: Ref<boolean>; load(params: object): Promise<void> }
```

---

### 2.2 Cart Store — Extended for Split Payments & Trade-In

```ts
// stores/cart.js additions

// Tenders replaces single paymentMethod
tenders: Ref<{ method: string; amount: number }[]>

// Computed
totalTendered:  ComputedRef<number>   // sum of tenders
remainingDue:   ComputedRef<number>   // grandTotal - totalTendered
changeAmount:   ComputedRef<number>   // max(0, totalTendered - grandTotal)

// Trade-in
tradeIn: Ref<{ unitId: number; imei: string; acceptedValue: number } | null>
// grandTotal = subtotal + tax - invoiceDiscount - tradeIn.acceptedValue

// Actions
addTender(method: string, amount: number): void
removeTender(index: number): void
clearTenders(): void
setTradeIn(unit): void
clearTradeIn(): void
```

---

### 2.3 Discount Approval Flow

```
User enters discount
       │
       ▼
discount > branch.discountThreshold?
       │ yes                  │ no
       ▼                      ▼
DiscountPanel shows       Apply directly
approval prompt
(reason + approver PIN)
       │
       ▼
requireStepUp('discount_override')
       │ granted              │ denied
       ▼                      ▼
Apply discount          Revert to threshold
+ log approval          Show toast
```

**`DiscountPanel.vue` props:**
```ts
props: {
  modelValue: number           // discount amount
  subtotal: number
  threshold: number            // from branchStore.settings.discountThreshold
  onApproved: () => void
}
```

---

### 2.4 Invoice Print Layout

**`ReceiptPrint.vue`** renders into a hidden `<div ref="printRef">`, then `usePrint().print(layout)` calls `window.print()` with a `@media print` CSS rule that hides everything except `#print-target`.

```html
<!-- 80mm thermal -->
<div class="print-80mm">
  <p class="font-bold text-center">{{ company.name }}</p>
  <p class="text-center text-xs">{{ company.address }}</p>
  <hr />
  <!-- line items: product | qty | price -->
  <!-- totals block -->
  <!-- IMEI block per serialized item -->
  <!-- warranty/return policy text -->
  <!-- barcode of invoice number -->
</div>

<!-- A4 — shown/hidden by layout prop -->
<div class="print-a4">
  <!-- formal invoice layout with letterhead -->
</div>
```

CSS in `main.css`:
```css
@media print {
  body > * { display: none !important; }
  #print-target { display: block !important; }
  .print-80mm { width: 80mm; font-size: 10px; }
  .print-a4   { width: 210mm; }
}
```

---

### 2.5 IMEI Device Lifecycle Timeline

**`AppTimeline.vue` props:**
```ts
props: {
  events: {
    id: string | number
    timestamp: string
    actor: string
    type: 'acquisition' | 'inspection' | 'transfer' | 'price_change'
          | 'repair' | 'sale' | 'return' | 'adjustment' | 'quarantine'
    title: string
    detail?: string
    highlight?: boolean   // e.g. current state
  }[]
}
```

Rendered as a left-bordered vertical list with icon per event type. Cost-related events (`price_change`, `acquisition`) are wrapped in `<PermGate perm="view_cost">`.

---

### 2.6 Repair Kanban Board

**`repairBoard` store:**
```ts
const STAGES = [
  'received', 'diagnosing', 'awaiting_approval',
  'waiting_parts', 'in_repair', 'qc',
  'repaired', 'unrepairable', 'ready', 'delivered'
]

// state
columns: Record<string, RepairJob[]>  // keyed by stage value

// actions
loadBoard(branchId): Promise<void>
moveJob(jobId, fromStage, toStage): Promise<void>  // calls repairsApi.updateStatus + optimistic update
```

**`AppKanban.vue` props:**
```ts
props: {
  columns: { key: string; label: string; items: object[] }[]
  itemKey: string
}
// emits: ('move', { itemId, fromCol, toCol })
```

Uses CSS `display:flex; overflow-x:auto` columns, drag via HTML5 `draggable` (no extra dep).

---

### 2.7 Cash Session State Machine

```
CLOSED ──open()──► OPEN ──close()──► PENDING_COUNT
                                            │
                              countingAmount entered
                                            │
                                      RECONCILED
                                            │
                              confirm() → CLOSED (archived)
```

**`cashSession` store actions:**
```ts
openSession(openingAmount: number): Promise<void>
addInflow(entry: { category: string; amount: number; note: string }): Promise<void>
addOutflow(entry): Promise<void>
submitCount(countedAmount: number): Promise<void>   // computes variance
confirmClose(): Promise<void>
```

---

### 2.8 Installment Plan Builder

**`InstallmentPlanBuilderView.vue`** — reactive preview table that recalculates on every field change:

```
saleAmount - downPayment = financedAmount
financedAmount × (1 + markupRate/100) = totalPayable
totalPayable / installmentCount = installmentAmount  (+ remainder on last)

Preview table: row per installment with due date + amount
Recalculates live as user types
```

---

### 2.9 Permission Matrix (Admin → Roles)

```
Rows:    Dashboard | Inventory | POS | Repairs | Purchases |
         Installments | Cash | Customers | Reports | Transfers | Admin
Columns: view | create | edit | approve | void | export | view_cost | view_profit | configure

Each cell: checkbox — checked = permission granted for that role
```

Stored as a flat permissions array: `['inventory.view', 'inventory.create', 'reports.export', ...]`

---

### 2.10 Audit Log Viewer

Read-only. No create/edit/delete affordance anywhere in the UI.

**Filters:** actor (user), entity type, entity ID, action (create/update/delete/login/approve/void), date range.

**Table columns:** Timestamp | Actor | Action | Entity Type | Entity ID | Changes (diff summary)

Changes shown as a `before → after` diff of changed fields, collapsed by default with an expand toggle.

---

### 2.11 Customer Khata (Ledger) — No Balance-Edit

The ledger is derived entirely from transaction records. There is **no input field** for balance anywhere in the customer UI — not in the form, not in a modal, not in an admin panel. The running balance column is always a computed display from debit/credit entries.

```
Columns: Date | Description | Reference | Debit | Credit | Balance
```

---

### 2.12 Step-Up Re-Authentication Modal

**`StepUpAuthModal.vue`** — triggered by `useStepUpAuth().requireStepUp(action)`:

```
┌─────────────────────────────────────┐
│ Confirm Identity                    │
│                                     │
│ This action requires re-verification│
│ Action: Cost Adjustment             │
│                                     │
│ Password: [____________]            │
│                                     │
│           [Cancel]  [Verify]        │
└─────────────────────────────────────┘
```

On verify: `POST /api/v1/auth/step-up/` with `{ password, action }`. Returns `{ token: <short-lived OTP> }` which is attached to the subsequent privileged API call as `X-Step-Up-Token`.

---

### 2.13 Barcode Label Print

**`BarcodeLabelsView.vue`** — configurable label fields, preview grid:

```
Fields (checkboxes): Name | SKU | Price | Barcode | QR | Branch | Category

Preview:
┌──────────────────┐
│ Samsung A54      │
│ SKU: SAM-A54-BLK │
│ Rs. 85,000       │
│ ▐▌▌▐▌▌▐ ← barcode│
└──────────────────┘
× 4 per row, print-ready
```

Barcode rendered via `jsbarcode` (no server dep). QR via `qrcode` package.

---

## 3. API Contract (Mock → Real Switchover Plan)

### Base URL
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Auth
```
POST /api/v1/auth/login/          → { token, user }
POST /api/v1/auth/logout/
GET  /api/v1/auth/me/             → { id, username, permissions[], branches[], role }
POST /api/v1/auth/step-up/        → { step_up_token }
POST /api/v1/auth/change-password/
```

### Branches
```
GET  /api/v1/branches/            → [{ id, name, is_default }]
```

### Inventory — Devices (IMEI)
```
GET    /api/v1/inventory/devices/
POST   /api/v1/inventory/devices/
GET    /api/v1/inventory/devices/:id/
PATCH  /api/v1/inventory/devices/:id/
GET    /api/v1/inventory/devices/:id/timeline/
POST   /api/v1/inventory/devices/:id/adjust_cost/
GET    /api/v1/inventory/devices/check_duplicate/?imei=<imei>
```

### Inventory — Accessories
```
GET    /api/v1/inventory/accessories/
POST   /api/v1/inventory/accessories/
PATCH  /api/v1/inventory/accessories/:id/
POST   /api/v1/inventory/accessories/:id/adjust_stock/
GET    /api/v1/inventory/accessories/:id/movements/
GET    /api/v1/inventory/low-stock/
GET    /api/v1/inventory/scan/?q=<barcode|imei>
```

### Sales
```
GET    /api/v1/sales/invoices/
POST   /api/v1/sales/invoices/
GET    /api/v1/sales/invoices/:id/
POST   /api/v1/sales/invoices/:id/finalize/
POST   /api/v1/sales/invoices/:id/void/
POST   /api/v1/sales/invoices/:id/correct/     → creates linked correction record
GET    /api/v1/sales/daily-summary/
```

### Repairs
```
GET    /api/v1/repairs/jobs/
POST   /api/v1/repairs/jobs/
GET    /api/v1/repairs/jobs/:id/
PATCH  /api/v1/repairs/jobs/:id/
POST   /api/v1/repairs/jobs/:id/update_status/
POST   /api/v1/repairs/jobs/:id/deliver/
GET    /api/v1/repairs/board/                  → jobs grouped by stage
```

### Purchases
```
GET    /api/v1/purchases/orders/
POST   /api/v1/purchases/orders/
GET    /api/v1/purchases/orders/:id/
POST   /api/v1/purchases/orders/:id/receive/
POST   /api/v1/purchases/acquisitions/         → used-phone intake
```

### Installments
```
GET    /api/v1/installments/plans/
POST   /api/v1/installments/plans/
GET    /api/v1/installments/plans/:id/
POST   /api/v1/installments/plans/:id/collect/
GET    /api/v1/installments/plans/:id/schedule/
GET    /api/v1/installments/overdue/
GET    /api/v1/installments/aging/
```

### Cash
```
GET    /api/v1/cash/sessions/current/
POST   /api/v1/cash/sessions/open/
POST   /api/v1/cash/sessions/close/
POST   /api/v1/cash/sessions/:id/inflow/
POST   /api/v1/cash/sessions/:id/outflow/
GET    /api/v1/cash/expenses/
POST   /api/v1/cash/expenses/
```

### Customers
```
GET    /api/v1/customers/
POST   /api/v1/customers/
GET    /api/v1/customers/:id/
PATCH  /api/v1/customers/:id/
GET    /api/v1/customers/:id/ledger/
GET    /api/v1/customers/:id/history/
GET    /api/v1/customers/check_duplicate/?name=&phone=
GET    /api/v1/customers/search/?q=
```

### Reports (all GET with date_from / date_to / branch params)
```
GET    /api/v1/reports/sales-summary/
GET    /api/v1/reports/profit-loss/
GET    /api/v1/reports/inventory-valuation/
GET    /api/v1/reports/imei-history/
GET    /api/v1/reports/repairs/
GET    /api/v1/reports/installments/
GET    /api/v1/reports/customer-ledger/
GET    /api/v1/reports/staff-performance/
GET    /api/v1/reports/dead-stock/
GET    /api/v1/reports/cash/
GET    /api/v1/reports/:slug/export/            → CSV blob
```

### Admin
```
GET    /api/v1/admin/users/
POST   /api/v1/admin/users/
PATCH  /api/v1/admin/users/:id/
POST   /api/v1/admin/users/:id/deactivate/
GET    /api/v1/admin/roles/
POST   /api/v1/admin/roles/
PATCH  /api/v1/admin/roles/:id/
GET    /api/v1/admin/audit-log/
```

### Transfers
```
GET    /api/v1/transfers/
POST   /api/v1/transfers/
GET    /api/v1/transfers/:id/
POST   /api/v1/transfers/:id/dispatch/
POST   /api/v1/transfers/:id/receive/
```

---

## 4. Correctness Properties

1. **Money totals never use floating-point arithmetic directly** — all line-item totals, subtotals, taxes, and discounts are computed in PKR integer paise (×100), divided only at display time via `formatMoney()`.
2. **Permission checks are double-enforced** — route guards block navigation AND `PermGate`/`usePermissions` suppress rendering. A permission change mid-session triggers a re-fetch of `/auth/me/`.
3. **Finalized records are immutable** — once `invoice.status` is `finalized`, `paid`, or `returned`, the edit UI is replaced with correction-only flows. This is enforced in `InvoiceDetailView` by `isEditable = computed(() => invoice.value?.status === 'draft')`.
4. **Scanner focus is never stolen** — every non-scanner input in POS carries `data-no-scanner-refocus`. The `handleBodyClick` listener in `ScannerInput` only refocuses when the clicked element lacks that attribute.
5. **Khata ledger has no balance-edit field** — `CustomerDetailView` and `CustomerLedgerView` contain zero `<input>` elements that write to balance. Balance is always derived from ledger entries.
6. **Destructive actions state their effect** — every `confirm()` call for void/return/adjustment/transfer passes a non-null `effect` string. `ConfirmDialog` renders it prominently. A `console.error` warning fires in dev if `effect` is omitted for actions whose `confirmClass` is `btn-danger`.
7. **Mock and real API are structurally identical** — mock handlers return the same JSON shape as the DRF serializer contracts above. Switching `VITE_USE_MOCK` must not require any changes to store actions or view components.
8. **Step-up token is single-use** — `useStepUpAuth` clears the step-up token from memory immediately after the privileged API call resolves, regardless of success or failure.
