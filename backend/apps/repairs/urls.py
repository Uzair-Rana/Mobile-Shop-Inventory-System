from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('jobs', views.RepairJobViewSet, basename='repair-job')

urlpatterns = router.urls
