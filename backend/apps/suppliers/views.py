from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from .models import Supplier, SupplierLedger
from .serializers import SupplierSerializer, SupplierLedgerSerializer


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all().order_by('name')
    serializer_class = SupplierSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name', 'company', 'phone']

    @action(detail=True, methods=['get'])
    def ledger(self, request, pk=None):
        supplier = self.get_object()
        entries = supplier.ledger.all()
        return Response(SupplierLedgerSerializer(entries, many=True).data)
