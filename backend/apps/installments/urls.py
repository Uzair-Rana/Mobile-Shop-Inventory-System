from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('plans', views.InstallmentPlanViewSet, basename='installment-plan')

urlpatterns = router.urls + [
    path('overdue/', views.overdue_plans),
    path('aging/',   views.aging_view),
]
