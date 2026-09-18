from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q, F, Count
from django.views.decorators.http import require_POST
from django.utils import timezone

from .nav import SECTIONS, TABS


# ── Auth helpers ──────────────────────────────────────────────────────────────

def activate(request):
    """First-run activation — requires the installation key to unlock the app."""
    from .activation import is_activated, set_activated, check_key
    if is_activated():
        return redirect('web:dashboard')
    error = ''
    if request.method == 'POST':
        if check_key(request.POST.get('key', '')):
            set_activated()
            return redirect('web:dashboard')
        error = 'Invalid installation key. Please try again.'
    return render(request, 'web/activate.html', {'error': error})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('web:dashboard')
    error = False
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username', ''),
            password=request.POST.get('password', ''),
        )
        if user:
            auth_login(request, user)
            return redirect(request.POST.get('next') or 'web:dashboard')
        error = True
    return render(request, 'web/login.html', {'error': error})


def logout_view(request):
    auth_logout(request)
    return redirect('web:login')


# ── Base context helper ───────────────────────────────────────────────────────

def _ctx(active, **extra):
    d = {'tabs': TABS, 'active': active}
    d.update(extra)
    return d


# ── Dashboard ─────────────────────────────────────────────────────────────────

@login_required(login_url='web:login')
def dashboard(request):
    from apps.sales.models import Invoice
    from apps.repairs.models import RepairJob
    from apps.inventory.models import Product, Unit
    from apps.installments.models import InstallmentPlan

    from datetime import timedelta
    from django.db.models import DecimalField, ExpressionWrapper
    from apps.cash.models import Expense
    from apps.transfers.models import Transfer

    today = timezone.now().date()

    # ── Time period the admin is viewing ──────────────────────────────────────
    period = request.GET.get('period', 'today')
    if period == 'week':
        start, period_label = today - timedelta(days=6), 'This Week'
    elif period == 'month':
        start, period_label = today.replace(day=1), 'This Month'
    elif period == 'year':
        start, period_label = today.replace(month=1, day=1), 'This Year'
    else:
        period, start, period_label = 'today', today, 'Today'
    periods = [('today', 'Today'), ('week', 'Weekly'), ('month', 'Monthly'), ('year', 'Yearly')]

    # ── Money flows within the selected period ────────────────────────────────
    # Sales = fully PAID invoices only. Udhaar / pending invoices are NOT sales.
    paid_invoices   = Invoice.objects.filter(status='paid', created_at__date__gte=start)
    period_invoices = Invoice.objects.filter(
        status__in=['finalized', 'paid', 'partially_paid'], created_at__date__gte=start)

    repairs_period = RepairJob.objects.filter(updated_at__date__gte=start)
    repair_income  = repairs_period.aggregate(t=Sum('amount_paid'))['t'] or 0

    total_sales   = paid_invoices.aggregate(t=Sum('grand_total'))['t'] or 0
    cash_received = (period_invoices.aggregate(t=Sum('amount_paid'))['t'] or 0) + repair_income
    expenses_period = Expense.objects.filter(expense_date__gte=start).aggregate(t=Sum('amount'))['t'] or 0
    net_cash = cash_received - expenses_period

    # ── Outstanding "udhaar" (credit) — current balances, not period-bound ─────
    inv_receivable = (Invoice.objects.filter(status='partially_paid')
                      .aggregate(t=Sum('balance_due'))['t'] or 0)
    repair_receivable = (RepairJob.objects.exclude(status='cancelled')
                         .filter(final_cost__gt=F('amount_paid'))
                         .aggregate(t=Sum(ExpressionWrapper(
                             F('final_cost') - F('amount_paid'),
                             output_field=DecimalField())))['t'] or 0)
    udhaar = inv_receivable + repair_receivable

    # ── Current-state snapshots (independent of the period) ───────────────────
    prod_profit = Product.objects.aggregate(t=Sum(ExpressionWrapper(
        (F('sell_price') - F('cost_price')) * F('stock_qty'),
        output_field=DecimalField())))['t'] or 0
    unit_profit = Unit.objects.filter(lifecycle_state='in_stock').aggregate(t=Sum(ExpressionWrapper(
        F('sell_price') - F('cost_price'), output_field=DecimalField())))['t'] or 0
    stock_profit = prod_profit + unit_profit

    open_repairs  = RepairJob.objects.exclude(status__in=['delivered', 'cancelled']).count()
    devices_stock = Unit.objects.filter(lifecycle_state='in_stock').count()
    overdue_plans = InstallmentPlan.objects.filter(status='active', next_due_date__lt=today).count()
    transfers_open = Transfer.objects.exclude(status__in=['received', 'cancelled']).count()

    kpis = [
        {'label': f'Sales ({period_label})',   'value': f'Rs. {total_sales:,.0f}',    'color': 'rose'},
        {'label': 'Cash Received',            'value': f'Rs. {cash_received:,.0f}',   'color': 'green'},
        {'label': 'Repairs Income',           'value': f'Rs. {repair_income:,.0f}',   'color': 'blue'},
        {'label': 'Expenses',                 'value': f'Rs. {expenses_period:,.0f}', 'color': 'rose'},
        {'label': 'Net Cash (Finance)',        'value': f'Rs. {net_cash:,.0f}',        'color': 'green'},
        {'label': 'Stock Profit',              'value': f'Rs. {stock_profit:,.0f}',    'color': 'violet'},
        {'label': 'Udhaar (Credit)',           'value': f'Rs. {udhaar:,.0f}',          'color': 'amber', 'url': 'web:udhaar'},
        {'label': f'Invoices ({period_label})','value': period_invoices.count(),       'color': 'blue'},
        {'label': 'Devices In Stock',          'value': devices_stock,                 'color': 'violet'},
        {'label': 'Open Repairs',              'value': open_repairs,                  'color': 'amber'},
        {'label': 'Open Transfers',            'value': transfers_open,                'color': 'cyan'},
        {'label': 'Overdue Plans',             'value': overdue_plans,                 'color': 'cyan'},
    ]

    # Quick links to the main sections (replaces the old dashboard tables).
    quick_links = [
        {'label': 'Point of Sale', 'icon': '🧾', 'url': 'web:pos'},
        {'label': 'Procurement',   'icon': '🚚', 'url': 'web:procurement_add'},
        {'label': 'Transfers',     'icon': '🔁', 'url': 'web:transfers'},
        {'label': 'Finance',       'icon': '💵', 'url': 'web:expenses'},
        {'label': 'Stock',         'icon': '📦', 'url': 'web:products'},
        {'label': 'Repairs',       'icon': '🔧', 'url': 'web:repairs'},
    ]

    return render(request, 'web/dashboard.html', _ctx('dashboard',
        title='Dashboard', kpis=kpis, quick_links=quick_links,
        periods=periods, period=period, period_label=period_label))


