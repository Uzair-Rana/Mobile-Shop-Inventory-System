from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .export_views import export_products_excel

router = DefaultRouter()
router.register('products',    views.ProductViewSet,  basename='product')
router.register('units',       views.UnitViewSet,     basename='unit')
router.register('categories',  views.CategoryViewSet, basename='category')
router.register('brands',      views.BrandViewSet,    basename='brand')

urlpatterns = router.urls + [
    path('scan/',          views.scan_lookup),
    path('low-stock/',     views.low_stock_view),
    path('export-excel/',  export_products_excel),

    # Frontend-facing aliases for cleaner URLs
    path('accessories/', views.ProductViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('accessories/<int:pk>/', views.ProductViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'put': 'update'})),
    path('accessories/<int:pk>/adjust_stock/', views.ProductViewSet.as_view({'post': 'adjust_stock'})),
    path('accessories/<int:pk>/movements/',    views.ProductViewSet.as_view({'get': 'movements'})),

    path('devices/', views.UnitViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('devices/by_imei/',        views.UnitViewSet.as_view({'get': 'by_imei'})),
    path('devices/check_duplicate/', views.UnitViewSet.as_view({'get': 'check_duplicate'})),
    path('devices/<int:pk>/',        views.UnitViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'put': 'update'})),
    path('devices/<int:pk>/timeline/',     views.UnitViewSet.as_view({'get': 'timeline'})),
    path('devices/<int:pk>/adjust_cost/',  views.UnitViewSet.as_view({'post': 'adjust_cost'})),
]
