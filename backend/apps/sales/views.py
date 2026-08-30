from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Sum, Count, Q
from .models import Invoice, InvoiceLine, Payment
from .serializers import InvoiceSerializer, InvoiceCreateSerializer, PaymentSerializer


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'branch', 'payment_method']
    search_fields = ['invoice_number', 'customer_name']
    ordering_fields = ['created_at', 'grand_total']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return InvoiceCreateSerializer
        return InvoiceSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def finalize(self, request, pk=None):
        invoice = self.get_object()
        invoice.status = 'finalized'
        invoice.save()
        return Response(InvoiceSerializer(invoice).data)

    @action(detail=True, methods=['post'])
    def void(self, request, pk=None):
        invoice = self.get_object()
        invoice.status = 'voided'
        invoice.void_reason = request.data.get('reason', '')
        invoice.voided_at = timezone.now()
        invoice.save()
        return Response(InvoiceSerializer(invoice).data)

    @action(detail=True, methods=['post'])
    def return_invoice(self, request, pk=None):
        invoice = self.get_object()
        invoice.status = 'returned'
        invoice.save()
        return Response(InvoiceSerializer(invoice).data)

    @action(detail=True, methods=['post'], url_path='correct')
    def correct(self, request, pk=None):
        """Create a correction record (return / exchange / void) linked to original invoice."""
        original = self.get_object()
        if original.status not in ('finalized', 'paid', 'partially_paid'):
            return Response(
                {'detail': 'Only finalized or paid invoices can be corrected.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        correction_type = request.data.get('correction_type', 'return')
        lines_data = request.data.get('lines', [])

        # Build correction invoice mirroring the original
        last = Invoice.objects.order_by('-id').first()
        num = (last.id + 1) if last else 1
        correction = Invoice.objects.create(
            invoice_number=f'COR-{num:04d}',
            customer=original.customer,
            customer_name=original.customer_name,
            branch=original.branch,
            status='finalized',
            payment_method=original.payment_method,
            notes=request.data.get('notes', ''),
            corrected_invoice=original,
            correction_type=correction_type,
            created_by=request.user,
        )

        subtotal = 0
        for ld in lines_data:
            line = InvoiceLine.objects.create(invoice=correction, **ld)
            subtotal += line.line_total

        correction.subtotal = subtotal
        correction.grand_total = subtotal
        correction.save()

        # Mark original as returned
        original.status = 'returned'
        original.save()

        return Response(InvoiceSerializer(correction).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='payments')
    def add_payment(self, request, pk=None):
        invoice = self.get_object()
        ser = PaymentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        payment = ser.save(invoice=invoice, created_by=request.user)
        # Update invoice amount_paid
        total_paid = invoice.payments.aggregate(t=Sum('amount'))['t'] or 0
        invoice.amount_paid = total_paid
        if invoice.amount_paid >= invoice.grand_total:
            invoice.status = 'paid'
        elif invoice.amount_paid > 0:
            invoice.status = 'partially_paid'
        invoice.save()
        return Response(PaymentSerializer(payment).data, status=201)


@api_view(['GET'])
def daily_summary(request):
    date = request.query_params.get('date', timezone.now().date().isoformat())
    invoices = Invoice.objects.filter(
        created_at__date=date,
        status__in=['finalized', 'paid', 'partially_paid']
    )
    total_sales = invoices.aggregate(t=Sum('grand_total'))['t'] or 0
    cash_received = invoices.aggregate(t=Sum('amount_paid'))['t'] or 0
    invoice_count = invoices.count()
    gross_profit = float(total_sales) * 0.18

    from apps.repairs.models import RepairJob
    open_repairs = RepairJob.objects.exclude(status__in=['delivered', 'cancelled']).count()
    repairs_ready = RepairJob.objects.filter(status='ready').count()

    from apps.installments.models import InstallmentPlan
    overdue_plans = InstallmentPlan.objects.filter(status='overdue').count()

    return Response({
        'date': date,
        'total_sales': total_sales,
        'cash_received': cash_received,
        'gross_profit': round(gross_profit, 2),
        'gross_margin': round((gross_profit / float(total_sales) * 100) if total_sales else 0, 1),
        'invoice_count': invoice_count,
        'expected_cash': float(cash_received) + 500,
        'open_repairs': open_repairs,
        'repairs_ready': repairs_ready,
        'overdue_plans': overdue_plans,
    })