# ── Hub ───────────────────────────────────────────────────────────────────────

@login_required(login_url='web:login')
def hub(request, key):
    section = SECTIONS.get(key)
    return render(request, 'web/hub.html', _ctx(key,
        section=section, title=section['label'] if section else 'Section'))


@login_required(login_url='web:login')
def stock(request):       return hub(request, 'stock')
@login_required(login_url='web:login')
def selling(request):     return hub(request, 'selling')
@login_required(login_url='web:login')
def workshop(request):    return hub(request, 'workshop')
@login_required(login_url='web:login')
def procurement(request): return hub(request, 'procurement')
@login_required(login_url='web:login')
def finance(request):     return hub(request, 'finance')


# ── Products (full catalog CRUD over the Product model) ───────────────────────

@login_required(login_url='web:login')
def products(request):
    from apps.inventory.models import Product
    qs = Product.objects.order_by('name')
    q   = request.GET.get('q', '')
    low = request.GET.get('low', '')
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(sku__icontains=q) | Q(brand__icontains=q) | Q(category__icontains=q))
    if low:
        qs = qs.filter(stock_qty__lte=F('reorder_level'))
    return render(request, 'web/products.html', _ctx('stock',
        title='Products', products=qs[:300], q=q, low=low, total=qs.count()))


@login_required(login_url='web:login')
def product_add(request):
    # Products are only added via Procurement
    return redirect('web:procurement_add')


@login_required(login_url='web:login')
def product_edit(request, pk):
    # Products are only restocked via Procurement
    return redirect('web:procurement_add')


# ── Stock — Barcode Labels ────────────────────────────────────────────────────

@login_required(login_url='web:login')
def labels(request):
    """Generate printable price/barcode labels for products (barcode = SKU)."""
    from apps.inventory.models import Product
    products = Product.objects.exclude(sku='').order_by('name')
    selected = None
    sel_id = request.GET.get('product')
    try:
        qty = int(request.GET.get('qty') or 0)
    except ValueError:
        qty = 0
    qty = max(0, min(qty, 100))          # cap to keep the print sane
    if sel_id:
        selected = Product.objects.filter(pk=sel_id).first()
    label_range = range(qty) if selected and qty else []
    return render(request, 'web/labels.html', _ctx('stock',
        title='Barcode Labels', products=products, selected=selected,
        qty=qty, label_range=label_range))


# ── POS (session-cart across products, IMEI units & spare parts) ──────────────
#
# Cart items are typed dicts: {'type': 'product'|'unit'|'spare', 'id', 'name',
# 'sku', 'imei', 'price'(str), 'qty'}. The key (type:id) makes each stock kind
# addressable so checkout can deduct from the right model.

def _pos_cart(request):
    cart = request.session.get('pos_cart', [])
    # Drop legacy carts saved under the old {'product_id': ...} schema.
    if any('type' not in i for i in cart):
        cart = []
        request.session['pos_cart'] = []
        request.session.modified = True
    return cart


def _cart_key(i):
    return f"{i['type']}:{i['id']}"


def _pos_totals(cart):
    from decimal import Decimal
    total = Decimal('0')
    count = 0
    for i in cart:
        total += Decimal(str(i['price'])) * i['qty']
        count += i['qty']
    return total, count


def _spare_stock_qs():
    """SparePart queryset annotated with ledger-derived stock."""
    from django.db.models import Sum, OuterRef, Subquery, Value, IntegerField
    from django.db.models.functions import Coalesce
    from apps.spare_parts.models import SparePart, SparePartLedger
    ledger = (SparePartLedger.objects.filter(part=OuterRef('pk'))
              .values('part').annotate(s=Sum('qty')).values('s'))
    return SparePart.objects.annotate(
        stock=Coalesce(Subquery(ledger, output_field=IntegerField()),
                       Value(0, output_field=IntegerField())))


@login_required(login_url='web:login')
def pos(request):
    from decimal import Decimal
    from apps.inventory.models import Product, Unit
    q = request.GET.get('q', '')

    cart = _pos_cart(request)
    cart_keys = {_cart_key(i) for i in cart}

    def mk(t, pk, name, sku, price, stock, low=False, brand='', imei=''):
        return {'type': t, 'id': pk, 'name': name, 'sku': sku or '',
                'price': price, 'stock': stock, 'low': low, 'brand': brand,
                'imei': imei, 'in_cart': f'{t}:{pk}' in cart_keys}

    sections = []

    # 1) Products / accessories — one section per category.
    pq = Product.objects.filter(stock_qty__gt=0).order_by('category', 'name')
    if q:
        pq = pq.filter(Q(name__icontains=q) | Q(sku__icontains=q) | Q(brand__icontains=q))
    by_cat = {}
    for p in pq[:400]:
        by_cat.setdefault(p.category or 'Uncategorized', []).append(
            mk('product', p.pk, p.name, p.sku, p.sell_price, p.stock_qty,
               low=(p.stock_qty <= p.reorder_level), brand=p.brand))
    for cat in sorted(by_cat, key=str.lower):
        sections.append({'title': cat, 'items': by_cat[cat]})

    # 2) IMEI devices — each in-stock unit is individually sellable.
    uq = Unit.objects.filter(lifecycle_state='in_stock').order_by('brand', 'model')
    if q:
        uq = uq.filter(Q(imei1__icontains=q) | Q(brand__icontains=q) | Q(model__icontains=q))
    units = [mk('unit', u.pk, f'{u.brand} {u.model}'.strip(), u.imei1, u.sell_price, 1,
                brand=u.brand, imei=u.imei1) for u in uq[:400]]
    if units:
        sections.append({'title': 'IMEI Devices', 'items': units})

    # 3) Spare parts — ledger-derived stock.
    sq = _spare_stock_qs().filter(stock__gt=0).order_by('name')
    if q:
        sq = sq.filter(Q(name__icontains=q) | Q(sku__icontains=q) | Q(brand_compat__icontains=q))
    spares = [mk('spare', s.pk, s.name, s.sku, s.sell_price, s.stock,
                 low=(s.stock <= s.reorder_level), brand=s.brand_compat) for s in sq[:400]]
    if spares:
        sections.append({'title': 'Spare Parts', 'items': spares})

    total, count = _pos_totals(cart)
    cart_view = [{**i, 'line_total': Decimal(str(i['price'])) * i['qty']} for i in cart]
    categories = [s['title'] for s in sections]

    return render(request, 'web/pos.html', _ctx('pos',
        title='Point of Sale',
        q=q, categories=categories, sections=sections,
        cart=cart_view, cart_total=total, cart_count=count,
    ))


