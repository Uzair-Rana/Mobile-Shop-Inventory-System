from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('', views.UserViewSet, basename='user')

urlpatterns = [
    path('login/',           views.login_view),
    path('logout/',          views.logout_view),
    path('me/',              views.me_view),
    path('change-password/', views.change_password_view),
    path('step-up/',         views.step_up_view),
]
