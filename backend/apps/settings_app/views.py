from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import CompanySettings
from .serializers import CompanySettingsSerializer


@api_view(['GET', 'PUT', 'PATCH'])
def company_settings(request):
    """Get or update the singleton company settings record."""
    obj, _ = CompanySettings.objects.get_or_create(id=1)

    if request.method == 'GET':
        return Response(CompanySettingsSerializer(obj).data)

    partial = (request.method == 'PATCH')
    ser = CompanySettingsSerializer(obj, data=request.data, partial=partial)
    ser.is_valid(raise_exception=True)
    ser.save()
    return Response(ser.data)