@login_required(login_url='web:login')
@require_POST
def pos_add(request):
    from apps.inventory.models import Product, Unit
    from apps.spare_parts.models import SparePart
    t = request.POST.get('type', 'product')
    pid = request.POST.get('id') or request.POST.get('product_id')
    cart = _pos_cart(request)
    key = f'{t}:{pid}'

    for i in cart:
        if _cart_key(i) == key:
            if t != 'unit':          # a unit is unique — never stack qty
                i['qty'] += 1
            break
    else:
        if t == 'unit':
            u = get_object_or_404(Unit, pk=pid, lifecycle_state='in_stock')
            cart.append({'type': 'unit', 'id': u.pk, 'name': f'{u.brand} {u.model}'.strip(),
                         'sku': u.imei1, 'imei': u.imei1, 'price': str(u.sell_price), 'qty': 1})
        elif t == 'spare':
            s = get_object_or_404(SparePart, pk=pid)
            cart.append({'type': 'spare', 'id': s.pk, 'name': s.name, 'sku': s.sku,
                         'imei': '', 'price': str(s.sell_price), 'qty': 1})
        else:
            p = get_object_or_404(Product, pk=pid)
            cart.append({'type': 'product', 'id': p.pk, 'name': p.name, 'sku': p.sku,
                         'imei': '', 'price': str(p.sell_price), 'qty': 1})

    request.session['pos_cart'] = cart
    request.session.modified = True
    return redirect(request.META.get('HTTP_REFERER') or 'web:pos')


@login_required(login_url='web:login')
@require_POST
def pos_remove(request):
    key = f"{request.POST.get('type')}:{request.POST.get('id')}"
    cart = [i for i in _pos_cart(request) if _cart_key(i) != key]
    request.session['pos_cart'] = cart
    request.session.modified = True
    return redirect('web:pos')


@login_required(login_url='web:login')
@require_POST
def pos_clear(request):
    request.session['pos_cart'] = []
    request.session.modified = True
    return redirect('web:pos')


@login_required(login_url='web:login')
@require_POST
def pos_checkout(request):
    from decimal import Decimal
    from django.db import transaction
    from apps.sales.models import Invoice, InvoiceLine
    from apps.inventory.models import Product, Unit, StockMovement
    from apps.spare_parts.models import SparePartLedger

    cart = _pos_cart(request)
    if not cart:
        return redirect('web:pos')

    customer_name = request.POST.get('customer_name') or 'Walk-in'
    customer_phone = (request.POST.get('customer_phone') or '').strip()
    method = request.POST.get('payment_method') or 'cash'
    subtotal, _ = _pos_totals(cart)

    # Customers are recorded automatically from the sale (no manual add).
    customer_obj = None
    cname = customer_name.strip()
    if cname and cname.lower() != 'walk-in':
        from apps.customers.models import Customer
        if customer_phone:
            customer_obj = Customer.objects.filter(phone=customer_phone).first()
        if not customer_obj:
            customer_obj = Customer.objects.filter(name__iexact=cname).first()
        if not customer_obj:
            customer_obj = Customer.objects.create(name=cname, phone=customer_phone)
        elif customer_phone and not customer_obj.phone:
            customer_obj.phone = customer_phone
            customer_obj.save(update_fields=['phone'])

    # Order-level discount (flat Rs.), clamped to [0, subtotal].
    try:
        discount = Decimal(str(request.POST.get('discount') or '0'))
    except Exception:
        discount = Decimal('0')
    discount = max(Decimal('0'), min(discount, subtotal))
    grand = subtotal - discount

    # Amount received now — blank means fully paid. Anything less is udhaar (credit).
    raw = request.POST.get('amount_received')
    if raw is None or str(raw).strip() == '':
        received = grand
    else:
        try:
            received = Decimal(str(raw))
        except Exception:
            received = grand
    received = max(Decimal('0'), min(received, grand))
    status = 'paid' if received >= grand else 'partially_paid'

    with transaction.atomic():
        inv = Invoice.objects.create(
            customer=customer_obj, customer_name=customer_name, status=status,
            subtotal=subtotal, discount_amount=discount,
            grand_total=grand, amount_paid=received,
            payment_method=method, created_by=request.user,
        )
        for i in cart:
            price = Decimal(str(i['price']))
            qty = i['qty']
            t = i['type']

            if t == 'unit':
                InvoiceLine.objects.create(
                    invoice=inv, product_type='unit', product_id=i['id'],
                    product_name=i['name'], sku=i.get('sku', ''), imei=i.get('imei', ''),
                    qty=1, unit_price=price, line_total=price,
                )
                Unit.objects.filter(pk=i['id'], lifecycle_state='in_stock').update(
                    lifecycle_state='sold')

            elif t == 'spare':
                InvoiceLine.objects.create(
                    invoice=inv, product_type='spare_part', product_id=i['id'],
                    product_name=i['name'], sku=i.get('sku', ''), qty=qty,
                    unit_price=price, line_total=price * qty,
                )
                SparePartLedger.objects.create(
                    part_id=i['id'], entry_type='sale', qty=-qty,
                    reference=inv.invoice_number, actor=request.user, note='POS sale',
                )

            else:  # product / accessory
                InvoiceLine.objects.create(
                    invoice=inv, product_type='accessory', product_id=i['id'],
                    product_name=i['name'], sku=i.get('sku', ''), qty=qty,
                    unit_price=price, line_total=price * qty,
                )
                Product.objects.filter(pk=i['id']).update(stock_qty=F('stock_qty') - qty)
                StockMovement.objects.create(
                    product_id=i['id'], type='sale', qty_change=-qty,
                    note=f'Sale via {inv.invoice_number}', actor=request.user,
                )

    request.session['pos_cart'] = []
    request.session.modified = True
    return redirect('web:invoice_detail', pk=inv.pk)


