import secrets
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.core.cache import cache
from .models import User, Role
from .serializers import (
    UserSerializer, UserCreateSerializer,
    LoginSerializer, ChangePasswordSerializer,
    RoleSerializer,
)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    ser = LoginSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    user = authenticate(
        username=ser.validated_data['username'],
        password=ser.validated_data['password'],
    )
    if not user or not user.is_active:
        return Response({'detail': 'Invalid credentials.'}, status=400)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key, 'user': UserSerializer(user).data})


@api_view(['POST'])
def logout_view(request):
    request.user.auth_token.delete()
    return Response({'detail': 'Logged out.'})


@api_view(['GET'])
def me_view(request):
    return Response(UserSerializer(request.user).data)


@api_view(['POST'])
def change_password_view(request):
    ser = ChangePasswordSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    if not request.user.check_password(ser.validated_data['old_password']):
        return Response({'detail': 'Old password incorrect.'}, status=400)
    request.user.set_password(ser.validated_data['new_password'])
    request.user.save()
    return Response({'detail': 'Password changed.'})


@api_view(['POST'])
def step_up_view(request):
    """Verify password and return a short-lived single-use step-up token."""
    password = request.data.get('password', '')
    action_name = request.data.get('action', 'unknown')
    if not request.user.check_password(password):
        return Response({'detail': 'Invalid password.'}, status=400)
    # Generate a random token, store in cache for 5 minutes (single-use)
    token = secrets.token_urlsafe(32)
    cache.set(f'stepup:{token}', {'user_id': request.user.id, 'action': action_name}, timeout=300)
    return Response({'step_up_token': token})


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'detail': 'User deactivated.'})


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.prefetch_related('permissions').all()
    serializer_class = RoleSerializer
