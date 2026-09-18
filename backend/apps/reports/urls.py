from django.urls import path
from . import views

urlpatterns = [
    path('sales-summary/',        views.sales_summary),
    path('profit-loss/',          views.profit_loss),
    path('inventory-valuation/',  views.inventory_valuation),
    path('imei-history/',         views.imei_history),
    path('repairs/',              views.repairs_report),
    path('installments/',         views.installments_report),
    path('customer-ledger/',      views.customer_ledger),
    path('staff-performance/',    views.staff_performance),
    path('dead-stock/',           views.dead_stock),
    path('cash/',                 views.cash_report),
    path('<slug:slug>/export/',   views.export_report),
]
