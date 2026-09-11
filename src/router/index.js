import { createRouter, createWebHistory } from 'vue-router'

// ── Lazy-loaded route components ───────────────────────────────────────────────
const DashboardView = () => import('@/views/dashboard/DashboardView.vue')

// POS
const PosView = () => import('@/views/pos/PosView.vue')

// Inventory
const InventoryLayout = () => import('@/views/inventory/InventoryLayout.vue')
const ProductListView = () => import('@/views/inventory/ProductListView.vue')
const ProductDetailView = () => import('@/views/inventory/ProductDetailView.vue')
const UnitListView = () => import('@/views/inventory/UnitListView.vue')
const AccessoryListView = () => import('@/views/inventory/AccessoryListView.vue')
const DeviceListView = () => import('@/views/inventory/DeviceListView.vue')
const DeviceDetailView = () => import('@/views/inventory/DeviceDetailView.vue')
const DeviceAddView = () => import('@/views/inventory/DeviceAddView.vue')
const BarcodeLabelsView = () => import('@/views/inventory/BarcodeLabelsView.vue')

// Sales
const SalesLayout = () => import('@/views/sales/SalesLayout.vue')
const InvoiceListView = () => import('@/views/sales/InvoiceListView.vue')
const InvoiceDetailView = () => import('@/views/sales/InvoiceDetailView.vue')
const InvoiceCorrectionView = () => import('@/views/sales/InvoiceCorrectionView.vue')

// Repairs
const RepairsLayout = () => import('@/views/repairs/RepairsLayout.vue')
const RepairListView = () => import('@/views/repairs/RepairListView.vue')
const RepairDetailView = () => import('@/views/repairs/RepairDetailView.vue')
const RepairNewView = () => import('@/views/repairs/RepairNewView.vue')
const RepairBoardView = () => import('@/views/repairs/RepairBoardView.vue')

// Customers
const CustomerListView = () => import('@/views/customers/CustomerListView.vue')
const CustomerDetailView = () => import('@/views/customers/CustomerDetailView.vue')

// Suppliers
const SupplierListView = () => import('@/views/suppliers/SupplierListView.vue')
const SupplierDetailView = () => import('@/views/suppliers/SupplierDetailView.vue')

// Purchases
const PurchasesLayout = () => import('@/views/purchases/PurchasesLayout.vue')
const PurchaseListView = () => import('@/views/purchases/PurchaseListView.vue')
const PurchaseDetailView = () => import('@/views/purchases/PurchaseDetailView.vue')
const PurchaseNewView = () => import('@/views/purchases/PurchaseNewView.vue')
const AcquisitionView = () => import('@/views/purchases/AcquisitionView.vue')

// Installments
const InstallmentListView = () => import('@/views/installments/InstallmentListView.vue')
const InstallmentDetailView = () => import('@/views/installments/InstallmentDetailView.vue')
const InstallmentPlanBuilderView = () => import('@/views/installments/InstallmentPlanBuilderView.vue')
const OverdueAgingView = () => import('@/views/installments/OverdueAgingView.vue')

// Cash
const CashSessionView = () => import('@/views/cash/CashSessionView.vue')
const ExpenseListView = () => import('@/views/cash/ExpenseListView.vue')

// Transfers
const TransferListView = () => import('@/views/transfers/TransferListView.vue')
const TransferDetailView = () => import('@/views/transfers/TransferDetailView.vue')

// Reports
const ReportsLayout = () => import('@/views/reports/ReportsLayout.vue')
const SalesReportView = () => import('@/views/reports/SalesReportView.vue')
const ProfitReportView = () => import('@/views/reports/ProfitReportView.vue')
const InventoryReportView = () => import('@/views/reports/InventoryReportView.vue')
const RepairReportView = () => import('@/views/reports/RepairReportView.vue')
const InstallmentReportView = () => import('@/views/reports/InstallmentReportView.vue')
const ImeiHistoryView = () => import('@/views/reports/ImeiHistoryView.vue')
const StaffReportView = () => import('@/views/reports/StaffReportView.vue')
const DeadStockView = () => import('@/views/reports/DeadStockView.vue')
const CashReportView = () => import('@/views/reports/CashReportView.vue')
const CustomerLedgerView = () => import('@/views/reports/CustomerLedgerView.vue')

