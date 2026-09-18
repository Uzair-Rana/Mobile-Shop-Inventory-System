"""Actual (realised) business profit for a period.

    Sales profit   = Σ (sale price − cost price) × qty kept by the customer,
                     per kind: mobile phones, accessories/products, spare parts
                     − invoice-level discounts
    Repair profit  = labour charges
                     + parts billed − parts cost
                     − other repair costs (outside work, courier…)
    Net profit     = sales profit + repair profit − expenses

Sales count on the invoice date; repairs count when first marked Ready or
Delivered (completed_at); expenses on their expense date. Returned quantities
are excluded; voided / returned invoices don't count.
"""
from decimal import Decimal

ZERO = Decimal('0')
SALE_KINDS = [('unit', 'Mobile phones'), ('accessory', 'Accessories & products'),
              ('spare_part', 'Spare parts')]


def profit_summary(start, end=None):
    from apps.sales.models import Invoice, InvoiceLine
    from apps.repairs.models import RepairJob
    from apps.cash.models import Expense

    counted = ['finalized', 'paid', 'partially_paid']
    invoices = Invoice.objects.filter(status__in=counted, created_at__date__gte=start)
    if end:
        invoices = invoices.filter(created_at__date__lte=end)

    kinds = {k: {'label': label, 'qty': 0, 'revenue': ZERO, 'cost': ZERO} for k, label in SALE_KINDS}
    for line in InvoiceLine.objects.filter(invoice__in=invoices):
        kept = line.qty - (line.returned_qty or 0)
        if kept <= 0:
            continue
        row = kinds.get(line.product_type, kinds['accessory'])
        row['qty'] += kept
        row['revenue'] += line.unit_price * kept
        row['cost'] += (line.cost_price or ZERO) * kept
    for row in kinds.values():
        row['profit'] = row['revenue'] - row['cost']
    discounts = sum((i.discount_amount for i in invoices), ZERO)
    sales_profit = sum((r['profit'] for r in kinds.values()), ZERO) - discounts

    jobs = RepairJob.objects.filter(completed_at__date__gte=start).exclude(status='cancelled')
    if end:
        jobs = jobs.filter(completed_at__date__lte=end)
    labour = parts_billed = parts_cost = extra = ZERO
    for job in jobs.prefetch_related('parts'):
        labour += job.labour_charge or ZERO
        extra += job.extra_cost or ZERO
        for p in job.parts.all():
            parts_billed += p.unit_price * p.qty
            parts_cost += p.cost * p.qty
    repair_profit = labour + parts_billed - parts_cost - extra

    expenses_qs = Expense.objects.filter(expense_date__gte=start)
    if end:
        expenses_qs = expenses_qs.filter(expense_date__lte=end)
    expenses = sum((e.amount for e in expenses_qs), ZERO)

    return {
        'sales': list(kinds.values()),
        'discounts': discounts,
        'sales_profit': sales_profit,
        'repair_jobs': jobs.count(),
        'labour': labour,
        'parts_billed': parts_billed,
        'parts_cost': parts_cost,
        'repair_extra': extra,
        'repair_profit': repair_profit,
        'expenses': expenses,
        'net_profit': sales_profit + repair_profit - expenses,
    }


def unsold_stock_margin():
    """Profit still sitting in unsold stock (sell − cost), not yet earned."""
    from django.db.models import DecimalField, ExpressionWrapper, F, Sum
    from apps.inventory.models import Product, Unit
    products = Product.objects.filter(stock_qty__gt=0).aggregate(t=Sum(ExpressionWrapper(
        (F('sell_price') - F('cost_price')) * F('stock_qty'), output_field=DecimalField())))['t'] or ZERO
    phones = Unit.objects.filter(lifecycle_state='in_stock').aggregate(t=Sum(ExpressionWrapper(
        F('sell_price') - F('cost_price'), output_field=DecimalField())))['t'] or ZERO
    return products + phones
