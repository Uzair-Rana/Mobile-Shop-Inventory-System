import csv
from io import StringIO
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Sum, Count, Avg, F, Q, DecimalField
from django.db.models.functions import TruncDate, TruncMonth
from rest_framework.decorators import api_view
from rest_framework.response import Response


# ─── Helpers ────────────────────────────────────────────────────────────────

def _date_params(request):
    today = timezone.now().date()
    date_from = request.query_params.get('date_from', today.replace(day=1).isoformat())
    date_to   = request.query_params.get('date_to',   today.isoformat())
    return date_from, date_to


def _branch_filter(request, field='branch_id'):
    branch_id = request.headers.get('X-Branch-ID') or request.query_params.get('branch')
    return {field: branch_id} if branch_id else {}


def _csv_response(filename, headers, rows):
    buf = StringIO()
    writer = csv.writer(buf)
    writer.writerow(headers)
    writer.writerows(rows)
    response = HttpResponse(buf.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# ─── 1. Sales Summary ────────────────────────────────────────────────────────

@api_view(['GET'])
def sales_summary(request):
    from apps.sales.models import Invoice, InvoiceLine
    date_from, date_to = _date_params(request)
    bf = _branch_filter(request)

    invoices = Invoice.objects.filter(
        created_at__date__gte=date_from,
        created_at__date__lte=date_to,
        status__in=['finalized', 'paid', 'partially_paid'],
        **bf,
    )

    daily = (
        invoices
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(total=Sum('grand_total'), count=Count('id'))
        .order_by('day')
    )

    totals = invoices.aggregate(
        total_revenue=Sum('grand_total'),
        total_invoices=Count('id'),
        total_discount=Sum('discount_amount'),
        total_tax=Sum('tax_amount'),
    )

    return Response({
        'date_from': date_from,
        'date_to': date_to,
        'totals': {k: str(v or 0) for k, v in totals.items()},
        'daily': [
            {'date': str(r['day']), 'total': str(r['total']), 'count': r['count']}
            for r in daily
        ],
    })


# ─── 2. Profit & Loss ────────────────────────────────────────────────────────

@api_view(['GET'])
def profit_loss(request):
    from apps.sales.models import Invoice, InvoiceLine
    from apps.cash.models import Expense
    date_from, date_to = _date_params(request)
    bf = _branch_filter(request)

    invoices = Invoice.objects.filter(
        created_at__date__gte=date_from,
        created_at__date__lte=date_to,
        status__in=['finalized', 'paid', 'partially_paid'],
        **bf,
    )
    total_revenue = invoices.aggregate(t=Sum('grand_total'))['t'] or 0

    # Cost of goods — sum cost_price from sold units + product lines
    # Approximate via InvoiceLine (cost not stored directly on line — use product lookup)
    # For now: derive from Unit.cost_price for unit lines, Product.cost_price for accessory lines
    lines = InvoiceLine.objects.filter(invoice__in=invoices)
    cost_of_goods = 0
    for line in lines.select_related():
        if line.product_type == 'unit':
            from apps.inventory.models import Unit
            try:
                unit = Unit.objects.get(id=line.product_id)
                cost_of_goods += float(unit.cost_price) * line.qty
            except Exception:
                pass
        else:
            from apps.inventory.models import Product
            try:
                product = Product.objects.get(id=line.product_id)
                cost_of_goods += float(product.cost_price) * line.qty
            except Exception:
                pass

    expenses = Expense.objects.filter(
        expense_date__gte=date_from,
        expense_date__lte=date_to,
        **_branch_filter(request, field='branch_id'),
    ).aggregate(t=Sum('amount'))['t'] or 0

    gross_profit = float(total_revenue) - cost_of_goods
    net_profit   = gross_profit - float(expenses)
    margin       = round((gross_profit / float(total_revenue) * 100), 2) if total_revenue else 0

    return Response({
        'date_from': date_from,
        'date_to': date_to,
        'revenue': str(round(total_revenue, 2)),
        'cost_of_goods': str(round(cost_of_goods, 2)),
        'gross_profit': str(round(gross_profit, 2)),
        'gross_margin_pct': margin,
        'total_expenses': str(round(float(expenses), 2)),
        'net_profit': str(round(net_profit, 2)),
    })


# ─── 3. Inventory Valuation ──────────────────────────────────────────────────

@api_view(['GET'])
def inventory_valuation(request):
    from apps.inventory.models import Product, Unit
    bf = _branch_filter(request)

    products = Product.objects.filter(**bf)
    units    = Unit.objects.filter(lifecycle_state='in_stock', **bf)

    product_value = products.aggregate(
        cost=Sum(F('cost_price') * F('stock_qty'), output_field=DecimalField()),
        retail=Sum(F('sell_price') * F('stock_qty'), output_field=DecimalField()),
        items=Count('id'),
    )
    unit_value = units.aggregate(
        cost=Sum('cost_price'),
        retail=Sum('sell_price'),
        items=Count('id'),
    )

    return Response({
        'accessories': {
            'items': product_value['items'],
            'cost_value': str(product_value['cost'] or 0),
            'retail_value': str(product_value['retail'] or 0),
        },
        'devices': {
            'items': unit_value['items'],
            'cost_value': str(unit_value['cost'] or 0),
            'retail_value': str(unit_value['retail'] or 0),
        },
        'totals': {
            'cost_value': str((product_value['cost'] or 0) + (unit_value['cost'] or 0)),
            'retail_value': str((product_value['retail'] or 0) + (unit_value['retail'] or 0)),
        },
    })


# ─── 4. IMEI History ─────────────────────────────────────────────────────────

@api_view(['GET'])
def imei_history(request):
    from apps.inventory.models import Unit
    imei = request.query_params.get('imei', '')
    if not imei:
        return Response({'detail': 'imei parameter is required.'}, status=400)

    from django.db.models import Q
    units = Unit.objects.filter(Q(imei1=imei) | Q(imei2=imei))
    if not units.exists():
        return Response({'detail': 'No device found with that IMEI.'}, status=404)

    unit = units.first()
    # Build a timeline from available data
    events = [
        {
            'event': 'acquired',
            'timestamp': unit.created_at.isoformat(),
            'detail': f'{unit.brand} {unit.model} | {unit.condition} | Cost: {unit.cost_price}',
        },
        {
            'event': unit.lifecycle_state,
            'timestamp': unit.updated_at.isoformat(),
            'detail': f'Current state: {unit.get_lifecycle_state_display()}',
        },
    ]

    # Check if sold
    from apps.sales.models import InvoiceLine
    sale_line = InvoiceLine.objects.filter(imei=imei).select_related('invoice').first()
    if sale_line:
        events.append({
            'event': 'sold',
            'timestamp': sale_line.invoice.created_at.isoformat(),
            'detail': f'Invoice {sale_line.invoice.invoice_number} | {sale_line.invoice.customer_name}',
        })

    events.sort(key=lambda e: e['timestamp'])
    return Response({'imei': imei, 'unit': {'id': unit.id, 'brand': unit.brand, 'model': unit.model}, 'events': events})


# ─── 5. Repairs Report ───────────────────────────────────────────────────────

@api_view(['GET'])
def repairs_report(request):
    from apps.repairs.models import RepairJob
    date_from, date_to = _date_params(request)
    bf = _branch_filter(request)

    jobs = RepairJob.objects.filter(
        created_at__date__gte=date_from,
        created_at__date__lte=date_to,
        **bf,
    )

    by_status = jobs.values('status').annotate(count=Count('id')).order_by('status')
    totals = jobs.aggregate(
        total_jobs=Count('id'),
        total_revenue=Sum('final_cost'),
        total_collected=Sum('amount_paid'),
    )

    return Response({
        'date_from': date_from,
        'date_to': date_to,
        'totals': {k: str(v or 0) for k, v in totals.items()},
        'by_status': list(by_status),
    })


# ─── 6. Installments Report ──────────────────────────────────────────────────

@api_view(['GET'])
def installments_report(request):
    from apps.installments.models import InstallmentPlan, InstallmentPayment
    date_from, date_to = _date_params(request)
    bf = _branch_filter(request)

    plans = InstallmentPlan.objects.filter(**bf)
    by_status = plans.values('status').annotate(count=Count('id')).order_by('status')

    collections = InstallmentPayment.objects.filter(
        collected_at__date__gte=date_from,
        collected_at__date__lte=date_to,
        plan__in=plans,
    ).aggregate(total=Sum('amount'), count=Count('id'))

    return Response({
        'date_from': date_from,
        'date_to': date_to,
        'by_status': list(by_status),
        'collections_in_period': {
            'total': str(collections['total'] or 0),
            'count': collections['count'],
        },
        'total_outstanding': str(
            plans.filter(status='active').aggregate(t=Sum('balance_remaining'))['t'] or 0
        ),
    })


# ─── 7. Customer Ledger ──────────────────────────────────────────────────────

@api_view(['GET'])
def customer_ledger(request):
    from apps.customers.models import Customer, CustomerLedger
    customer_id = request.query_params.get('customer_id')
    date_from, date_to = _date_params(request)

    if not customer_id:
        return Response({'detail': 'customer_id is required.'}, status=400)

    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return Response({'detail': 'Customer not found.'}, status=404)

    entries = CustomerLedger.objects.filter(
        customer=customer,
        created_at__date__gte=date_from,
        created_at__date__lte=date_to,
    ).order_by('created_at')

    # Build running balance
    rows = []
    running = 0
    for e in entries:
        amt = float(e.amount)
        if e.type == 'debit':
            running += amt
        else:
            running -= amt
        rows.append({
            'id': e.id,
            'date': e.created_at.isoformat(),
            'description': e.description,
            'reference': e.reference,
            'debit': str(e.amount) if e.type == 'debit' else '0',
            'credit': str(e.amount) if e.type == 'credit' else '0',
            'balance': str(round(running, 2)),
        })

    return Response({
        'customer': {'id': customer.id, 'name': customer.name, 'phone': customer.phone},
        'date_from': date_from,
        'date_to': date_to,
        'entries': rows,
    })


# ─── 8. Staff Performance ────────────────────────────────────────────────────

@api_view(['GET'])
def staff_performance(request):
    from apps.sales.models import Invoice
    from apps.repairs.models import RepairJob
    date_from, date_to = _date_params(request)
    bf = _branch_filter(request)

    sales_by_staff = (
        Invoice.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to,
            status__in=['finalized', 'paid', 'partially_paid'],
            **bf,
        )
        .values('created_by__id', 'created_by__username', 'created_by__full_name')
        .annotate(invoice_count=Count('id'), total_sales=Sum('grand_total'))
        .order_by('-total_sales')
    )

    repairs_by_tech = (
        RepairJob.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to,
            **bf,
        )
        .values('technician__id', 'technician__username')
        .annotate(job_count=Count('id'), total_revenue=Sum('final_cost'))
        .order_by('-job_count')
    )

    return Response({
        'date_from': date_from,
        'date_to': date_to,
        'sales': [
            {
                'user_id': r['created_by__id'],
                'username': r['created_by__username'],
                'full_name': r['created_by__full_name'],
                'invoice_count': r['invoice_count'],
                'total_sales': str(r['total_sales'] or 0),
            }
            for r in sales_by_staff
        ],
        'repairs': [
            {
                'user_id': r['technician__id'],
                'username': r['technician__username'],
                'job_count': r['job_count'],
                'total_revenue': str(r['total_revenue'] or 0),
            }
            for r in repairs_by_tech
        ],
    })


