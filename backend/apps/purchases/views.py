from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import PurchaseOrder, PurchaseOrderLine, Acquisition
from .serializers import (
    PurchaseOrderSerializer, PurchaseOrderCreateSerializer,
    AcquisitionSerializer,
)


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.select_related('supplier', 'branch').prefetch_related('lines').all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'branch', 'supplier']
    search_fields = ['order_number', 'supplier__name']
    ordering_fields = ['created_at', 'grand_total', 'expected_date']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return PurchaseOrderCreateSerializer
        return PurchaseOrderSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        branch_id = self.request.headers.get('X-Branch-ID')
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        """Mark order as received and optionally update qty_received per line."""
        order = self.get_object()
        if order.status == 'received':
            return Response({'detail': 'Order already received.'}, status=status.HTTP_400_BAD_REQUEST)

        lines_data = request.data.get('lines', [])  # [{'line_id': x, 'qty_received': y}]
        all_received = True

        for ld in lines_data:
            try:
                line = order.lines.get(id=ld['line_id'])
                line.qty_received = ld.get('qty_received', line.qty_ordered)
                line.save()
                if line.qty_received < line.qty_ordered:
                    all_received = False
            except PurchaseOrderLine.DoesNotExist:
                pass

        order.status = 'received' if all_received else 'partially_received'
        order.received_at = timezone.now()
        order.save()
        return Response(PurchaseOrderSerializer(order).data)


@api_view(['POST'])
def create_acquisition(request):
    """Register a used-phone / trade-in acquisition."""
    ser = AcquisitionSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    acq = ser.save(created_by=request.user)
    return Response(AcquisitionSerializer(acq).data, status=status.HTTP_201_CREATED)


class AcquisitionViewSet(viewsets.ModelViewSet):
    queryset = Acquisition.objects.select_related('customer', 'branch').all()
    serializer_class = AcquisitionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'branch']
    search_fields = ['acquisition_number', 'customer_name', 'imei', 'device_model']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
