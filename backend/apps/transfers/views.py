from django.utils import timezone
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Transfer, TransferItem
from .serializers import TransferSerializer, TransferCreateSerializer


class TransferViewSet(viewsets.ModelViewSet):
    queryset = Transfer.objects.select_related(
        'from_branch', 'to_branch', 'created_by', 'dispatched_by', 'received_by'
    ).prefetch_related('items').all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'from_branch', 'to_branch']
    search_fields = ['transfer_number']
    ordering_fields = ['created_at', 'dispatched_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return TransferCreateSerializer
        return TransferSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        branch_id = self.request.headers.get('X-Branch-ID')
        if branch_id:
            qs = qs.filter(
                Q(from_branch_id=branch_id) | Q(to_branch_id=branch_id)
            )
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def dispatch(self, request, pk=None):
        transfer = self.get_object()
        if transfer.status != 'draft':
            return Response({'detail': 'Only draft transfers can be dispatched.'}, status=400)

        # Move inventory: mark units as 'transferred', decrement product stock
        for item in transfer.items.all():
            if item.item_type == 'unit':
                from apps.inventory.models import Unit
                try:
                    unit = Unit.objects.get(id=item.item_id)
                    unit.lifecycle_state = 'transferred'
                    unit.save()
                except Unit.DoesNotExist:
                    pass
            else:
                from apps.inventory.models import Product, StockMovement
                try:
                    product = Product.objects.get(id=item.item_id)
                    product.stock_qty -= item.qty
                    product.save()
                    StockMovement.objects.create(
                        product=product,
                        type='transfer_out',
                        qty_change=-item.qty,
                        note=f'Transfer {transfer.transfer_number}',
                        actor=request.user,
                    )
                except Product.DoesNotExist:
                    pass

        transfer.status = 'dispatched'
        transfer.dispatched_by = request.user
        transfer.dispatched_at = timezone.now()
        transfer.save()
        return Response(TransferSerializer(transfer).data)

    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        transfer = self.get_object()
        if transfer.status != 'dispatched':
            return Response({'detail': 'Only dispatched transfers can be received.'}, status=400)

        # Move inventory to destination branch
        for item in transfer.items.all():
            if item.item_type == 'unit':
                from apps.inventory.models import Unit
                try:
                    unit = Unit.objects.get(id=item.item_id)
                    unit.lifecycle_state = 'in_stock'
                    unit.branch = transfer.to_branch
                    unit.save()
                except Unit.DoesNotExist:
                    pass
            else:
                from apps.inventory.models import Product, StockMovement
                try:
                    product = Product.objects.get(id=item.item_id)
                    product.stock_qty += item.qty
                    product.branch = transfer.to_branch
                    product.save()
                    StockMovement.objects.create(
                        product=product,
                        type='transfer_in',
                        qty_change=item.qty,
                        note=f'Transfer {transfer.transfer_number}',
                        actor=request.user,
                    )
                except Product.DoesNotExist:
                    pass

        transfer.status = 'received'
        transfer.received_by = request.user
        transfer.received_at = timezone.now()
        transfer.save()
        return Response(TransferSerializer(transfer).data)