# ─── 9. Dead Stock ───────────────────────────────────────────────────────────

@api_view(['GET'])
def dead_stock(request):
    from apps.inventory.models import Product, Unit
    from datetime import timedelta
    bf = _branch_filter(request)
    threshold_days = int(request.query_params.get('days', 90))
    cutoff = timezone.now() - timedelta(days=threshold_days)

    # Products with no sales movement since cutoff
    dead_products = Product.objects.filter(
        stock_qty__gt=0,
        updated_at__lt=cutoff,
        **bf,
    ).values('id', 'name', 'sku', 'stock_qty', 'sell_price', 'cost_price', 'updated_at')

    # Units in_stock since cutoff
    dead_units = Unit.objects.filter(
        lifecycle_state='in_stock',
        updated_at__lt=cutoff,
        **bf,
    ).values('id', 'brand', 'model', 'imei1', 'sell_price', 'cost_price', 'updated_at')

    return Response({
        'threshold_days': threshold_days,
        'dead_accessories': [
            {**r, 'sell_price': str(r['sell_price']), 'cost_price': str(r['cost_price']),
             'updated_at': r['updated_at'].isoformat()}
            for r in dead_products
        ],
        'dead_devices': [
            {**r, 'sell_price': str(r['sell_price']), 'cost_price': str(r['cost_price']),
             'updated_at': r['updated_at'].isoformat()}
            for r in dead_units
        ],
    })


