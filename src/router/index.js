import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// ── Lazy-loaded route components ───────────────────────────────────────────────
const LoginView = () => import('@/views/auth/LoginView.vue')
const DashboardView = () => import('@/views/dashboard/DashboardView.vue')

// POS
const PosView = () => import('@/views/pos/PosView.vue')

// Inventory
const InventoryLayout = () => import('@/views/inventory/InventoryLayout.vue')
const ProductListView = () => import('@/views/inventory/ProductListView.vue')
const ProductDetailView = () => import('@/views/inventory/ProductDetailView.vue')
const UnitListView = () => import('@/views/inventory/UnitListView.vue')
const AccessoryListView = () => import('@/views/inventory/AccessoryListView.vue')

// Sales
const SalesLayout = () => import('@/views/sales/SalesLayout.vue')
const InvoiceListView = () => import('@/views/sales/InvoiceListView.vue')
const InvoiceDetailView = () => import('@/views/sales/InvoiceDetailView.vue')

// Repairs
const RepairsLayout = () => import('@/views/repairs/RepairsLayout.vue')
const RepairListView = () => import('@/views/repairs/RepairListView.vue')
const RepairDetailView = () => import('@/views/repairs/RepairDetailView.vue')
const RepairNewView = () => import('@/views/repairs/RepairNewView.vue')

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

// Installments
const InstallmentListView = () => import('@/views/installments/InstallmentListView.vue')
const InstallmentDetailView = () => import('@/views/installments/InstallmentDetailView.vue')

// Reports
const ReportsLayout = () => import('@/views/reports/ReportsLayout.vue')
const SalesReportView = () => import('@/views/reports/SalesReportView.vue')
const ProfitReportView = () => import('@/views/reports/ProfitReportView.vue')
const InventoryReportView = () => import('@/views/reports/InventoryReportView.vue')
const RepairReportView = () => import('@/views/reports/RepairReportView.vue')
const InstallmentReportView = () => import('@/views/reports/InstallmentReportView.vue')

// Settings
const SettingsLayout = () => import('@/views/settings/SettingsLayout.vue')
const CompanySettingsView = () => import('@/views/settings/CompanySettingsView.vue')
const UsersSettingsView = () => import('@/views/settings/UsersSettingsView.vue')
const RolesSettingsView = () => import('@/views/settings/RolesSettingsView.vue')
const TaxSettingsView = () => import('@/views/settings/TaxSettingsView.vue')

