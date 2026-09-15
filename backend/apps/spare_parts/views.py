from django.db import transaction
from django.db.models import Sum, Value, IntegerField, OuterRef, Subquery
from django.db.models.functions import Coalesce
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import SparePart, SparePartLedger
from .serializers import (
    SparePartSerializer, SparePartDetailSerializer,
    SparePartLedgerSerializer,
    StockInSerializer, StockOutSerializer,
)
from apps.audit.models import AuditTrail
from apps.audit.recorder import record_audit


class SparePartViewSet(viewsets.ModelViewSet):
    """
    CRUD for the spare-parts master catalog plus stock-in / stock-out actions.

    List endpoint annotates stock_on_hand via a subquery so no N+1 queries.
    Detail endpoint returns the full ledger.
    """
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'brand_compat', 'branch', 'is_active']
    search_fields    = ['sku', 'name', 'brand_compat', 'model_compat']
    ordering_fields  = ['name', 'sku', 'category', 'cost_price', 'sell_price']
    ordering         = ['category', 'name']

    def get_queryset(self):
        # Annotate each part with its current stock derived from the ledger
        ledger_sum = (
            SparePartLedger.objects
            .filter(part=OuterRef('pk'))
            .values('part')
            .annotate(s=Sum('qty'))
            .values('s')
        )
        qs = SparePart.objects.annotate(
            _stock=Coalesce(
                Subquery(ledger_sum, output_field=IntegerField()),
                Value(0, output_field=IntegerField()),
            )
        )
        # Branch filter from header
        branch_id = self.request.headers.get('X-Branch-ID')
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        # Optional ?low_stock=true
        if self.request.query_params.get('low_stock') == 'true':
            qs = [p for p in qs if p._stock <= p.reorder_level]
        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SparePartDetailSerializer
        return SparePartSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    # ── Stock IN ──────────────────────────────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='stock-in')
    @transaction.atomic
    def stock_in(self, request, pk=None):
        part = SparePart.objects.select_for_update().get(pk=pk)
        ser  = StockInSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d    = ser.validated_data

        prev_balance = part.stock_on_hand

        entry = SparePartLedger.objects.create(
            part       = part,
            entry_type = d['entry_type'],
            qty        = d['qty'],           # positive
            unit_cost  = d.get('unit_cost'),
            reference  = d.get('reference', ''),
            note       = d.get('note', ''),
            actor      = request.user,
        )

        record_audit(
            actor       = request.user,
            action_type = AuditTrail.MANUAL_STOCK_ADJUSTMENT,
            entity_type = 'SparePart',
            entity_id   = part.pk,
            previous_values = {'stock_on_hand': prev_balance},
            new_values      = {'stock_on_hand': entry.balance_after},
            reason      = f'{d["entry_type"]} +{d["qty"]}  ref={d.get("reference","")}',
            request     = request,
        )

        return Response({
            'entry':         SparePartLedgerSerializer(entry).data,
            'prev_balance':  prev_balance,
            'new_balance':   entry.balance_after,
        }, status=status.HTTP_201_CREATED)

    # ── Stock OUT ─────────────────────────────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='stock-out')
    @transaction.atomic
    def stock_out(self, request, pk=None):
        part = SparePart.objects.select_for_update().get(pk=pk)
        ser  = StockOutSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d    = ser.validated_data

        prev_balance = part.stock_on_hand
        if prev_balance < d['qty']:
            return Response(
                {'detail': f'Insufficient stock. Available: {prev_balance}, requested: {d["qty"]}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        entry = SparePartLedger.objects.create(
            part       = part,
            entry_type = d['entry_type'],
            qty        = -d['qty'],          # negate → negative ledger entry
            unit_cost  = None,
            reference  = d.get('reference', ''),
            note       = d.get('note', ''),
            actor      = request.user,
        )

        record_audit(
            actor       = request.user,
            action_type = AuditTrail.MANUAL_STOCK_ADJUSTMENT,
            entity_type = 'SparePart',
            entity_id   = part.pk,
            previous_values = {'stock_on_hand': prev_balance},
            new_values      = {'stock_on_hand': entry.balance_after},
            reason      = f'{d["entry_type"]} -{d["qty"]}  ref={d.get("reference","")}',
            request     = request,
        )

        return Response({
            'entry':        SparePartLedgerSerializer(entry).data,
            'prev_balance': prev_balance,
            'new_balance':  entry.balance_after,
        }, status=status.HTTP_201_CREATED)

    # ── Ledger (full history) ──────────────────────────────────────────────────
    @action(detail=True, methods=['get'], url_path='ledger')
    def ledger(self, request, pk=None):
        part    = self.get_object()
        entries = part.ledger.select_related('actor').order_by('-created_at')
        page    = self.paginate_queryset(entries)
        if page is not None:
            return self.get_paginated_response(
                SparePartLedgerSerializer(page, many=True).data)
        return Response(SparePartLedgerSerializer(entries, many=True).data)

    # ── Category metadata ──────────────────────────────────────────────────────
    @action(detail=False, methods=['get'], url_path='categories')
    def categories(self, request):
        return Response([
            {'value': c.value, 'label': c.label}
            for c in SparePart.Category
        ])

    # ── Low-stock summary ──────────────────────────────────────────────────────
    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request):
        qs = self.get_queryset()
        if isinstance(qs, list):
            low = qs  # already filtered
        else:
            low = [p for p in qs if p._stock <= p.reorder_level]
        return Response(SparePartSerializer(low, many=True).data)
