from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('expenses', views.ExpenseViewSet, basename='expense')

urlpatterns = router.urls + [
    path('sessions/current/', views.current_session),
    path('sessions/open/',    views.open_session),
    path('sessions/close/',   views.close_session),
    path('sessions/<int:session_id>/inflow/',  views.add_inflow),
    path('sessions/<int:session_id>/outflow/', views.add_outflow),
]