# ── Stock — Devices ───────────────────────────────────────────────────────────

@login_required(login_url='web:login')
def devices(request):
    from apps.inventory.models import Unit
    qs = Unit.objects.select_related('branch', 'added_by').order_by('-created_at')
    q  = request.GET.get('q', '')
    state = request.GET.get('state', '')
    if q:
        qs = qs.filter(Q(imei1__icontains=q) | Q(brand__icontains=q) | Q(model__icontains=q))
    if state:
        qs = qs.filter(lifecycle_state=state)
    states = Unit.LIFECYCLE
    return render(request, 'web/devices.html', _ctx('stock',
        title='IMEI Devices', units=qs[:100], q=q, state=state, states=states,
        total=qs.count()))


@login_required(login_url='web:login')
def device_detail(request, pk):
    from apps.inventory.models import Unit
    unit = get_object_or_404(Unit, pk=pk)
    return render(request, 'web/device_detail.html', _ctx('stock',
        title=f'{unit.brand} {unit.model}', unit=unit))


@login_required(login_url='web:login')
def device_add(request):
    # Devices are only added via Procurement (IMEI category)
    return redirect('web:procurement_add')


# ── Stock — Accessories ────────────────────────────────────────────────────────

@login_required(login_url='web:login')
def accessories(request):
    from apps.inventory.models import Product
    qs = Product.objects.select_related('branch').order_by('name')
    q  = request.GET.get('q', '')
    low = request.GET.get('low', '')
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(sku__icontains=q))
    if low:
        qs = qs.filter(stock_qty__lte=F('reorder_level'))
    return render(request, 'web/accessories.html', _ctx('stock',
        title='Accessories', products=qs[:200], q=q, low=low, total=qs.count()))


@login_required(login_url='web:login')
def accessory_add(request):
    # Accessories are only added via Procurement
    return redirect('web:procurement_add')


# ── Sales — Invoices ──────────────────────────────────────────────────────────

@login_required(login_url='web:login')
def invoices(request):
    from apps.sales.models import Invoice
    qs = Invoice.objects.select_related('customer', 'branch', 'created_by').order_by('-created_at')
    q      = request.GET.get('q', '')
    status = request.GET.get('status', '')
    if q:
        qs = qs.filter(Q(invoice_number__icontains=q) | Q(customer_name__icontains=q))
    if status:
        qs = qs.filter(status=status)
    statuses = Invoice.STATUS
    return render(request, 'web/invoices.html', _ctx('selling',
        title='Invoices', invoices=qs[:100], q=q, status=status, statuses=statuses))


@login_required(login_url='web:login')
def udhaar(request):
    """Outstanding credit — pending invoices and repair balances to collect."""
    from apps.sales.models import Invoice
    from apps.repairs.models import RepairJob
    q = request.GET.get('q', '')
    invoices = (Invoice.objects.filter(status='partially_paid')
                .select_related('customer').order_by('-created_at'))
    repairs = (RepairJob.objects.exclude(status='cancelled')
               .filter(final_cost__gt=F('amount_paid')).order_by('-created_at'))
    if q:
        invoices = invoices.filter(Q(invoice_number__icontains=q) |
                                   Q(customer_name__icontains=q) |
                                   Q(customer__phone__icontains=q))
        repairs = repairs.filter(Q(job_number__icontains=q) |
                                 Q(customer_name__icontains=q) |
                                 Q(customer_phone__icontains=q))
    inv_total = invoices.aggregate(t=Sum('balance_due'))['t'] or 0
    repairs = list(repairs)
    for r in repairs:
        r.balance = (r.final_cost or 0) - (r.amount_paid or 0)
    rep_total = sum(r.balance for r in repairs)
    return render(request, 'web/udhaar.html', _ctx('selling',
        title='Udhaar (Credit)', invoices=invoices, repairs=repairs, q=q,
        inv_total=inv_total, rep_total=rep_total, total=inv_total + rep_total))


@login_required(login_url='web:login')
def invoice_detail(request, pk):
    from apps.sales.models import Invoice
    from apps.settings_app.models import CompanySettings
    inv = get_object_or_404(Invoice.objects.prefetch_related('lines', 'payments'), pk=pk)
    lines = list(inv.lines.all())
    for l in lines:
        l.remaining = l.qty - (l.returned_qty or 0)   # units still returnable
    company, _ = CompanySettings.objects.get_or_create(id=1)
    return render(request, 'web/invoice_detail.html', _ctx('selling',
        title=f'Invoice {inv.invoice_number}', inv=inv, lines=lines, company=company))


@login_required(login_url='web:login')
@require_POST
def invoice_status_update(request, pk):
    """Admin sets an invoice as Paid or Pending (with amount received)."""
    from decimal import Decimal
    from apps.sales.models import Invoice
    inv = get_object_or_404(Invoice, pk=pk)
    choice = request.POST.get('pay_status')

    if choice == 'paid':
        inv.amount_paid = inv.grand_total
        inv.status = 'paid'
    elif choice == 'pending':
        raw = request.POST.get('amount_paid')
        if raw not in (None, ''):
            try:
                inv.amount_paid = max(Decimal('0'), min(Decimal(str(raw)), inv.grand_total))
            except Exception:
                pass
        inv.status = 'paid' if inv.amount_paid >= inv.grand_total else 'partially_paid'

    inv.save()   # recomputes balance_due
    return redirect('web:invoice_detail', pk=inv.pk)


