from django.utils import timezone
from django.db.models import Sum, Q
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import CashSession, CashEntry, Expense
from .serializers import (
    CashSessionSerializer, CashEntrySerializer, CashEntryCreateSerializer,
    ExpenseSerializer, CloseSessionSerializer,
)


@api_view(['GET'])
def current_session(request):
    """Get the open session for the requesting branch, or 404."""
    branch_id = request.headers.get('X-Branch-ID')
    qs = CashSession.objects.filter(status='open')
    if branch_id:
        qs = qs.filter(branch_id=branch_id)
    session = qs.order_by('-opened_at').first()
    if not session:
        return Response({'detail': 'No open session.'}, status=404)
    return Response(CashSessionSerializer(session).data)


@api_view(['POST'])
def open_session(request):
    """Open a new cash session. Only one open session per branch allowed."""
    branch_id = request.headers.get('X-Branch-ID') or request.data.get('branch')
    if not branch_id:
        return Response({'detail': 'branch is required.'}, status=400)

    already_open = CashSession.objects.filter(branch_id=branch_id, status='open').exists()
    if already_open:
        return Response({'detail': 'A session is already open for this branch.'}, status=400)

    opening_amount = request.data.get('opening_amount', 0)
    session = CashSession.objects.create(
        branch_id=branch_id,
        opened_by=request.user,
        opening_amount=opening_amount,
        expected_closing=opening_amount,
    )
    return Response(CashSessionSerializer(session).data, status=201)


@api_view(['POST'])
def close_session(request):
    """Initiate close — transitions to pending_count."""
    branch_id = request.headers.get('X-Branch-ID')
    qs = CashSession.objects.filter(status='open')
    if branch_id:
        qs = qs.filter(branch_id=branch_id)
    session = qs.order_by('-opened_at').first()
    if not session:
        return Response({'detail': 'No open session to close.'}, status=404)

    ser = CloseSessionSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    counted = ser.validated_data['counted_amount']

    # Calculate expected
    inflows = session.entries.filter(type='inflow').aggregate(t=Sum('amount'))['t'] or 0
    outflows = session.entries.filter(type='outflow').aggregate(t=Sum('amount'))['t'] or 0
    expected = session.opening_amount + inflows - outflows

    session.counted_amount = counted
    session.expected_closing = expected
    session.variance = counted - expected
    session.status = 'closed'
    session.closed_by = request.user
    session.closed_at = timezone.now()
    session.notes = ser.validated_data.get('notes', '')
    session.save()
    return Response(CashSessionSerializer(session).data)


@api_view(['POST'])
def add_inflow(request, session_id):
    session = _get_session(session_id)
    return _add_entry(request, session, entry_type='inflow')


@api_view(['POST'])
def add_outflow(request, session_id):
    session = _get_session(session_id)
    return _add_entry(request, session, entry_type='outflow')


def _get_session(session_id):
    return CashSession.objects.get(id=session_id)


def _add_entry(request, session, entry_type):
    if session.status != 'open':
        return Response({'detail': 'Session is not open.'}, status=400)
    ser = CashEntryCreateSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    entry = CashEntry.objects.create(
        session=session,
        type=entry_type,
        created_by=request.user,
        **ser.validated_data,
    )
    # Update expected_closing
    inflows = session.entries.filter(type='inflow').aggregate(t=Sum('amount'))['t'] or 0
    outflows = session.entries.filter(type='outflow').aggregate(t=Sum('amount'))['t'] or 0
    session.expected_closing = session.opening_amount + inflows - outflows
    session.save(update_fields=['expected_closing'])
    return Response(CashEntrySerializer(entry).data, status=201)


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.select_related('branch').all()
    serializer_class = ExpenseSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['branch', 'category', 'expense_date']
    ordering_fields = ['expense_date', 'amount', 'created_at']
    ordering = ['-expense_date']

    def get_queryset(self):
        qs = super().get_queryset()
        branch_id = self.request.headers.get('X-Branch-ID')
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            qs = qs.filter(expense_date__gte=date_from)
        if date_to:
            qs = qs.filter(expense_date__lte=date_to)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
