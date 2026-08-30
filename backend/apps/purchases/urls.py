from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('orders',       views.PurchaseOrderViewSet, basename='purchase-order')
router.register('acquisitions', views.AcquisitionViewSet,   basename='acquisition')

urlpatterns = router.urls
