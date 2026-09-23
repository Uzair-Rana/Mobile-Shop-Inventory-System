"""
Navigation information architecture for the Django-rendered frontend.
Mirrors the previous Vue nav: major tabs → each opens a hub of options.
"""

SECTIONS = {
    'stock': {
        'key': 'stock', 'label': 'Stock', 'icon': 'box', 'url_name': 'web:stock',
        'description': 'Inventory, devices, accessories & spare parts',
        'items': [
            {'label': 'IMEI Devices',   'url_name': 'web:devices',      'icon': 'device', 'desc': 'Serialized phone inventory'},
            {'label': 'Accessories',    'url_name': 'web:accessories',  'icon': 'plug',   'desc': 'Non-serialized stock items'},
            {'label': 'Spare Parts',    'url_name': 'web:spare_parts',  'icon': 'wrench', 'desc': 'Display, battery, charging, body, camera parts'},
            {'label': 'Products',       'url_name': 'web:products',     'icon': 'box',    'desc': 'Full product catalog'},
            {'label': 'Barcode Labels', 'url_name': 'web:labels',       'icon': 'tag',    'desc': 'Print price / IMEI labels'},
            {'label': 'Low Stock Alerts', 'url_name': 'web:low_stock',  'icon': 'alert',  'desc': 'Items at or below their alert level', 'badge': 'low_stock_count'},
        ],
    },
    'selling': {
        'key': 'selling', 'label': 'Sales', 'icon': 'receipt', 'url_name': 'web:selling',
        'description': 'Invoices & customers',
        'items': [
            {'label': 'Invoices',  'url_name': 'web:invoices',  'icon': 'receipt', 'desc': 'Sales invoices & history'},
            {'label': 'Customers', 'url_name': 'web:customers', 'icon': 'users',   'desc': 'Customer directory'},
        ],
    },
    'workshop': {
        'key': 'workshop', 'label': 'Repairs', 'icon': 'wrench', 'url_name': 'web:workshop',
        'description': 'Repair board & job tickets',
        'items': [
            {'label': 'Repair Jobs', 'url_name': 'web:repairs', 'icon': 'wrench', 'desc': 'All repair tickets'},
        ],
    },
    'procurement': {
        'key': 'procurement', 'label': 'Procurement', 'icon': 'truck', 'url_name': 'web:procurement',
        'description': 'Purchases, suppliers & sending stock out',
        'items': [
            {'label': 'Purchases', 'url_name': 'web:procurement_list', 'icon': 'truck', 'desc': 'Buy phones, accessories & parts from a seller — stock updates automatically'},
            {'label': 'Suppliers', 'url_name': 'web:suppliers', 'icon': 'building', 'desc': 'Supplier directory'},
            {'label': 'Send Stock Out', 'url_name': 'web:transfers', 'icon': 'transfer', 'desc': 'Send goods to another shop / person — stock is deducted'},
        ],
    },
    'finance': {
        'key': 'finance', 'label': 'Finance', 'icon': 'cash', 'url_name': 'web:finance',
        'description': 'Profit & loss, cash & expenses',
        'items': [
            {'label': 'Profit & Loss', 'url_name': 'web:profit', 'icon': 'cash', 'desc': 'Real profit from sales & repairs, minus expenses'},
            {'label': 'Expenses', 'url_name': 'web:expenses', 'icon': 'expense', 'desc': 'Record & approve expenses'},
        ],
    },
}

# Ordered top-level tabs shown in the sidebar.
TABS = [
    {'label': 'Dashboard',     'url_name': 'web:dashboard', 'icon': 'home',    'match': 'dashboard'},
    {'label': 'Point of Sale', 'url_name': 'web:pos',       'icon': 'pos',     'match': 'pos', 'accent': True},
    {'label': 'Stock',         'url_name': 'web:stock',     'icon': 'box',     'match': 'stock'},
    {'label': 'Sales',         'url_name': 'web:selling',   'icon': 'receipt', 'match': 'selling'},
    {'label': 'Repairs',       'url_name': 'web:workshop',  'icon': 'wrench',  'match': 'workshop'},
    {'label': 'Procurement',   'url_name': 'web:procurement', 'icon': 'truck', 'match': 'procurement'},
    {'label': 'Finance',       'url_name': 'web:finance',   'icon': 'cash',    'match': 'finance'},
    {'label': 'Low Stock',     'url_name': 'web:low_stock', 'icon': 'alert',   'match': 'low_stock', 'badge': 'low_stock_count'},
    # "Settings" is the shop-owner page (backup & restore); the technical page
    # behind the access key is "Developer Options".
    {'label': 'Settings',         'url_name': 'web:backup',   'icon': 'backup', 'match': 'backup'},
    {'label': 'Developer Options', 'url_name': 'web:settings', 'icon': 'cog',   'match': 'settings'},
]
