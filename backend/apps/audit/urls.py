from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users.views import UserViewSet, RoleViewSet
from . import views

# Admin-scoped router: /api/v1/admin/users/, /api/v1/admin/roles/
router = DefaultRouter()
router.register('users', UserViewSet, basename='admin-user')
router.register('roles', RoleViewSet, basename='admin-role')

urlpatterns = router.urls + [
    path('audit-log/', views.AuditLogListView.as_view()),
]