@login_required(login_url='web:login')
@require_POST
def invoice_line_return(request, line_id):
    """Return some/all of one invoice line back into stock."""
    from django.db import transaction
    from apps.sales.models import InvoiceLine
    from apps.inventory.models import Product, Unit, StockMovement
    from apps.spare_parts.models import SparePartLedger

    line = get_object_or_404(InvoiceLine.objects.select_related('invoice'), pk=line_id)
    remaining = line.qty - (line.returned_qty or 0)
    try:
        want = int(request.POST.get('qty') or remaining)
    except (TypeError, ValueError):
        want = remaining
    qty = max(0, min(want, remaining))
    if not qty or not line.product_id:
        return redirect('web:invoice_detail', pk=line.invoice_id)

    inv = line.invoice
    with transaction.atomic():
        if line.product_type == 'unit':
            # A serialized device — put the specific unit back in stock.
            Unit.objects.filter(pk=line.product_id, lifecycle_state='sold').update(
                lifecycle_state='in_stock')
        elif line.product_type == 'spare_part':
            SparePartLedger.objects.create(
                part_id=line.product_id, entry_type='return_in', qty=qty,
                reference=inv.invoice_number, actor=request.user,
                note='Customer return')
        else:  # product / accessory
            Product.objects.filter(pk=line.product_id).update(
                stock_qty=F('stock_qty') + qty)
            StockMovement.objects.create(
                product_id=line.product_id, type='return', qty_change=qty,
                note=f'Return via {inv.invoice_number}', actor=request.user)

        line.returned_qty = (line.returned_qty or 0) + qty
        line.save(update_fields=['returned_qty'])

        # If every line is fully returned, mark the invoice returned.
        if all((l.returned_qty or 0) >= l.qty for l in inv.lines.all()):
            inv.status = 'returned'
            inv.save(update_fields=['status', 'updated_at'])

    return redirect('web:invoice_detail', pk=line.invoice_id)


# ── Sales — Customers ─────────────────────────────────────────────────────────

@login_required(login_url='web:login')
def customers(request):
    from apps.customers.models import Customer
    qs = Customer.objects.order_by('name')
    q  = request.GET.get('q', '')
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(phone__icontains=q) | Q(cnic__icontains=q))
    return render(request, 'web/customers.html', _ctx('selling',
        title='Customers', customers=qs[:200], q=q))


@login_required(login_url='web:login')
def customer_detail(request, pk):
    from apps.customers.models import Customer
    from apps.sales.models import Invoice
    cust    = get_object_or_404(Customer, pk=pk)
    invoices= Invoice.objects.filter(customer=cust).order_by('-created_at')[:20]
    ledger  = cust.ledger.order_by('-created_at')[:30]
    return render(request, 'web/customer_detail.html', _ctx('selling',
        title=cust.name, cust=cust, invoices=invoices, ledger=ledger))


@login_required(login_url='web:login')
def customer_add(request):
    # Customers are recorded automatically when an invoice is generated —
    # there is no manual "add customer" flow.
    return redirect('web:customers')


# ── Workshop — Repairs ────────────────────────────────────────────────────────

@login_required(login_url='web:login')
def repairs(request):
    from apps.repairs.models import RepairJob
    # Completed/terminal jobs live in History; everything else is Active.
    HISTORY = ['delivered', 'cancelled', 'unrepairable']
    base = RepairJob.objects.select_related('customer', 'technician', 'branch')
    q   = request.GET.get('q', '')
    tab = request.GET.get('tab', 'active')
    if tab != 'history':
        tab = 'active'

    qs = base.order_by('-created_at')
    if q:
        qs = qs.filter(Q(job_number__icontains=q) | Q(customer_name__icontains=q) | Q(device_model__icontains=q))
    qs = qs.filter(status__in=HISTORY) if tab == 'history' else qs.exclude(status__in=HISTORY)

    active_count  = base.exclude(status__in=HISTORY).count()
    history_count = base.filter(status__in=HISTORY).count()
    return render(request, 'web/repairs.html', _ctx('workshop',
        title='Repair Jobs', jobs=qs[:200], q=q, tab=tab,
        active_count=active_count, history_count=history_count))


@login_required(login_url='web:login')
def repair_detail(request, pk):
    from apps.repairs.models import RepairJob
    from apps.users.models import User
    job = get_object_or_404(RepairJob.objects.prefetch_related('logs', 'parts'), pk=pk)
    job.balance = (job.final_cost or 0) - (job.amount_paid or 0)
    technicians = User.objects.filter(is_active=True)
    return render(request, 'web/repair_detail.html', _ctx('workshop',
        title=f'Job {job.job_number}', job=job,
        technicians=technicians, statuses=RepairJob.STATUS))


@login_required(login_url='web:login')
@require_POST
def repair_update(request, pk):
    """Update a repair job — status, diagnosis, costing & payment (with udhaar)."""
    from decimal import Decimal
    from apps.repairs.models import RepairJob, RepairStatusLog
    job = get_object_or_404(RepairJob, pk=pk)
    p = request.POST

    def dec(val, current):
        try:
            return Decimal(str(val))
        except Exception:
            return current

    old_status = job.status
    job.status      = p.get('status') or job.status
    job.diagnosis   = p.get('diagnosis', job.diagnosis)
    job.final_cost  = dec(p.get('final_cost'), job.final_cost)
    job.amount_paid = dec(p.get('amount_paid'), job.amount_paid)
    tech = p.get('technician')
    job.technician_id = int(tech) if tech else None
    job.save()

    note = (p.get('note') or '').strip()
    if job.status != old_status or note:
        RepairStatusLog.objects.create(
            repair=job, status=job.status, note=note, actor=request.user)

    return redirect('web:repair_detail', pk=job.pk)


@login_required(login_url='web:login')
def repair_new(request):
    from apps.repairs.models import RepairJob
    from apps.branches.models import Branch
    from apps.users.models import User
    error = ''
    if request.method == 'POST':
        p = request.POST
        try:
            job = RepairJob.objects.create(
                customer_id=p.get('customer') or None,
                customer_name=p['customer_name'],
                customer_phone=p.get('customer_phone', ''),
                device_model=p['device_model'],
                device_imei=p.get('device_imei', ''),
                fault_description=p['fault_description'],
                branch_id=p.get('branch') or None,
                technician_id=p.get('technician') or None,
                estimated_cost=p.get('estimated_cost') or 0,
                created_by=request.user,
            )
            return redirect('web:repair_detail', pk=job.pk)
        except Exception as e:
            error = str(e)
    branches    = Branch.objects.filter(is_active=True)
    technicians = User.objects.filter(is_active=True)
    return render(request, 'web/repair_form.html', _ctx('workshop',
        title='New Repair Job', branches=branches, technicians=technicians, error=error))


# ── Procurement — Purchases ───────────────────────────────────────────────────

