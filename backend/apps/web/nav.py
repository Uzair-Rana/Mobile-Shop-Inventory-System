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
        'description': 'Procurement, purchases, suppliers & transfers',
        'items': [
            {'label': 'Procurement', 'url_name': 'web:procurement_list', 'icon': 'truck',   'desc': 'Add stock via supplier procurement'},
            {'label': 'Purchases', 'url_name': 'web:purchases', 'icon': 'receipt',  'desc': 'Purchase orders'},
            {'label': 'Suppliers', 'url_name': 'web:suppliers', 'icon': 'building', 'desc': 'Supplier directory'},
            {'label': 'Transfers', 'url_name': 'web:transfers', 'icon': 'transfer', 'desc': 'Stock transfers'},
        ],
    },
    'finance': {
        'key': 'finance', 'label': 'Finance', 'icon': 'cash', 'url_name': 'web:finance',
        'description': 'Cash sessions & expenses',
        'items': [
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
    {'label': 'Settings',      'url_name': 'web:settings',  'icon': 'cog',     'match': 'settings'},
]