# ─── 10. Cash Report ─────────────────────────────────────────────────────────

@api_view(['GET'])
def cash_report(request):
    from apps.cash.models import CashSession, CashEntry, Expense
    date_from, date_to = _date_params(request)
    bf = _branch_filter(request)

    sessions = CashSession.objects.filter(
        opened_at__date__gte=date_from,
        opened_at__date__lte=date_to,
        **bf,
    )
    entries = CashEntry.objects.filter(session__in=sessions)

    inflows  = entries.filter(type='inflow').aggregate(t=Sum('amount'))['t'] or 0
    outflows = entries.filter(type='outflow').aggregate(t=Sum('amount'))['t'] or 0

    expenses = Expense.objects.filter(
        expense_date__gte=date_from,
        expense_date__lte=date_to,
        **_branch_filter(request, field='branch_id'),
    ).aggregate(t=Sum('amount'))['t'] or 0

    by_category = (
        entries.filter(type='inflow')
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    return Response({
        'date_from': date_from,
        'date_to': date_to,
        'total_inflows': str(inflows),
        'total_outflows': str(outflows),
        'total_expenses': str(expenses),
        'net_cash': str(float(inflows) - float(outflows) - float(expenses)),
        'by_category': [
            {'category': r['category'], 'total': str(r['total'])}
            for r in by_category
        ],
        'session_count': sessions.count(),
    })


# ─── CSV Export ──────────────────────────────────────────────────────────────

EXPORT_MAP = {
    'sales-summary':         (sales_summary,         ['Date', 'Total', 'Count']),
    'profit-loss':           (profit_loss,            ['Metric', 'Value']),
    'inventory-valuation':   (inventory_valuation,    ['Type', 'Items', 'Cost Value', 'Retail Value']),
    'repairs':               (repairs_report,         ['Status', 'Count']),
    'installments':          (installments_report,    ['Status', 'Count']),
    'staff-performance':     (staff_performance,      ['User', 'Invoices', 'Total Sales']),
    'dead-stock':            (dead_stock,             ['Name', 'SKU', 'Qty', 'Sell Price', 'Last Updated']),
    'cash':                  (cash_report,            ['Category', 'Total']),
}


@api_view(['GET'])
def export_report(request, slug):
    """Generic CSV export — calls the matching report view and flattens to CSV."""
    if slug not in EXPORT_MAP:
        return Response({'detail': f'Unknown report slug: {slug}'}, status=404)

    view_fn, headers = EXPORT_MAP[slug]
    # Call the view internally to get the data dict
    inner_response = view_fn(request._request)
    data = inner_response.data

    buf = StringIO()
    writer = csv.writer(buf)
    writer.writerow(headers)

    # Best-effort flat export: write key-value pairs from the top-level dict
    for key, value in data.items():
        if isinstance(value, list):
            for row in value:
                if isinstance(row, dict):
                    writer.writerow(list(row.values()))
                else:
                    writer.writerow([row])
        elif isinstance(value, dict):
            for k, v in value.items():
                writer.writerow([k, v])
        else:
            writer.writerow([key, value])

    response = HttpResponse(buf.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{slug}-report.csv"'
    return response