@login_required(login_url='web:login')
def purchases(request):
    from apps.purchases.models import PurchaseOrder
    qs = PurchaseOrder.objects.select_related('supplier', 'branch').order_by('-created_at')
    q      = request.GET.get('q', '')
    status = request.GET.get('status', '')
    if q:
        qs = qs.filter(Q(order_number__icontains=q) | Q(supplier__name__icontains=q))
    if status:
        qs = qs.filter(status=status)
    statuses = PurchaseOrder.STATUS
    return render(request, 'web/purchases.html', _ctx('procurement',
        title='Purchase Orders', orders=qs[:100], q=q, status=status, statuses=statuses))


@login_required(login_url='web:login')
def purchase_detail(request, pk):
    from apps.purchases.models import PurchaseOrder
    order = get_object_or_404(PurchaseOrder.objects.prefetch_related('lines'), pk=pk)
    return render(request, 'web/purchase_detail.html', _ctx('procurement',
        title=f'PO {order.order_number}', order=order))


# ── Procurement — Suppliers ───────────────────────────────────────────────────

@login_required(login_url='web:login')
def suppliers(request):
    from apps.suppliers.models import Supplier
    qs = Supplier.objects.annotate(
        spend=Sum('procurements__total'),
        purchases=Count('procurements', distinct=True),
    ).order_by('name')
    q  = request.GET.get('q', '')
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(phone__icontains=q))
    return render(request, 'web/suppliers.html', _ctx('procurement',
        title='Suppliers', suppliers=qs[:200], q=q))


@login_required(login_url='web:login')
def supplier_add(request):
    from apps.suppliers.models import Supplier
    error = ''
    if request.method == 'POST':
        p = request.POST
        name = (p.get('name') or '').strip()
        if not name:
            error = 'Supplier name is required.'
        elif Supplier.objects.filter(name__iexact=name).exists():
            error = 'A supplier with this name already exists.'
        else:
            Supplier.objects.create(
                name=name, company=p.get('company', ''), phone=p.get('phone', ''),
                email=p.get('email', ''), address=p.get('address', ''),
                notes=p.get('notes', ''),
            )
            return redirect('web:suppliers')
    return render(request, 'web/supplier_form.html', _ctx('procurement',
        title='Add Supplier', error=error))


@login_required(login_url='web:login')
def supplier_detail(request, pk):
    from apps.suppliers.models import Supplier
    sup   = get_object_or_404(Supplier, pk=pk)
    procs = sup.procurements.select_related('supplier').order_by('-date', '-id')[:100]
    total_spend = sup.procurements.aggregate(t=Sum('total'))['t'] or 0
    return render(request, 'web/supplier_detail.html', _ctx('procurement',
        title=sup.name, supplier=sup, procurements=procs,
        total_spend=total_spend, purchase_count=procs.count()))


@login_required(login_url='web:login')
def supplier_edit(request, pk):
    from apps.suppliers.models import Supplier
    sup = get_object_or_404(Supplier, pk=pk)
    error = ''
    if request.method == 'POST':
        p = request.POST
        name = (p.get('name') or '').strip()
        if not name:
            error = 'Supplier name is required.'
        elif Supplier.objects.filter(name__iexact=name).exclude(pk=sup.pk).exists():
            error = 'Another supplier already uses this name.'
        else:
            sup.name    = name
            sup.company = p.get('company', '')
            sup.phone   = p.get('phone', '')
            sup.email   = p.get('email', '')
            sup.address = p.get('address', '')
            sup.notes   = p.get('notes', '')
            sup.save()
            return redirect('web:supplier_detail', pk=sup.pk)
    return render(request, 'web/supplier_form.html', _ctx('procurement',
        title=f'Edit {sup.name}', supplier=sup, mode='edit', error=error))


# ── Procurement — Transfers ───────────────────────────────────────────────────

@login_required(login_url='web:login')
def transfers(request):
    from apps.transfers.models import Transfer
    qs = Transfer.objects.select_related('from_branch', 'to_branch').order_by('-created_at')
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')
    if q:
        qs = qs.filter(Q(transfer_number__icontains=q) |
                       Q(from_branch__name__icontains=q) |
                       Q(to_branch__name__icontains=q))
    if status:
        qs = qs.filter(status=status)
    return render(request, 'web/transfers.html', _ctx('procurement',
        title='Transfers', transfers=qs[:100], q=q, status=status, statuses=Transfer.STATUS))


@login_required(login_url='web:login')
def transfer_add(request):
    from apps.transfers.models import Transfer
    from apps.branches.models import Branch
    branches = Branch.objects.order_by('name')
    error = ''
    if request.method == 'POST':
        p = request.POST
        fb, tb = p.get('from_branch'), p.get('to_branch')
        if not fb or not tb:
            error = 'Select both the source and destination branch.'
        elif fb == tb:
            error = 'From and To branches must be different.'
        else:
            Transfer.objects.create(
                from_branch_id=fb, to_branch_id=tb,
                status=p.get('status') or 'draft',
                notes=p.get('notes', ''),
                created_by=request.user,
            )
            return redirect('web:transfers')
    return render(request, 'web/transfer_form.html', _ctx('procurement',
        title='New Transfer', branches=branches, statuses=Transfer.STATUS, error=error))


# ── Finance — Cash & Expenses ─────────────────────────────────────────────────

@login_required(login_url='web:login')
def expenses(request):
    from apps.cash.models import Expense, CashSession
    qs = Expense.objects.select_related('branch').order_by('-expense_date')
    q = request.GET.get('q', '')
    category = request.GET.get('category', '')
    if q:
        qs = qs.filter(Q(description__icontains=q) | Q(reference__icontains=q))
    if category:
        qs = qs.filter(category=category)
    sess = CashSession.objects.filter(status='open').first()
    total = qs.aggregate(t=Sum('amount'))['t'] or 0   # total of the filtered view
    today = timezone.now().date()
    today_total = Expense.objects.filter(expense_date=today).aggregate(t=Sum('amount'))['t'] or 0
    return render(request, 'web/expenses.html', _ctx('finance',
        title='Cash & Expenses', expenses=qs[:100], active_session=sess, total=total,
        today_total=today_total, categories=Expense.CATEGORIES, today=today,
        q=q, sel_category=category))


