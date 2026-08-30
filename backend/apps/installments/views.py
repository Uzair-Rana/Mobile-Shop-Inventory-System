from datetime import timedelta
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import InstallmentPlan, InstallmentSchedule, InstallmentPayment
from .serializers import (
    InstallmentPlanSerializer, InstallmentPlanCreateSerializer,
    InstallmentScheduleSerializer, CollectPaymentSerializer,
)


class InstallmentPlanViewSet(viewsets.ModelViewSet):
    queryset = InstallmentPlan.objects.select_related('customer', 'branch').prefetch_related('schedule').all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'branch', 'customer']
    search_fields = ['plan_number', 'customer__name', 'customer__phone']
    ordering_fields = ['created_at', 'next_due_date', 'balance_remaining']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return InstallmentPlanCreateSerializer
        return InstallmentPlanSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        branch_id = self.request.headers.get('X-Branch-ID')
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        return qs

    def perform_create(self, serializer):
        plan = serializer.save(created_by=self.request.user)
        self._generate_schedule(plan)

    def _generate_schedule(self, plan):
        """Auto-generate schedule rows after plan creation."""
        today = plan.start_date
        for i in range(1, plan.installment_count + 1):
            # Add one month per installment
            due = today.replace(day=1)
            month = due.month + i - 1
            year = due.year + (month - 1) // 12
            month = ((month - 1) % 12) + 1
            try:
                due = due.replace(year=year, month=month, day=today.day)
            except ValueError:
                # Handle end-of-month edge cases
                import calendar
                last_day = calendar.monthrange(year, month)[1]
                due = due.replace(year=year, month=month, day=last_day)

            # Last installment absorbs any rounding remainder
            if i == plan.installment_count:
                amount = plan.total_payable - (plan.installment_amount * (plan.installment_count - 1))
            else:
                amount = plan.installment_amount

            InstallmentSchedule.objects.create(
                plan=plan,
                installment_number=i,
                due_date=due,
                amount_due=round(amount, 2),
            )

        # Set next_due_date
        first = plan.schedule.order_by('due_date').first()
        if first:
            plan.next_due_date = first.due_date
            plan.save(update_fields=['next_due_date'])

    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        plan = self.get_object()
        return Response(InstallmentScheduleSerializer(plan.schedule.all(), many=True).data)

    @action(detail=True, methods=['post'])
    def collect(self, request, pk=None):
        plan = self.get_object()
        ser = CollectPaymentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        amount = ser.validated_data['amount']
        schedule_id = ser.validated_data.get('schedule_item_id')

        # Record payment
        payment = InstallmentPayment.objects.create(
            plan=plan,
            schedule_item_id=schedule_id,
            amount=amount,
            payment_method=ser.validated_data.get('payment_method', 'cash'),
            reference=ser.validated_data.get('reference', ''),
            collected_by=request.user,
        )

        # Update plan totals
        plan.amount_paid = (plan.amount_paid or 0) + amount
        plan.balance_remaining = plan.total_payable - plan.amount_paid

        if plan.balance_remaining <= 0:
            plan.status = 'completed'
            plan.balance_remaining = 0

        # Mark schedule item if provided
        if schedule_id:
            try:
                item = InstallmentSchedule.objects.get(id=schedule_id, plan=plan)
                item.amount_paid = (item.amount_paid or 0) + amount
                item.status = 'paid' if item.amount_paid >= item.amount_due else 'partial'
                if item.status == 'paid':
                    item.paid_at = timezone.now()
                item.save()
            except InstallmentSchedule.DoesNotExist:
                pass

        # Update next_due_date to next unpaid item
        next_item = plan.schedule.filter(status__in=['pending', 'partial', 'overdue']).order_by('due_date').first()
        if next_item:
            plan.next_due_date = next_item.due_date

        plan.save()
        return Response(InstallmentPlanSerializer(plan).data)


@api_view(['GET'])
def overdue_plans(request):
    """List all overdue plans."""
    today = timezone.now().date()
    plans = InstallmentPlan.objects.filter(
        status='active',
        next_due_date__lt=today
    ).select_related('customer', 'branch')
    from .serializers import InstallmentPlanSerializer
    return Response({
        'count': plans.count(),
        'results': InstallmentPlanSerializer(plans, many=True).data,
    })


@api_view(['GET'])
def aging_view(request):
    """Overdue installments grouped into aging buckets."""
    today = timezone.now().date()
    overdue_items = InstallmentSchedule.objects.filter(
        status__in=['pending', 'partial'],
        due_date__lt=today
    ).select_related('plan__customer')

    buckets = {
        '1-7d': {'count': 0, 'amount': 0},
        '8-30d': {'count': 0, 'amount': 0},
        '31-60d': {'count': 0, 'amount': 0},
        '61-90d': {'count': 0, 'amount': 0},
        '90d+': {'count': 0, 'amount': 0},
    }

    for item in overdue_items:
        days = (today - item.due_date).days
        remaining = float(item.amount_due - item.amount_paid)
        if days <= 7:
            key = '1-7d'
        elif days <= 30:
            key = '8-30d'
        elif days <= 60:
            key = '31-60d'
        elif days <= 90:
            key = '61-90d'
        else:
            key = '90d+'
        buckets[key]['count'] += 1
        buckets[key]['amount'] += remaining

    return Response({'buckets': buckets, 'as_of': today.isoformat()})