// ── Route definitions ──────────────────────────────────────────────────────────
const routes = [
    {
        path: '/login',
        name: 'login',
        component: LoginView,
        meta: { public: true },
    },
    {
        path: '/',
        redirect: '/dashboard',
        meta: { requiresAuth: true },
    },
    {
        path: '/dashboard',
        name: 'dashboard',
        component: DashboardView,
        meta: { requiresAuth: true, title: 'Dashboard' },
    },
    {
        path: '/pos',
        name: 'pos',
        component: PosView,
        meta: { requiresAuth: true, title: 'Point of Sale', fullscreen: true },
    },
    {
        path: '/inventory',
        component: InventoryLayout,
        meta: { requiresAuth: true },
        children: [
            { path: '', redirect: 'products' },
            { path: 'products', name: 'inventory.products', component: ProductListView, meta: { title: 'Products' } },
            { path: 'products/:id', name: 'inventory.product', component: ProductDetailView, meta: { title: 'Product' } },
            { path: 'units', name: 'inventory.units', component: UnitListView, meta: { title: 'IMEI / Units' } },
            { path: 'accessories', name: 'inventory.accessories', component: AccessoryListView, meta: { title: 'Accessories' } },
        ],
    },
    {
        path: '/sales',
        component: SalesLayout,
        meta: { requiresAuth: true },
        children: [
            { path: '', redirect: 'invoices' },
            { path: 'invoices', name: 'sales.invoices', component: InvoiceListView, meta: { title: 'Invoices' } },
            { path: 'invoices/:id', name: 'sales.invoice', component: InvoiceDetailView, meta: { title: 'Invoice' } },
        ],
    },
    {
        path: '/repairs',
        component: RepairsLayout,
        meta: { requiresAuth: true },
        children: [
            { path: '', redirect: 'jobs' },
            { path: 'jobs', name: 'repairs.list', component: RepairListView, meta: { title: 'Repair Jobs' } },
            { path: 'jobs/new', name: 'repairs.new', component: RepairNewView, meta: { title: 'New Repair Job' } },
            { path: 'jobs/:id', name: 'repairs.detail', component: RepairDetailView, meta: { title: 'Repair Job' } },
        ],
    },
    {
        path: '/customers',
        meta: { requiresAuth: true },
        children: [
            { path: '', name: 'customers.list', component: CustomerListView, meta: { title: 'Customers' } },
            { path: ':id', name: 'customers.detail', component: CustomerDetailView, meta: { title: 'Customer' } },
        ],
    },
    {
        path: '/suppliers',
        meta: { requiresAuth: true },
        children: [
            { path: '', name: 'suppliers.list', component: SupplierListView, meta: { title: 'Suppliers' } },
            { path: ':id', name: 'suppliers.detail', component: SupplierDetailView, meta: { title: 'Supplier' } },
        ],
    },
    {
        path: '/purchases',
        component: PurchasesLayout,
        meta: { requiresAuth: true },
        children: [
            { path: '', redirect: 'orders' },
            { path: 'orders', name: 'purchases.list', component: PurchaseListView, meta: { title: 'Purchase Orders' } },
            { path: 'orders/new', name: 'purchases.new', component: PurchaseNewView, meta: { title: 'New PO' } },
            { path: 'orders/:id', name: 'purchases.detail', component: PurchaseDetailView, meta: { title: 'Purchase Order' } },
        ],
    },
    {
        path: '/installments',
        meta: { requiresAuth: true },
        children: [
            { path: '', name: 'installments.list', component: InstallmentListView, meta: { title: 'Installment Plans' } },
            { path: ':id', name: 'installments.detail', component: InstallmentDetailView, meta: { title: 'Installment Plan' } },
        ],
    },
    {
        path: '/reports',
        component: ReportsLayout,
        meta: { requiresAuth: true, requiresPermission: 'view_reports' },
        children: [
            { path: '', redirect: 'sales' },
            { path: 'sales', name: 'reports.sales', component: SalesReportView, meta: { title: 'Sales Report' } },
            { path: 'profit', name: 'reports.profit', component: ProfitReportView, meta: { title: 'Profit & Loss', requiresPermission: 'view_profit' } },
            { path: 'inventory', name: 'reports.inventory', component: InventoryReportView, meta: { title: 'Inventory Valuation' } },
            { path: 'repairs', name: 'reports.repairs', component: RepairReportView, meta: { title: 'Repairs Report' } },
            { path: 'installments', name: 'reports.installments', component: InstallmentReportView, meta: { title: 'Installments Report' } },
        ],
    },
    {
        path: '/settings',
        component: SettingsLayout,
        meta: { requiresAuth: true },
        children: [
            { path: '', redirect: 'company' },
            { path: 'company', name: 'settings.company', component: CompanySettingsView, meta: { title: 'Company' } },
            { path: 'users', name: 'settings.users', component: UsersSettingsView, meta: { title: 'Users', requiresPermission: 'manage_users' } },
            { path: 'roles', name: 'settings.roles', component: RolesSettingsView, meta: { title: 'Roles', requiresPermission: 'manage_users' } },
            { path: 'tax', name: 'settings.tax', component: TaxSettingsView, meta: { title: 'Tax' } },
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
router.beforeEach(async (to, _from, next) => {
    const auth = useAuthStore()

    // Init auth from stored token on first load
    if (!auth.user && auth.token) {
        await auth.init()
    }

    if (to.meta.public) return next()

    if (to.meta.requiresAuth && !auth.isLoggedIn) {
        return next({ name: 'login', query: { redirect: to.fullPath } })
    }

    if (to.meta.requiresPermission && !auth.hasPermission(to.meta.requiresPermission)) {
        return next({ name: 'dashboard' })
    }

    // Update document title
    document.title = to.meta.title ? `${to.meta.title} — DEVNEST` : 'DEVNEST'

    next()
})

export default router
