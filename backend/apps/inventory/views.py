from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Product, Unit, StockMovement, Category, Brand
from .serializers import (
    ProductSerializer, UnitSerializer, StockMovementSerializer,
    StockAdjustSerializer, CategorySerializer, BrandSerializer,
    UnitCostAdjustSerializer,
)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['branch', 'category', 'brand']
    search_fields = ['name', 'sku', 'brand', 'category']
    ordering_fields = ['name', 'sell_price', 'stock_qty', 'created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        branch_id = self.request.headers.get('X-Branch-ID')
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        return qs

    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        product = self.get_object()
        ser = StockAdjustSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        qty = ser.validated_data['qty_change']
        note = ser.validated_data.get('note', '')
        product.stock_qty += qty
        product.save()
        StockMovement.objects.create(
            product=product,
            type='adjustment_in' if qty > 0 else 'adjustment_out',
            qty_change=qty,
            note=note,
            actor=request.user,
        )
        return Response(ProductSerializer(product).data)

    @action(detail=False, methods=['get'])
    def movements(self, request, pk=None):
        product_id = request.query_params.get('product_id')
        qs = StockMovement.objects.filter(product_id=product_id).order_by('-created_at')
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(StockMovementSerializer(page, many=True).data)
        return Response(StockMovementSerializer(qs, many=True).data)


class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.select_related('branch', 'added_by').all()
    serializer_class = UnitSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['lifecycle_state', 'branch', 'brand', 'condition']
    search_fields = ['imei1', 'imei2', 'serial', 'brand', 'model']

    def get_queryset(self):
        qs = super().get_queryset()
        branch_id = self.request.headers.get('X-Branch-ID')
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)

    @action(detail=False, methods=['get'])
    def by_imei(self, request):
        imei = request.query_params.get('imei')
        from django.db.models import Q
        try:
            unit = Unit.objects.get(Q(imei1=imei) | Q(imei2=imei))
            return Response(UnitSerializer(unit).data)
        except Unit.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)

    @action(detail=False, methods=['get'], url_path='check_duplicate')
    def check_duplicate(self, request):
        imei = request.query_params.get('imei', '')
        from django.db.models import Q
        exists = Unit.objects.filter(Q(imei1=imei) | Q(imei2=imei)).exists()
        return Response({'duplicate': exists, 'imei': imei})

    @action(detail=True, methods=['post'], url_path='adjust_cost')
    def adjust_cost(self, request, pk=None):
        unit = self.get_object()
        ser = UnitCostAdjustSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        old_cost = unit.cost_price
        unit.cost_price = ser.validated_data['cost_price']
        unit.save()
        # Record in audit — this is a privileged action, caller must have step-up token
        return Response({
            'id': unit.id,
            'old_cost_price': str(old_cost),
            'new_cost_price': str(unit.cost_price),
        })

    @action(detail=True, methods=['get'], url_path='timeline')
    def timeline(self, request, pk=None):
        """Return lifecycle events for a unit from StockMovements and status history."""
        unit = self.get_object()
        events = []

        # Acquisition event
        events.append({
            'id': f'acq-{unit.id}',
            'timestamp': unit.created_at.isoformat(),
            'actor': unit.added_by.username if unit.added_by else 'system',
            'type': 'acquisition',
            'title': 'Device acquired',
            'detail': f'Cost: {unit.cost_price} | Condition: {unit.condition}',
            'highlight': False,
        })

        # Current state
        events.append({
            'id': f'state-{unit.id}',
            'timestamp': unit.updated_at.isoformat(),
            'actor': 'system',
            'type': unit.lifecycle_state,
            'title': f'Current state: {unit.get_lifecycle_state_display()}',
            'detail': None,
            'highlight': True,
        })

        events.sort(key=lambda e: e['timestamp'])
        return Response(events)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


from rest_framework.decorators import api_view
from rest_framework.response import Response as R
from django.db.models import Q


@api_view(['GET'])
def scan_lookup(request):
    q = request.query_params.get('q', '')
    # Check units first (IMEI/serial devices)
    try:
        unit = Unit.objects.get(Q(imei1=q) | Q(imei2=q) | Q(serial=q))
        return R({
            'type': 'unit',
            'unit_id': unit.id,
            'product_id': unit.id,
            'name': f'{unit.brand} {unit.model}',
            'sku': unit.serial,
            'imei': unit.imei1,
            'price': str(unit.sell_price),
        })
    except Unit.DoesNotExist:
        pass
    # Then accessories (by SKU or name)
    try:
        acc = Product.objects.get(Q(sku=q))
        return R({
            'type': 'accessory',
            'product_id': acc.id,
            'name': acc.name,
            'sku': acc.sku,
            'imei': None,
            'price': str(acc.sell_price),
        })
    except Product.DoesNotExist:
        pass
    return R({'detail': 'Not found.'}, status=404)


@api_view(['GET'])
def low_stock_view(request):
    from django.db.models import F
    qs = Product.objects.filter(stock_qty__lte=F('reorder_level'))
    branch_id = request.headers.get('X-Branch-ID')
    if branch_id:
        qs = qs.filter(branch_id=branch_id)
    return R({'count': qs.count(), 'results': ProductSerializer(qs, many=True).data})