@login_required(login_url='web:login')
@require_POST
def expense_add(request):
    from decimal import Decimal
    from apps.cash.models import Expense
    p = request.POST
    try:
        amount = Decimal(str(p.get('amount') or '0'))
    except Exception:
        amount = Decimal('0')
    description = (p.get('description') or '').strip()
    if amount > 0 and description:
        Expense.objects.create(
            category=p.get('category') or 'other',
            amount=amount,
            description=description,
            reference=(p.get('reference') or '').strip(),
            expense_date=p.get('expense_date') or timezone.now().date(),
            created_by=request.user,
        )
    return redirect('web:expenses')


# ── Settings ──────────────────────────────────────────────────────────────────

@login_required(login_url='web:login')
def settings_page(request):
    from apps.settings_app.models import CompanySettings
    from apps.users.models import User
    from apps.branches.models import Branch
    company, _ = CompanySettings.objects.get_or_create(id=1)
    users    = User.objects.order_by('username')[:30]
    branches = Branch.objects.order_by('name')
    return render(request, 'web/settings.html', _ctx('settings',
        title='Settings', company=company, users=users, branches=branches,
        can_edit=request.user.is_superuser,
        restored=request.GET.get('restored'), restore_error=request.GET.get('restore_error')))


@login_required(login_url='web:login')
@require_POST
def company_save(request):
    """Admin edits company profile — incl. the shop location printed on bills."""
    from apps.settings_app.models import CompanySettings
    if not request.user.is_superuser:
        return redirect('web:settings')
    company, _ = CompanySettings.objects.get_or_create(id=1)
    p = request.POST
    company.name           = (p.get('name') or company.name).strip()
    company.phone          = p.get('phone', '').strip()
    company.email          = p.get('email', '').strip()
    company.address        = p.get('address', '').strip()
    company.ntn            = p.get('ntn', '').strip()
    company.receipt_footer = p.get('receipt_footer', '').strip()
    if request.FILES.get('logo'):
        company.logo = request.FILES['logo']
    elif p.get('remove_logo'):
        company.logo.delete(save=False)
        company.logo = None
    company.save()
    return redirect('web:settings')


@login_required(login_url='web:login')
def backup_download(request):
    """Download a full backup (database + uploaded media) as a zip — save it to USB."""
    import io, os, zipfile, sqlite3, tempfile
    from django.conf import settings as dj_settings
    from django.core.management import call_command
    from django.http import HttpResponse

    if not request.user.is_superuser:
        return redirect('web:settings')

    stamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        db = dj_settings.DATABASES['default']
        if 'sqlite' in db['ENGINE'] and os.path.exists(db['NAME']):
            # Consistent snapshot via SQLite's online backup API.
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.sqlite3')
            tmp.close()
            src, dst = sqlite3.connect(db['NAME']), sqlite3.connect(tmp.name)
            with dst:
                src.backup(dst)
            src.close(); dst.close()
            z.write(tmp.name, 'db.sqlite3')
            os.unlink(tmp.name)
        else:
            # Non-SQLite: a portable JSON data dump.
            out = io.StringIO()
            call_command('dumpdata', '--natural-primary', '--natural-foreign',
                         '-e', 'contenttypes', '-e', 'auth.permission', stdout=out)
            z.writestr('data.json', out.getvalue())

        media = str(dj_settings.MEDIA_ROOT)
        if os.path.isdir(media):
            for root, _, files in os.walk(media):
                for f in files:
                    fp = os.path.join(root, f)
                    z.write(fp, os.path.join('media', os.path.relpath(fp, media)))

    buf.seek(0)
    resp = HttpResponse(buf.getvalue(), content_type='application/zip')
    resp['Content-Disposition'] = f'attachment; filename="backup_{stamp}.zip"'
    return resp


@login_required(login_url='web:login')
@require_POST
def restore_backup(request):
    """Restore records from a previously downloaded backup .zip (overwrites data)."""
    import os, zipfile, sqlite3, tempfile
    from django.conf import settings as dj_settings
    from django.db import connections
    from django.core.management import call_command
    from django.urls import reverse

    if not request.user.is_superuser:
        return redirect('web:settings')

    f = request.FILES.get('backup')
    if not f:
        return redirect(f"{reverse('web:settings')}?restore_error=Choose+a+backup+file+first.")
    try:
        z = zipfile.ZipFile(f)
    except zipfile.BadZipFile:
        return redirect(f"{reverse('web:settings')}?restore_error=Not+a+valid+backup+zip.")

    names = z.namelist()
    db = dj_settings.DATABASES['default']
    try:
        if 'sqlite' in db['ENGINE'] and 'db.sqlite3' in names:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.sqlite3')
            tmp.write(z.read('db.sqlite3'))
            tmp.close()
            # Sanity-check the uploaded DB before touching the live one.
            chk = sqlite3.connect(tmp.name)
            chk.execute("SELECT count(*) FROM sqlite_master")
            chk.close()
            connections.close_all()          # release the live DB handle
            src, dst = sqlite3.connect(tmp.name), sqlite3.connect(db['NAME'])
            with dst:
                src.backup(dst)              # overwrite live DB, lock-safe
            src.close(); dst.close(); os.unlink(tmp.name)
        elif 'data.json' in names:
            tmpj = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
            tmpj.write(z.read('data.json'))
            tmpj.close()
            call_command('loaddata', tmpj.name)
            os.unlink(tmpj.name)
        else:
            return redirect(f"{reverse('web:settings')}?restore_error=Backup+has+no+database.")

        # Restore uploaded media files.
        media = str(dj_settings.MEDIA_ROOT)
        for n in names:
            if n.startswith('media/') and not n.endswith('/'):
                target = os.path.join(media, n[len('media/'):])
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with open(target, 'wb') as out:
                    out.write(z.read(n))
    except Exception as e:
        return redirect(f"{reverse('web:settings')}?restore_error=Restore+failed:+{str(e)[:80]}")

    return redirect(f"{reverse('web:settings')}?restored=1")


@login_required(login_url='web:login')
@require_POST
def user_edit(request, pk):
    """Admin renames a user (updates full_name + first/last so it shows everywhere)."""
    from apps.users.models import User
    if not request.user.is_superuser:
        return redirect('web:settings')
    user = get_object_or_404(User, pk=pk)
    name = (request.POST.get('full_name') or '').strip()
    parts = name.split(' ', 1)
    user.full_name  = name
    user.first_name = parts[0] if parts and parts[0] else ''
    user.last_name  = parts[1] if len(parts) > 1 else ''
    user.save(update_fields=['full_name', 'first_name', 'last_name'])
    return redirect('web:settings')


