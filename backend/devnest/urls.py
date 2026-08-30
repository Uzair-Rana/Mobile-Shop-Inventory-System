from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include([
        path('auth/',        include('apps.users.urls')),
        path('branches/',    include('apps.branches.urls')),
        path('inventory/',   include('apps.inventory.urls')),
        path('sales/',       include('apps.sales.urls')),
        path('repairs/',     include('apps.repairs.urls')),
        path('installments/',include('apps.installments.urls')),
        path('purchases/',   include('apps.purchases.urls')),
        path('customers/',   include('apps.customers.urls')),
        path('suppliers/',   include('apps.suppliers.urls')),
        path('transfers/',   include('apps.transfers.urls')),
        path('cash/',        include('apps.cash.urls')),
        path('reports/',     include('apps.reports.urls')),
        path('settings/',    include('apps.settings_app.urls')),
        path('admin/',       include('apps.audit.urls')),
    ])),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
