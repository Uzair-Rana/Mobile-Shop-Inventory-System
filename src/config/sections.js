/**
 * Navigation information architecture.
 *
 * SECTIONS = the "major tabs" that open a hub page in the body listing their
 * sub-options as cards. TABS = the full ordered list shown in the sidebar
 * (direct links like Dashboard/POS + the section hubs + Reports/Settings).
 */

export const SECTIONS = [
    {
        key: 'stock', label: 'Stock', icon: 'box', to: '/stock',
        description: 'Inventory, devices, accessories & labels',
        items: [
            { label: 'IMEI Devices',   to: '/inventory/devices',     icon: 'device', desc: 'Serialized phone inventory' },
            { label: 'Accessories',    to: '/inventory/accessories', icon: 'plug',   desc: 'Non-serialized stock items' },
            { label: 'Products',       to: '/inventory/products',    icon: 'box',    desc: 'Full product catalog' },
            { label: 'Barcode Labels', to: '/inventory/labels',      icon: 'tag',    desc: 'Print price / IMEI labels' },
        ],
    },
    {
        key: 'selling', label: 'Sales', icon: 'receipt', to: '/selling',
        description: 'Invoices & customers',
        items: [
            { label: 'Invoices',  to: '/sales/invoices', icon: 'receipt', desc: 'Sales invoices & history' },
            { label: 'Customers', to: '/customers',      icon: 'users',   desc: 'Customer directory' },
        ],
    },
    {
        key: 'workshop', label: 'Repairs', icon: 'wrench', to: '/workshop',
        description: 'Repair board & job tickets',
        items: [
            { label: 'Repair Board', to: '/repairs/board', icon: 'wrench', desc: 'Live board of active jobs' },
            { label: 'Repair Jobs',  to: '/repairs/jobs',  icon: 'wrench', desc: 'All repair tickets' },
        ],
    },
    {
        key: 'procurement', label: 'Procurement', icon: 'truck', to: '/procurement',
        description: 'Purchases, suppliers & transfers',
        items: [
            { label: 'Purchases', to: '/purchases/orders', icon: 'truck',    desc: 'Purchase orders' },
            { label: 'Suppliers', to: '/suppliers',        icon: 'building', desc: 'Supplier directory' },
            { label: 'Transfers', to: '/transfers',        icon: 'transfer', desc: 'Stock transfers' },
        ],
    },
    {
        key: 'finance', label: 'Finance', icon: 'cash', to: '/finance',
        description: 'Cash sessions & expenses',
        items: [
            { label: 'Cash Session', to: '/cash',          icon: 'cash',    desc: 'Open / close the drawer' },
            { label: 'Expenses',     to: '/cash/expenses', icon: 'expense', desc: 'Record & approve expenses' },
        ],
    },
]

export const TABS = [
    { label: 'Dashboard',     to: '/dashboard', icon: 'home' },
    { label: 'Point of Sale', to: '/pos',       icon: 'pos', accent: true },
    { label: 'Stock',         to: '/stock',     icon: 'box' },
    { label: 'Sales',         to: '/selling',   icon: 'receipt' },
    { label: 'Repairs',       to: '/workshop',  icon: 'wrench' },
    { label: 'Procurement',   to: '/procurement', icon: 'truck' },
    { label: 'Finance',       to: '/finance',   icon: 'cash' },
    { label: 'Reports',       to: '/reports',   icon: 'chart' },
    { label: 'Settings',      to: '/settings',  icon: 'cog' },
]

/** All route prefixes that belong to a given tab (for active-state matching). */
export function tabMatchPrefixes(tab) {
    const section = SECTIONS.find(s => s.to === tab.to)
    if (!section) return [tab.to]
    return [section.to, ...section.items.map(i => i.to)]
}