# ── Spare Parts ───────────────────────────────────────────────────────────────

@login_required(login_url='web:login')
def spare_parts(request):
    from apps.spare_parts.models import SparePart
    from django.db.models import Sum, OuterRef, Subquery, Value, IntegerField
    from django.db.models.functions import Coalesce
    from apps.spare_parts.models import SparePartLedger

    ledger_sum = (
        SparePartLedger.objects.filter(part=OuterRef('pk'))
        .values('part').annotate(s=Sum('qty')).values('s')
    )
    qs = SparePart.objects.annotate(
        stock_level=Coalesce(Subquery(ledger_sum, output_field=IntegerField()), Value(0, output_field=IntegerField()))
    ).order_by('category', 'name')

    category = request.GET.get('category', '')
    q        = request.GET.get('q', '')
    if category:
        qs = qs.filter(category=category)
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(sku__icontains=q) | Q(brand_compat__icontains=q))

    categories = SparePart.Category.choices
    return render(request, 'web/spare_parts.html', _ctx('stock',
        title='Spare Parts', parts=qs[:200], categories=categories,
        active_cat=category, q=q))


@login_required(login_url='web:login')
def spare_part_detail(request, pk):
    from apps.spare_parts.models import SparePart
    part   = get_object_or_404(SparePart, pk=pk)
    ledger = part.ledger.select_related('actor').order_by('-created_at')[:50]
    stock  = part.ledger.aggregate(s=Sum('qty'))['s'] or 0
    return render(request, 'web/spare_part_detail.html', _ctx('stock',
        title=part.name, part=part, ledger=ledger, stock=stock))


# ══ Procurement ════════════════════════════════════════════════════════════════

@login_required(login_url='web:login')
def procurement_list(request):
    from apps.procurement.models import Procurement
    qs = Procurement.objects.select_related('supplier').order_by('-date', '-id')
    q = request.GET.get('q', '')
    if q:
        qs = qs.filter(Q(invoice_no__icontains=q) | Q(supplier__name__icontains=q))
    return render(request, 'web/procurement_list.html', _ctx('procurement',
        title='Procurement', procurements=qs[:100], q=q))


@login_required(login_url='web:login')
def procurement_detail(request, pk):
    from apps.procurement.models import Procurement
    proc = get_object_or_404(Procurement.objects.select_related('supplier'), pk=pk)
    return render(request, 'web/procurement_detail.html', _ctx('procurement',
        title=f'Procurement #{proc.pk}', proc=proc, items=proc.items.all()))


def _existing_catalog():
    """Names + SKUs of everything already in stock — feeds the procurement
    autocomplete so the admin selects an existing item instead of creating a
    near-duplicate."""
    from apps.inventory.models import Product
    from apps.spare_parts.models import SparePart
    rows = list(Product.objects.values('name', 'sku'))
    rows += list(SparePart.objects.values('name', 'sku'))
    return rows


@login_required(login_url='web:login')
def procurement_add(request):
    from django.db import transaction
    from apps.procurement.models import Procurement
    from apps.procurement.forms import ProcurementForm, ProcurementItemFormSet
    from apps.procurement.stock_sync import apply_procurement

    # Clear the running "added this session" list.
    if request.GET.get('clear'):
        request.session.pop('recent_procurements', None)
        return redirect('web:procurement_add')

    if request.method == 'POST':
        form = ProcurementForm(request.POST)
        formset = ProcurementItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                proc = form.save(commit=False)
                proc.created_by = request.user
                proc.save()
                formset.instance = proc
                formset.save()
                apply_procurement(proc, request.user)   # auto-create/update stock
            # Remember it, then Post/Redirect/Get back to a fresh form so the
            # admin can keep adding — the just-saved entries show in a list below.
            recent = request.session.get('recent_procurements', [])
            recent.insert(0, proc.pk)
            request.session['recent_procurements'] = recent[:10]
            return redirect('web:procurement_add')
    else:
        form = ProcurementForm()
        formset = ProcurementItemFormSet()

    recent_ids = request.session.get('recent_procurements', [])
    recent = list(Procurement.objects.filter(pk__in=recent_ids)
                  .select_related('supplier').prefetch_related('items'))
    recent.sort(key=lambda p: recent_ids.index(p.pk))   # keep newest-first order
    return render(request, 'web/procurement_form.html', _ctx('procurement',
        title='New Procurement', form=form, formset=formset, mode='add',
        existing_catalog=_existing_catalog(), recent=recent))


@login_required(login_url='web:login')
def procurement_edit(request, pk):
    from django.db import transaction
    from apps.procurement.models import Procurement
    from apps.procurement.forms import ProcurementForm, ProcurementItemFormSet
    from apps.procurement.stock_sync import apply_procurement, reverse_procurement

    proc = get_object_or_404(Procurement, pk=pk)
    if request.method == 'POST':
        form = ProcurementForm(request.POST, instance=proc)
        formset = ProcurementItemFormSet(request.POST, instance=proc)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                reverse_procurement(proc, request.user)   # undo old stock effect
                form.save()
                formset.save()                            # apply edits / adds / deletes
                proc.refresh_from_db()
                apply_procurement(proc, request.user)     # re-apply new stock effect
            return redirect('web:procurement_detail', pk=proc.pk)
    else:
        form = ProcurementForm(instance=proc)
        formset = ProcurementItemFormSet(instance=proc)
    return render(request, 'web/procurement_form.html', _ctx('procurement',
        title=f'Edit Procurement #{proc.pk}', form=form, formset=formset, mode='edit', proc=proc,
        existing_catalog=_existing_catalog()))


@login_required(login_url='web:login')
@require_POST
def procurement_delete(request, pk):
    from django.db import transaction
    from apps.procurement.models import Procurement
    from apps.procurement.stock_sync import reverse_procurement

    proc = get_object_or_404(Procurement, pk=pk)
    with transaction.atomic():
        reverse_procurement(proc, request.user)   # reverse stock, then delete
        proc.delete()
    return redirect('web:procurement_list')
