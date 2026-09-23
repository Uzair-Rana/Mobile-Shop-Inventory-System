from django.urls import path
from . import views

app_name = 'web'

urlpatterns = [
    # Activation (install key gate)
    path('activate/', views.activate, name='activate'),

    # Auth
    path('login/',  views.login_view,  name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # POS
    path('pos/',          views.pos,          name='pos'),
    path('pos/add/',      views.pos_add,      name='pos_add'),
    path('pos/remove/',   views.pos_remove,   name='pos_remove'),
    path('pos/update/',   views.pos_update,   name='pos_update'),
    path('pos/add-imeis/', views.pos_add_imeis, name='pos_add_imeis'),
    path('pos/clear/',    views.pos_clear,    name='pos_clear'),
    path('pos/checkout/', views.pos_checkout, name='pos_checkout'),

    # Section hubs
    path('stock/',         views.stock,         name='stock'),
    path('sales/',         views.selling,        name='selling'),
    path('workshop/',      views.workshop,       name='workshop'),
    path('procurement/',   views.procurement,    name='procurement'),
    path('finance/',       views.finance,        name='finance'),
    path('settings/',              views.settings_page, name='settings'),
    path('settings/company/',      views.company_save,  name='company_save'),
    path('settings/unlock/',       views.settings_unlock, name='settings_unlock'),
    path('settings/lock/',         views.settings_lock,   name='settings_lock'),
    path('settings/theme/',        views.theme_save,      name='theme_save'),
    path('settings/access-key/',   views.settings_key_save, name='settings_key_save'),
    path('settings/printing/',     views.printing_save,   name='printing_save'),
    path('settings/options/',      views.option_save,     name='option_save'),
    path('backup/',                views.backup_page,     name='backup'),
    path('backup/download/',       views.backup_download, name='backup_download'),
    path('backup/restore/',        views.restore_backup,  name='restore_backup'),
    path('settings/users/<int:pk>/edit/', views.user_edit, name='user_edit'),

    # Stock — Excel export of any stock list (shared on WhatsApp)
    path('stock/<str:kind>/export.xlsx', views.stock_export, name='stock_export'),
    path('stock/<str:kind>/export.svg',  views.stock_export_svg, name='stock_export_svg'),

    # Stock — Devices
    path('stock/devices/',           views.devices,       name='devices'),
    path('stock/devices/add/',       views.device_add,    name='device_add'),
    path('stock/devices/<int:pk>/',  views.device_detail, name='device_detail'),
    path('stock/devices/<int:pk>/update/', views.device_update, name='device_update'),

    # Stock — Accessories
    path('stock/accessories/',       views.accessories,    name='accessories'),
    path('stock/accessories/add/',   views.accessory_add,  name='accessory_add'),

    # Stock — Spare Parts
    path('stock/spare-parts/',            views.spare_parts,       name='spare_parts'),
    path('stock/spare-parts/<int:pk>/',   views.spare_part_detail, name='spare_part_detail'),
    path('stock/spare-parts/<int:pk>/edit/', views.spare_part_edit, name='spare_part_edit'),

    # Stock — Products
    path('stock/products/',            views.products,     name='products'),
    path('stock/products/add/',        views.product_add,  name='product_add'),
    path('stock/products/<int:pk>/edit/', views.product_edit, name='product_edit'),

    # Stub (labels)
    path('stock/labels/',    views.labels, name='labels'),

    # Sales
    path('sales/udhaar/',             views.udhaar,          name='udhaar'),
    path('sales/invoices/',           views.invoices,        name='invoices'),
    path('sales/invoices/<int:pk>/',  views.invoice_detail,  name='invoice_detail'),
    path('sales/invoices/<int:pk>/status/', views.invoice_status_update, name='invoice_status_update'),
    path('sales/invoices/lines/<int:line_id>/return/', views.invoice_line_return, name='invoice_line_return'),
    path('sales/customers/',          views.customers,        name='customers'),
    path('sales/customers/add/',      views.customer_add,     name='customer_add'),
    path('sales/customers/<int:pk>/', views.customer_detail,  name='customer_detail'),

    # Workshop
    path('workshop/repairs/',            views.repairs,       name='repairs'),
    path('workshop/repairs/new/',        views.repair_new,    name='repair_new'),
    path('workshop/repairs/<int:pk>/',        views.repair_detail, name='repair_detail'),
    path('workshop/repairs/<int:pk>/update/', views.repair_update, name='repair_update'),
    path('workshop/repairs/<int:pk>/parts/add/', views.repair_part_add, name='repair_part_add'),
    path('workshop/repairs/parts/<int:part_id>/remove/', views.repair_part_remove, name='repair_part_remove'),

    # Procurement — stock-in entries (auto-updates stock)
    path('procurement/entries/',              views.procurement_list,   name='procurement_list'),
    path('procurement/entries/new/',          views.procurement_add,    name='procurement_add'),
    path('procurement/entries/<int:pk>/',     views.procurement_detail, name='procurement_detail'),
    path('procurement/entries/<int:pk>/edit/',views.procurement_edit,   name='procurement_edit'),
    path('procurement/entries/<int:pk>/delete/', views.procurement_delete, name='procurement_delete'),

    # Procurement — supporting
    path('procurement/purchases/',           views.purchases,        name='purchases'),
    path('procurement/purchases/<int:pk>/',  views.purchase_detail,  name='purchase_detail'),
    path('procurement/suppliers/',           views.suppliers,         name='suppliers'),
    path('procurement/suppliers/add/',           views.supplier_add,    name='supplier_add'),
    path('procurement/suppliers/<int:pk>/',      views.supplier_detail, name='supplier_detail'),
    path('procurement/suppliers/<int:pk>/edit/', views.supplier_edit,   name='supplier_edit'),

    # Send stock out (to another shop / person) — deducts stock
    path('procurement/send-out/',                 views.transfers,       name='transfers'),
    path('procurement/send-out/new/',             views.transfer_add,    name='transfer_add'),
    path('procurement/send-out/<int:pk>/',        views.transfer_detail, name='transfer_detail'),
    path('procurement/send-out/<int:pk>/cancel/', views.transfer_cancel, name='transfer_cancel'),

    # Finance
    path('finance/profit/',       views.profit,      name='profit'),
    path('finance/expenses/',     views.expenses,    name='expenses'),
    path('finance/expenses/add/', views.expense_add, name='expense_add'),
]