// Settings
const SettingsLayout = () => import('@/views/settings/SettingsLayout.vue')
const CompanySettingsView = () => import('@/views/settings/CompanySettingsView.vue')
const UsersSettingsView = () => import('@/views/settings/UsersSettingsView.vue')
const RolesSettingsView = () => import('@/views/settings/RolesSettingsView.vue')
const TaxSettingsView = () => import('@/views/settings/TaxSettingsView.vue')
const AuditLogView = () => import('@/views/settings/AuditLogView.vue')

// ── Route definitions ──────────────────────────────────────────────────────────
const routes = [
    {
        path: '/',
        redirect: '/dashboard',
    },
    {
        path: '/dashboard',
        name: 'dashboard',
        component: DashboardView,
        meta: { title: 'Dashboard' },
    },
    {
        path: '/pos',
        name: 'pos',
        component: PosView,
        meta: { title: 'Point of Sale', fullscreen: true },
    },
    // Cash
    {
        path: '/cash',
        meta: {},
        children: [
            { path: '', name: 'cash.session', component: CashSessionView, meta: { title: 'Cash Session' } },
            { path: 'expenses', name: 'cash.expenses', component: ExpenseListView, meta: { title: 'Expenses' } },
        ],
    },
    // Transfers
    {
        path: '/transfers',
        meta: {},
        children: [
            { path: '', name: 'transfers.list', component: TransferListView, meta: { title: 'Transfers' } },
            { path: ':id', name: 'transfers.detail', component: TransferDetailView, meta: { title: 'Transfer' } },
        ],
    },
    // Inventory
    {
        path: '/inventory',
        component: InventoryLayout,
        meta: {},
        children: [
            { path: '', redirect: 'products' },
            { path: 'products', name: 'inventory.products', component: ProductListView, meta: { title: 'Products' } },
            { path: 'products/:id', name: 'inventory.product', component: ProductDetailView, meta: { title: 'Product' } },
            { path: 'units', name: 'inventory.units', component: UnitListView, meta: { title: 'IMEI / Units' } },
            { path: 'accessories', name: 'inventory.accessories', component: AccessoryListView, meta: { title: 'Accessories' } },
            { path: 'devices', name: 'inventory.devices', component: DeviceListView, meta: { title: 'Devices' } },
            { path: 'devices/new', name: 'inventory.devices.new', component: DeviceAddView, meta: { title: 'Add Device' } },
            { path: 'devices/:id', name: 'inventory.devices.detail', component: DeviceDetailView, meta: { title: 'Device' } },
            { path: 'labels', name: 'inventory.labels', component: BarcodeLabelsView, meta: { title: 'Barcode Labels' } },
        ],
    },
    // Sales
    {
        path: '/sales',
        component: SalesLayout,
        meta: {},
        children: [
            { path: '', redirect: 'invoices' },
            { path: 'invoices', name: 'sales.invoices', component: InvoiceListView, meta: { title: 'Invoices' } },
            { path: 'invoices/:id', name: 'sales.invoice', component: InvoiceDetailView, meta: { title: 'Invoice' } },
            { path: 'invoices/:id/correct', name: 'sales.invoice.correct', component: InvoiceCorrectionView, meta: { title: 'Invoice Correction' } },
        ],
    },
    // Repairs
    {
        path: '/repairs',
        component: RepairsLayout,
        meta: {},
        children: [
            { path: '', redirect: 'jobs' },
            { path: 'board', name: 'repairs.board', component: RepairBoardView, meta: { title: 'Repair Board' } },
            { path: 'jobs', name: 'repairs.list', component: RepairListView, meta: { title: 'Repair Jobs' } },
            { path: 'jobs/new', name: 'repairs.new', component: RepairNewView, meta: { title: 'New Repair Job' } },
            { path: 'jobs/:id', name: 'repairs.detail', component: RepairDetailView, meta: { title: 'Repair Job' } },
        ],
    },
    // Customers
    {
        path: '/customers',
        meta: {},
        children: [
            { path: '', name: 'customers.list', component: CustomerListView, meta: { title: 'Customers' } },
            { path: ':id', name: 'customers.detail', component: CustomerDetailView, meta: { title: 'Customer' } },
        ],
    },
    // Suppliers
    {
        path: '/suppliers',
        meta: {},
        children: [
            { path: '', name: 'suppliers.list', component: SupplierListView, meta: { title: 'Suppliers' } },
            { path: ':id', name: 'suppliers.detail', component: SupplierDetailView, meta: { title: 'Supplier' } },
        ],
    },
    // Purchases
    {
        path: '/purchases',
        component: PurchasesLayout,
        meta: {},
        children: [
            { path: '', redirect: 'orders' },
            { path: 'orders', name: 'purchases.list', component: PurchaseListView, meta: { title: 'Purchase Orders' } },
            { path: 'orders/new', name: 'purchases.new', component: PurchaseNewView, meta: { title: 'New PO' } },
            { path: 'orders/:id', name: 'purchases.detail', component: PurchaseDetailView, meta: { title: 'Purchase Order' } },
            { path: 'acquisitions/new', name: 'purchases.acquisition', component: AcquisitionView, meta: { title: 'Used Phone Acquisition' } },
        ],
    },
    // Installments
    {
        path: '/installments',
        meta: {},
        children: [
            { path: '', name: 'installments.list', component: InstallmentListView, meta: { title: 'Installment Plans' } },
            { path: 'new', name: 'installments.new', component: InstallmentPlanBuilderView, meta: { title: 'New Installment Plan' } },
            { path: 'aging', name: 'installments.aging', component: OverdueAgingView, meta: { title: 'Overdue Aging' } },
            { path: ':id', name: 'installments.detail', component: InstallmentDetailView, meta: { title: 'Installment Plan' } },
        ],
    },
    // Reports
    {
        path: '/reports',
        component: ReportsLayout,
        meta: { requiresPermission: 'view_reports' },
        children: [
            { path: '', redirect: 'sales' },
            { path: 'sales', name: 'reports.sales', component: SalesReportView, meta: { title: 'Sales Report' } },
            { path: 'profit', name: 'reports.profit', component: ProfitReportView, meta: { title: 'Profit & Loss', requiresPermission: 'view_profit' } },
            { path: 'inventory', name: 'reports.inventory', component: InventoryReportView, meta: { title: 'Inventory Valuation' } },
            { path: 'repairs', name: 'reports.repairs', component: RepairReportView, meta: { title: 'Repairs Report' } },
            { path: 'installments', name: 'reports.installments', component: InstallmentReportView, meta: { title: 'Installments Report' } },
            { path: 'imei-history', name: 'reports.imei', component: ImeiHistoryView, meta: { title: 'IMEI History' } },
            { path: 'staff', name: 'reports.staff', component: StaffReportView, meta: { title: 'Staff Report', requiresPermission: 'view_reports' } },
            { path: 'dead-stock', name: 'reports.deadstock', component: DeadStockView, meta: { title: 'Dead Stock' } },
            { path: 'cash', name: 'reports.cash', component: CashReportView, meta: { title: 'Cash Report' } },
            { path: 'customer-ledger', name: 'reports.ledger', component: CustomerLedgerView, meta: { title: 'Customer Ledger' } },
        ],
    },
    // Settings
    {
        path: '/settings',
        component: SettingsLayout,
        meta: {},
        children: [
            { path: '', redirect: 'company' },
            { path: 'company', name: 'settings.company', component: CompanySettingsView, meta: { title: 'Company' } },
            { path: 'users', name: 'settings.users', component: UsersSettingsView, meta: { title: 'Users', requiresPermission: 'manage_users' } },
            { path: 'roles', name: 'settings.roles', component: RolesSettingsView, meta: { title: 'Roles', requiresPermission: 'manage_users' } },
            { path: 'tax', name: 'settings.tax', component: TaxSettingsView, meta: { title: 'Tax' } },
            { path: 'audit', name: 'settings.audit', component: AuditLogView, meta: { title: 'Audit Log' } },
        ],
    },
    // 404
    { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
]

// ── Router instance ────────────────────────────────────────────────────────────
export const router = createRouter({
    history: createWebHistory(),
    routes,
    scrollBehavior: () => ({ top: 0 }),
})

// ── Navigation guard ───────────────────────────────────────────────────────────
import { useAuthStore } from '@/stores/auth'

router.beforeEach((to, _from, next) => {
    document.title = to.meta.title ? `${to.meta.title} — My Phone ERP` : 'My Phone ERP'
    next()
})

export default router
