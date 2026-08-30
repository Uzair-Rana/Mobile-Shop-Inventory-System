from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from .models import Customer, CustomerLedger
from .serializers import CustomerSerializer, CustomerLedgerSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by('name')
    serializer_class = CustomerSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name', 'phone', 'cnic', 'email']

    @action(detail=True, methods=['get'])
    def ledger(self, request, pk=None):
        customer = self.get_object()
        entries = customer.ledger.all()
        return Response(CustomerLedgerSerializer(entries, many=True).data)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        # Returns sales invoices and repairs for this customer
        from apps.sales.models import Invoice
        from apps.sales.serializers import InvoiceSerializer
        invoices = Invoice.objects.filter(customer=self.get_object()).order_by('-created_at')[:20]
        return Response(InvoiceSerializer(invoices, many=True).data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        q = request.query_params.get('q', '')
        qs = Customer.objects.filter(name__icontains=q) | Customer.objects.filter(phone__icontains=q)
        return Response(CustomerSerializer(qs[:20], many=True).data)

    @action(detail=False, methods=['get'], url_path='check_duplicate')
    def check_duplicate(self, request):
        name = request.query_params.get('name', '')
        phone = request.query_params.get('phone', '')
        from django.db.models import Q
        qs = Customer.objects.filter(Q(name__iexact=name) | Q(phone=phone))
        if qs.exists():
            return Response({'duplicate': True, 'matches': CustomerSerializer(qs[:5], many=True).data})
        return Response({'duplicate': False, 'matches': []})
