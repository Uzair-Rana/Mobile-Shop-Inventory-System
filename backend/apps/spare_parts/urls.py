from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('parts', views.SparePartViewSet, basename='spare-part')

urlpatterns = router.urls
