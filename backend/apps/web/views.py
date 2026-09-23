from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q, F, Count
from django.views.decorators.http import require_POST
from django.utils import timezone

from apps.inventory.search import word_search, PRODUCT_FIELDS, UNIT_FIELDS, SPARE_FIELDS

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

PERIODS = [('today', 'Today'), ('week', 'Weekly'), ('month', 'Monthly'), ('year', 'Yearly')]


def _period(request):
    """(key, start date, label, choices) for the ?period= selector."""
    from datetime import timedelta
    today = timezone.localdate()
    period = request.GET.get('period', 'today')
    if period == 'week':
        start, label = today - timedelta(days=6), 'This Week'
    elif period == 'month':
        start, label = today.replace(day=1), 'This Month'
    elif period == 'year':
        start, label = today.replace(month=1, day=1), 'This Year'
    else:
        period, start, label = 'today', today, 'Today'
    return period, start, label, PERIODS


@login_required(login_url='web:login')
def dashboard(request):
    from apps.sales.models import Invoice
    from apps.repairs.models import RepairJob
    from apps.inventory.models import Product, Unit
    from apps.installments.models import InstallmentPlan

    from django.db.models import DecimalField, ExpressionWrapper
    from apps.cash.models import Expense
    from .profit import profit_summary

    today = timezone.now().date()
    period, start, period_label, periods = _period(request)

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

    net_profit = profit_summary(start)['net_profit']

    # ── Current-state snapshots (independent of the period) ───────────────────

    open_repairs  = RepairJob.objects.exclude(status__in=['delivered', 'cancelled']).count()
    devices_stock = Unit.objects.filter(lifecycle_state='in_stock').count()
    overdue_plans = InstallmentPlan.objects.filter(status='active', next_due_date__lt=today).count()
    low_stock = Product.objects.filter(stock_qty__lte=F('reorder_level')).count()
    low_spares = _spare_stock_qs().filter(stock__lte=F('reorder_level')).count()

    kpis = [
        {'label': f'Sales ({period_label})',   'value': f'Rs. {total_sales:,.0f}',    'color': 'rose'},
        {'label': 'Cash Received',            'value': f'Rs. {cash_received:,.0f}',   'color': 'green'},
        {'label': 'Repairs Income',           'value': f'Rs. {repair_income:,.0f}',   'color': 'blue'},
        {'label': 'Expenses',                 'value': f'Rs. {expenses_period:,.0f}', 'color': 'rose'},
        {'label': 'Net Cash (Finance)',        'value': f'Rs. {net_cash:,.0f}',        'color': 'green'},
        {'label': f'Net Profit ({period_label})', 'value': f'Rs. {net_profit:,.0f}', 'color': 'violet',
         'url': 'web:profit', 'query': f'?period={period}'},
        {'label': 'Udhaar (Credit)',           'value': f'Rs. {udhaar:,.0f}',          'color': 'amber', 'url': 'web:udhaar'},
        {'label': f'Invoices ({period_label})','value': period_invoices.count(),       'color': 'blue'},
        {'label': 'Devices In Stock',          'value': devices_stock,                 'color': 'violet'},
        {'label': 'Open Repairs',              'value': open_repairs,                  'color': 'amber'},
        {'label': 'Low Stock Items',           'value': low_stock,                     'color': 'rose', 'url': 'web:products', 'query': '?low=1'},
        {'label': 'Low Stock Spares',          'value': low_spares,                    'color': 'rose', 'url': 'web:spare_parts', 'query': '?low=1'},
        {'label': 'Overdue Plans',             'value': overdue_plans,                 'color': 'cyan'},
    ]

    # Quick links to the main sections (replaces the old dashboard tables).
    quick_links = [
        {'label': 'Point of Sale', 'icon': '🧾', 'url': 'web:pos'},
        {'label': 'Purchases',     'icon': '🚚', 'url': 'web:procurement_add'},
        {'label': 'Invoices',      'icon': '📄', 'url': 'web:invoices'},
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

def stock_queryset(kind, params):
    """The filtered stock list for a page — shared by the page itself and its
    Excel export, so both always show the same items.
    kind: products | accessories | devices | spare_parts"""
    from apps.inventory.models import Product, Unit
    q = params.get('q', '')
    if kind in ('products', 'accessories'):
        qs = Product.objects.order_by('name')
        if kind == 'accessories':
            # Accessories = every non-serialised item except those filed as "Product".
            qs = qs.exclude(category__iexact='product')
        qs = word_search(qs, q, PRODUCT_FIELDS)
        if params.get('low'):
            qs = qs.filter(stock_qty__lte=F('reorder_level'))
        return qs
    if kind == 'devices':
        qs = word_search(Unit.objects.select_related('added_by').order_by('-created_at'), q, UNIT_FIELDS)
        if params.get('state'):
            qs = qs.filter(lifecycle_state=params['state'])
        return qs
    # spare parts — stock is derived from the ledger
    qs = _spare_stock_qs().annotate(stock_level=F('stock')).order_by('category', 'name')
    if params.get('category'):
        qs = qs.filter(category=params['category'])
    if params.get('low'):
        qs = qs.filter(stock_level__lte=F('reorder_level'))
    return word_search(qs, q, SPARE_FIELDS)


@login_required(login_url='web:login')
def stock_export(request, kind):
    """Excel sheet of the current stock list (same search / filters as the
    page) for sharing on WhatsApp. Cost prices are left out on purpose."""
    import io
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from django.http import Http404, HttpResponse
    from apps.settings_app.models import CompanySettings

    kind = kind.replace('-', '_')   # /stock/spare-parts/… or spare_parts
    titles = {'products': 'Product List', 'accessories': 'Accessories',
              'devices': 'Mobile Phones', 'spare_parts': 'Spare Parts'}
    if kind not in titles:
        raise Http404
    qs = stock_queryset(kind, request.GET)
    if kind == 'devices' and not request.GET.get('state'):
        qs = qs.filter(lifecycle_state='in_stock')   # share what can be sold

    if kind == 'devices':
        headers = ['Brand', 'Model', 'IMEI', 'Condition', 'PTA Status', 'Price (Rs.)']
        rows = [[u.brand, u.model, u.imei1, u.condition, u.pta_status, float(u.sell_price)] for u in qs]
    elif kind == 'spare_parts':
        headers = ['Part', 'SKU', 'Category', 'Compatible With', 'Price (Rs.)', 'In Stock']
        rows = [[p.name, p.sku, p.get_category_display(),
                 ' · '.join(x for x in (p.brand_compat, p.model_compat) if x),
                 float(p.sell_price), p.stock_level] for p in qs]
    else:
        headers = ['Item', 'SKU', 'Brand', 'Category', 'Price (Rs.)', 'In Stock']
        rows = [[p.name, p.sku, p.brand, p.category, float(p.sell_price), p.stock_qty] for p in qs]

    company = CompanySettings.objects.first()
    shop = company.name if company else 'My Phone'
    wb = Workbook()
    ws = wb.active
    ws.title = titles[kind][:31]
    ws.append([shop])
    ws.append([f"{titles[kind]} — {timezone.localtime().strftime('%d %b %Y')}"])
    ws.append([])
    ws.append(headers)
    for r in rows:
        ws.append(r)
    ws['A1'].font = Font(bold=True, size=14)
    ws['A2'].font = Font(italic=True, color='555555')
    head_fill = PatternFill('solid', fgColor='E11D48')
    for cell in ws[4]:
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = head_fill
        cell.alignment = Alignment(horizontal='center')
    price_col = headers.index('Price (Rs.)') + 1
    for (cell,) in ws.iter_rows(min_row=5, min_col=price_col, max_col=price_col):
        cell.number_format = '#,##0'
    for i, h in enumerate(headers, start=1):
        width = max([len(str(h))] + [len(str(r[i - 1])) for r in rows[:500]]) + 2
        ws.column_dimensions[ws.cell(row=4, column=i).column_letter].width = min(width, 45)
    ws.freeze_panes = 'A5'

    buf = io.BytesIO()
    wb.save(buf)
    import re
    safe_shop = re.sub(r'[^A-Za-z0-9 _-]+', '', shop).strip() or 'Shop'
    name = f"{safe_shop} - {titles[kind]} {timezone.localtime().strftime('%Y-%m-%d')}.xlsx"
    resp = HttpResponse(buf.getvalue(),
                        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    resp['Content-Disposition'] = f'attachment; filename="{name}"'
    return resp


@login_required(login_url='web:login')
def stock_export_svg(request, kind):
    """The current stock list drawn as one SVG image (price-list style) — the
    format sent on WhatsApp. Same search / filters as the page; no costs."""
    from xml.sax.saxutils import escape
    from django.http import Http404, HttpResponse
    from apps.settings_app.models import CompanySettings

    kind = kind.replace('-', '_')
    titles = {'products': 'Product List', 'accessories': 'Accessories',
              'devices': 'Mobile Phones', 'spare_parts': 'Spare Parts'}
    if kind not in titles:
        raise Http404
    qs = stock_queryset(kind, request.GET)
    if kind == 'devices':
        if not request.GET.get('state'):
            qs = qs.filter(lifecycle_state='in_stock')
        rows = [(f'{u.brand} {u.model}', f'IMEI {u.imei1} · {u.condition} · {u.pta_status}', u.sell_price, '')
                for u in qs]
    elif kind == 'spare_parts':
        rows = [(p.name, ' · '.join(x for x in (p.get_category_display(), p.brand_compat, p.model_compat) if x),
                 p.sell_price, f'{p.stock_level} in stock') for p in qs]
    else:
        rows = [(p.name, ' · '.join(x for x in (p.brand, p.category) if x), p.sell_price,
                 f'{p.stock_qty} in stock') for p in qs]

    company = CompanySettings.objects.first()
    shop = company.name if company else 'My Phone'
    brand = {'blue': '#2563eb', 'emerald': '#059669', 'violet': '#7c3aed',
             'orange': '#ea580c', 'teal': '#0d9488'}.get(getattr(company, 'theme', ''), '#e11d48')
    W, top, rh = 820, 150, 54
    H = top + max(1, len(rows)) * rh + 70

    def clip(text, n):
        text = str(text or '')
        return escape(text if len(text) <= n else text[:n - 1] + '…')

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'font-family="Segoe UI, Arial, sans-serif">',
           f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
           f'<rect width="{W}" height="104" fill="{brand}"/>',
           f'<text x="30" y="50" font-size="30" font-weight="800" fill="#fff">{clip(shop, 40)}</text>',
           f'<text x="30" y="84" font-size="18" fill="#fff">{escape(titles[kind])} — '
           f'{timezone.localtime().strftime("%d %b %Y")}</text>',
           '<text x="30" y="134" font-size="14" font-weight="700" fill="#6b7280">ITEM</text>',
           f'<text x="{W - 30}" y="134" font-size="14" font-weight="700" fill="#6b7280" text-anchor="end">PRICE</text>']
    for i, (name, sub, price, stock) in enumerate(rows):
        y = top + i * rh
        if i % 2 == 0:
            out.append(f'<rect x="0" y="{y}" width="{W}" height="{rh}" fill="#f9fafb"/>')
        out.append(f'<text x="30" y="{y + 23}" font-size="18" font-weight="700" fill="#111827">{clip(name, 48)}</text>')
        out.append(f'<text x="30" y="{y + 43}" font-size="13" fill="#6b7280">{clip(sub, 80)}</text>')
        out.append(f'<text x="{W - 30}" y="{y + 25}" font-size="19" font-weight="800" fill="{brand}" '
                   f'text-anchor="end">Rs. {price:,.0f}</text>')
        if stock:
            out.append(f'<text x="{W - 30}" y="{y + 44}" font-size="12" fill="#6b7280" text-anchor="end">{escape(stock)}</text>')
    if not rows:
        out.append(f'<text x="30" y="{top + 30}" font-size="16" fill="#6b7280">No items.</text>')
    out.append(f'<text x="{W / 2}" y="{H - 25}" font-size="12" fill="#9ca3af" text-anchor="middle">'
               f'{len(rows)} items · Prices subject to change · Developed by Devnest</text>')
    out.append('</svg>')

    import re
    safe_shop = re.sub(r'[^A-Za-z0-9 _-]+', '', shop).strip() or 'Shop'
    name = f"{safe_shop} - {titles[kind]} {timezone.localtime().strftime('%Y-%m-%d')}.svg"
    resp = HttpResponse('\n'.join(out), content_type='image/svg+xml; charset=utf-8')
    resp['Content-Disposition'] = f'attachment; filename="{name}"'
    return resp


@login_required(login_url='web:login')
def products(request):
    qs = stock_queryset('products', request.GET)
    q   = request.GET.get('q', '')
    low = request.GET.get('low', '')
    return render(request, 'web/products.html', _ctx('stock',
        title='Products', products=qs[:300], q=q, low=low, total=qs.count()))


@login_required(login_url='web:login')
def product_add(request):
    # Products are only added via Procurement
    return redirect('web:procurement_add')


def _decimal(raw, current):
    """POSTed money field → Decimal, falling back to the stored value."""
    from decimal import Decimal, InvalidOperation
    try:
        return Decimal(str(raw).strip())
    except (InvalidOperation, AttributeError, TypeError, ValueError):
        return current


@login_required(login_url='web:login')
def product_edit(request, pk):
    """Edit a catalog item's details — name, prices and the low-stock alert.

    Stock quantity is deliberately read-only: quantities only ever move through
    Purchases, POS and returns, so they stay reconcilable with the ledger.
    """
    from apps.inventory.models import Product
    from apps.audit.models import AuditTrail
    from apps.audit.recorder import record_audit

    prod  = get_object_or_404(Product, pk=pk)
    error = ''
    if request.method == 'POST':
        p = request.POST
        name = (p.get('name') or '').strip()
        sku  = (p.get('sku') or '').strip()
        try:
            level = int(p.get('reorder_level') or 0)
        except ValueError:
            level = -1

        if not name:
            error = 'Product name is required.'
        elif not sku:
            error = 'SKU is required.'
        elif Product.objects.filter(sku__iexact=sku).exclude(pk=prod.pk).exists():
            error = 'Another product already uses this SKU.'
        elif level < 0:
            error = 'Low stock alert must be 0 or more.'
        else:
            before = {'cost_price': prod.cost_price, 'sell_price': prod.sell_price,
                      'reorder_level': prod.reorder_level}
            prod.name     = name
            prod.sku      = sku
            prod.brand    = (p.get('brand') or '').strip()
            prod.category = (p.get('category') or '').strip()
            prod.description = (p.get('description') or '').strip()
            prod.cost_price  = _decimal(p.get('cost_price'), prod.cost_price)
            prod.sell_price  = _decimal(p.get('sell_price'), prod.sell_price)
            prod.reorder_level = level
            prod.save()
            after = {'cost_price': prod.cost_price, 'sell_price': prod.sell_price,
                     'reorder_level': prod.reorder_level}
            if before != after:
                record_audit(
                    actor=request.user, action_type=AuditTrail.PRICE_ADJUSTMENT,
                    entity_type='Product', entity_id=prod.pk,
                    previous_values=before, new_values=after,
                    reason='Edited from the product page', request=request,
                )
            dest = 'web:accessories' if prod.category.lower() != 'product' else 'web:products'
            return redirect(dest)

    return render(request, 'web/product_form.html', _ctx('stock',
        title=f'Edit {prod.name}', product=prod, error=error))


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


def _back_to_pos(request):
    """Return to the POS page the action came from (keeps an active search)."""
    from django.utils.http import url_has_allowed_host_and_scheme
    ref = request.META.get('HTTP_REFERER', '')
    if ref and '/pos/' in ref and url_has_allowed_host_and_scheme(ref, allowed_hosts={request.get_host()}):
        return redirect(ref)
    return redirect('web:pos')


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


class OutOfStock(Exception):
    pass


def _available(kind, pk):
    """Current stock of a product / spare part / unit (unit: 1 if in stock)."""
    from apps.inventory.models import Product, Unit
    if kind == 'unit':
        return 1 if Unit.objects.filter(pk=pk, lifecycle_state='in_stock').exists() else 0
    if kind == 'spare':
        return _spare_stock_qs().filter(pk=pk).values_list('stock', flat=True).first() or 0
    return Product.objects.filter(pk=pk).values_list('stock_qty', flat=True).first() or 0


def _cost_of(kind, pk):
    """Current cost price of one unit / product / spare part (for profit)."""
    from apps.inventory.models import Product, Unit
    from apps.spare_parts.models import SparePart
    model = {'unit': Unit, 'spare': SparePart}.get(kind, Product)
    return model.objects.filter(pk=pk).values_list('cost_price', flat=True).first() or 0


def _take_stock(kind, pk, qty, name, reference, user, reason='sale'):
    """Deduct stock inside the caller's transaction; raises OutOfStock if short.
    reason: 'sale', 'repair_use' or 'transfer_out'."""
    from apps.inventory.models import Product, Unit, StockMovement
    from apps.spare_parts.models import SparePartLedger
    if kind == 'unit':
        new_state = 'transferred' if reason == 'transfer_out' else 'sold'
        if not Unit.objects.filter(pk=pk, lifecycle_state='in_stock').update(lifecycle_state=new_state):
            raise OutOfStock(f'"{name}" is no longer in stock.')
        return
    if kind == 'spare':
        have = _available('spare', pk)
        if have < qty:
            raise OutOfStock(f'Only {have} of "{name}" in stock (needed {qty}).')
        SparePartLedger.objects.create(part_id=pk, entry_type=reason, qty=-qty,
                                       reference=reference, actor=user)
        return
    product = Product.objects.select_for_update().filter(pk=pk).first()
    if product is None or product.stock_qty < qty:
        have = product.stock_qty if product else 0
        raise OutOfStock(f'Only {have} of "{name}" in stock (needed {qty}).')
    product.stock_qty -= qty
    product.save(update_fields=['stock_qty', 'updated_at'])
    StockMovement.objects.create(product=product, type=reason, qty_change=-qty,
                                 note=reference, actor=user)


def _return_stock(kind, pk, qty, reference, user, reason='return'):
    """Put stock back (customer return, part removed from a repair, or a
    cancelled transfer — reason 'transfer_in')."""
    from apps.inventory.models import Product, Unit, StockMovement
    from apps.spare_parts.models import SparePartLedger
    if kind == 'unit':
        was = 'transferred' if reason == 'transfer_in' else 'sold'
        Unit.objects.filter(pk=pk, lifecycle_state=was).update(lifecycle_state='in_stock')
    elif kind == 'spare':
        entry = 'transfer_in' if reason == 'transfer_in' else 'return_in'
        SparePartLedger.objects.create(part_id=pk, entry_type=entry, qty=qty,
                                       reference=reference, actor=user)
    else:
        Product.objects.filter(pk=pk).update(stock_qty=F('stock_qty') + qty)
        StockMovement.objects.create(product_id=pk, type=reason, qty_change=qty,
                                     note=reference, actor=user)


@login_required(login_url='web:login')
def pos(request):
    from decimal import Decimal
    from apps.inventory.models import Product, Unit
    from apps.settings_app.choices import options
    q = request.GET.get('q', '')

    cart = _pos_cart(request)
    cart_qty = {_cart_key(i): i['qty'] for i in cart}

    def mk(t, pk, name, sku, price, stock, low=False, brand='', imei=''):
        return {'type': t, 'id': pk, 'name': name, 'sku': sku or '',
                'price': price, 'stock': stock, 'low': low, 'brand': brand,
                'imei': imei, 'in_cart': cart_qty.get(f'{t}:{pk}', 0)}

    sections = []

    # 1) Products / accessories — one section per category.
    pq = Product.objects.filter(stock_qty__gt=0).order_by('category', 'name')
    if q:
        pq = word_search(pq, q, PRODUCT_FIELDS)
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
        uq = word_search(uq, q, UNIT_FIELDS)
    units = [mk('unit', u.pk, f'{u.brand} {u.model}'.strip(), u.imei1, u.sell_price, 1,
                brand=u.brand, imei=u.imei1) for u in uq[:400]]
    if units:
        sections.append({'title': 'IMEI Devices', 'items': units})

    # 3) Spare parts — ledger-derived stock.
    sq = _spare_stock_qs().filter(stock__gt=0).order_by('name')
    if q:
        sq = word_search(sq, q, SPARE_FIELDS)
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
        payment_options=options('payment_method') or ['Cash'],
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
                if i['qty'] < _available(t, pid):
                    i['qty'] += 1
                else:
                    from django.contrib import messages
                    messages.warning(request, f'No more "{i["name"]}" in stock.')
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
    return _back_to_pos(request)


@login_required(login_url='web:login')
@require_POST
def pos_update(request):
    """Set a cart line's quantity and price (bulk / wholesale sales)."""
    from decimal import Decimal, InvalidOperation
    from django.contrib import messages
    key = f"{request.POST.get('type')}:{request.POST.get('id')}"
    cart = _pos_cart(request)
    for i in cart:
        if _cart_key(i) != key:
            continue
        if i['type'] != 'unit':
            try:
                qty = int(request.POST.get('qty') or i['qty'])
            except ValueError:
                qty = i['qty']
            step = request.POST.get('step')
            if step in ('1', '-1'):      # − / + buttons
                qty = i['qty'] + int(step)
            if qty < 1:                  # "−" on the last one removes the line
                cart.remove(i)
                break
            have = _available(i['type'], i['id'])
            if qty > have:
                messages.warning(request, f'Only {have} of "{i["name"]}" in stock.')
                qty = max(1, have)
            i['qty'] = qty
        try:
            price = Decimal(str(request.POST.get('price')))
            if price >= 0:
                i['price'] = str(price)
        except (InvalidOperation, ValueError):
            pass
        break
    request.session['pos_cart'] = cart
    request.session.modified = True
    return _back_to_pos(request)


@login_required(login_url='web:login')
@require_POST
def pos_add_imeis(request):
    """Add many IMEI devices at once — paste or scan one IMEI per line."""
    from django.contrib import messages
    from apps.inventory.models import Unit
    cart = _pos_cart(request)
    in_cart = {_cart_key(i) for i in cart}
    raw = request.POST.get('imeis', '')
    imeis = list(dict.fromkeys(x.strip() for x in raw.replace(',', '\n').splitlines() if x.strip()))
    added, missing = 0, []
    for imei in imeis:
        u = Unit.objects.filter(Q(imei1=imei) | Q(imei2=imei), lifecycle_state='in_stock').first()
        if not u:
            missing.append(imei)
        elif f'unit:{u.pk}' not in in_cart:
            cart.append({'type': 'unit', 'id': u.pk, 'name': f'{u.brand} {u.model}'.strip(),
                         'sku': u.imei1, 'imei': u.imei1, 'price': str(u.sell_price), 'qty': 1})
            in_cart.add(f'unit:{u.pk}')
            added += 1
    request.session['pos_cart'] = cart
    request.session.modified = True
    if added:
        messages.success(request, f'Added {added} device(s) to the cart.')
    if missing:
        messages.error(request, 'Not in stock / not found: ' + ', '.join(missing))
    return _back_to_pos(request)


@login_required(login_url='web:login')
@require_POST
def pos_remove(request):
    key = f"{request.POST.get('type')}:{request.POST.get('id')}"
    cart = [i for i in _pos_cart(request) if _cart_key(i) != key]
    request.session['pos_cart'] = cart
    request.session.modified = True
    return _back_to_pos(request)


@login_required(login_url='web:login')
@require_POST
def pos_clear(request):
    request.session['pos_cart'] = []
    request.session.modified = True
    return _back_to_pos(request)


@login_required(login_url='web:login')
@require_POST
def pos_checkout(request):
    from decimal import Decimal
    from django.db import transaction
    from apps.sales.models import Invoice, InvoiceLine

    cart = _pos_cart(request)
    if not cart:
        return redirect('web:pos')

    customer_name = request.POST.get('customer_name') or 'Walk-in'
    customer_phone = (request.POST.get('customer_phone') or '').strip()
    method = (request.POST.get('payment_method') or 'Cash').strip()[:50]
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

    line_types = {'unit': 'unit', 'spare': 'spare_part', 'product': 'accessory'}
    try:
        # All-or-nothing: if any line is short on stock, nothing is saved.
        with transaction.atomic():
            inv = Invoice.objects.create(
                customer=customer_obj, customer_name=customer_name, status=status,
                subtotal=subtotal, discount_amount=discount,
                grand_total=grand, amount_paid=received,
                payment_method=method, created_by=request.user,
            )
            for i in cart:
                price = Decimal(str(i['price']))
                qty = 1 if i['type'] == 'unit' else i['qty']
                InvoiceLine.objects.create(
                    invoice=inv, product_type=line_types[i['type']], product_id=i['id'],
                    product_name=i['name'], sku=i.get('sku', ''), imei=i.get('imei', ''),
                    qty=qty, unit_price=price, line_total=price * qty,
                    cost_price=_cost_of(i['type'], i['id']),
                )
                _take_stock(i['type'], i['id'], qty, i['name'],
                            f'Sale via {inv.invoice_number}', request.user)
    except OutOfStock as e:
        from django.contrib import messages
        messages.error(request, f'Sale not completed — {e}')
        return redirect('web:pos')

    request.session['pos_cart'] = []
    request.session.modified = True
    return redirect('web:invoice_detail', pk=inv.pk)


# ── Stock — Devices ───────────────────────────────────────────────────────────

@login_required(login_url='web:login')
def devices(request):
    from apps.inventory.models import Unit
    qs = stock_queryset('devices', request.GET)
    q  = request.GET.get('q', '')
    state = request.GET.get('state', '')
    states = Unit.LIFECYCLE
    return render(request, 'web/devices.html', _ctx('stock',
        title='IMEI Devices', units=qs[:100], q=q, state=state, states=states,
        total=qs.count()))


@login_required(login_url='web:login')
def device_detail(request, pk):
    from apps.inventory.models import Unit
    from apps.settings_app.choices import options
    unit = get_object_or_404(Unit, pk=pk)
    return render(request, 'web/device_detail.html', _ctx('stock',
        title=f'{unit.brand} {unit.model}', unit=unit,
        pta_options=options('pta_status', include=unit.pta_status),
        condition_options=options('device_condition', include=unit.condition)))


@login_required(login_url='web:login')
@require_POST
def device_update(request, pk):
    """Edit a device's PTA status, condition, price and extra identifiers."""
    from decimal import Decimal, InvalidOperation
    from django.contrib import messages
    from apps.inventory.models import Unit
    unit = get_object_or_404(Unit, pk=pk)
    p = request.POST
    unit.pta_status = (p.get('pta_status') or unit.pta_status).strip()[:50]
    unit.condition = (p.get('condition') or unit.condition).strip()[:50]
    unit.imei2 = (p.get('imei2') or '').strip() or None
    unit.serial = (p.get('serial') or '').strip()
    try:
        unit.sell_price = max(Decimal('0'), Decimal(str(p.get('sell_price'))))
    except (InvalidOperation, ValueError):
        pass
    unit.save()
    messages.success(request, 'Device updated.')
    return redirect('web:device_detail', pk=unit.pk)


@login_required(login_url='web:login')
def device_add(request):
    # Devices are only added via Procurement (IMEI category)
    return redirect('web:procurement_add')


# ── Stock — Accessories ────────────────────────────────────────────────────────

@login_required(login_url='web:login')
def accessories(request):
    qs = stock_queryset('accessories', request.GET)
    q  = request.GET.get('q', '')
    low = request.GET.get('low', '')
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
    qs = Invoice.objects.select_related('customer', 'created_by').order_by('-created_at')
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
        title=f'Invoice {inv.invoice_number}', inv=inv, lines=lines, company=company,
        receipt=_invoice_receipt(inv, lines), token_copies=TOKEN_COPIES))


# Tokens print twice on one slip: one for the customer, one kept by the shop.
TOKEN_COPIES = ['CUSTOMER COPY', 'SHOP COPY']


def _invoice_receipt(inv, lines):
    """Data for the printed bill (web/_receipt.html)."""
    meta = [('Invoice #', inv.invoice_number),
            ('Date', timezone.localtime(inv.created_at).strftime('%d-%m-%Y %I:%M %p')),
            ('Customer', inv.customer_name or 'Walk-in')]
    if inv.customer and inv.customer.phone:
        meta.append(('Phone', inv.customer.phone))
    rows = [{'name': l.product_name,
             'sub': f'IMEI {l.imei}' if l.imei else (l.sku or ''),
             'qty': l.qty, 'rate': l.unit_price, 'amount': l.line_total} for l in lines]
    totals = [{'label': 'Subtotal', 'value': inv.subtotal}]
    if inv.discount_amount:
        totals.append({'label': 'Discount', 'value': inv.discount_amount, 'minus': True})
    if inv.tax_amount:
        totals.append({'label': 'Tax', 'value': inv.tax_amount})
    totals += [{'label': 'TOTAL', 'value': inv.grand_total, 'strong': True},
               {'label': f'Paid ({inv.get_payment_method_display()})', 'value': inv.amount_paid}]
    if inv.balance_due > 0:
        totals.append({'label': 'Balance Due', 'value': inv.balance_due, 'alert': True})
    return {'title': 'SALE INVOICE', 'meta': meta, 'rows': rows, 'totals': totals, 'note': inv.notes}


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
    kind = {'unit': 'unit', 'spare_part': 'spare'}.get(line.product_type, 'product')
    with transaction.atomic():
        _return_stock(kind, line.product_id, qty, f'Return via {inv.invoice_number}', request.user)

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
    base = RepairJob.objects.select_related('customer', 'technician')
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
    from apps.inventory.models import Product
    from apps.settings_app.models import CompanySettings
    from apps.settings_app.choices import options
    job = get_object_or_404(RepairJob.objects.prefetch_related('logs', 'parts'), pk=pk)
    job.balance = (job.final_cost or 0) - (job.amount_paid or 0)
    technicians = User.objects.filter(is_active=True)
    # Stock the technician can pick from: spare parts first, then accessories.
    spares = _spare_stock_qs().filter(stock__gt=0, is_active=True).order_by('name')
    products = Product.objects.filter(stock_qty__gt=0).order_by('name')
    company, _ = CompanySettings.objects.get_or_create(id=1)
    meta = [('Job #', job.job_number),
            ('Date', timezone.localtime().strftime('%d-%m-%Y %I:%M %p')),
            ('Customer', job.customer_name)]
    if job.customer_phone:
        meta.append(('Phone', job.customer_phone))
    meta.append(('Device', job.device_model + (f' ({job.device_imei})' if job.device_imei else '')))
    rows = [{'name': 'Repair / labour charges', 'sub': job.diagnosis, 'qty': 1,
             'rate': job.labour_charge, 'amount': job.labour_charge}]
    rows += [{'name': p.name, 'sub': p.sku, 'qty': p.qty, 'rate': p.unit_price,
              'amount': p.line_total} for p in job.parts.all()]
    totals = [{'label': 'TOTAL', 'value': job.final_cost, 'strong': True},
              {'label': 'Paid', 'value': job.amount_paid}]
    if job.balance > 0:
        totals.append({'label': 'Balance Due', 'value': job.balance, 'alert': True})
    received = [a.strip() for a in (job.accessories_received or '').split(',') if a.strip()]
    if received:
        meta.append(('Received with', ', '.join(received)))
    receipt = {'title': 'REPAIR BILL', 'meta': meta, 'rows': rows, 'totals': totals}
    return render(request, 'web/repair_detail.html', _ctx('workshop',
        title=f'Job {job.job_number}', job=job, company=company, receipt=receipt,
        token_copies=TOKEN_COPIES, received=received,
        parts_cost=sum((pt.cost * pt.qty for pt in job.parts.all()), 0),
        repair_profit=job.labour_charge + sum((pt.line_total - pt.cost * pt.qty for pt in job.parts.all()), 0) - job.extra_cost,
        accessory_options=options('repair_accessory') + [a for a in received if a not in options('repair_accessory')],
        spares=spares, products=products,
        technicians=technicians, statuses=RepairJob.STATUS))


@login_required(login_url='web:login')
@require_POST
def repair_part_add(request, pk):
    """Take a spare part / product from stock and add it to the repair bill."""
    from decimal import Decimal, InvalidOperation
    from django.db import transaction
    from django.contrib import messages
    from apps.repairs.models import RepairJob, RepairPart
    from apps.inventory.models import Product
    from apps.spare_parts.models import SparePart
    job = get_object_or_404(RepairJob, pk=pk)

    kind, _, item_id = (request.POST.get('item') or '').partition(':')
    model = {'spare': SparePart, 'product': Product}.get(kind)
    if not model or not item_id.isdigit():
        messages.error(request, 'Choose a part from stock.')
        return redirect('web:repair_detail', pk=pk)
    item = get_object_or_404(model, pk=int(item_id))
    try:
        qty = max(1, int(request.POST.get('qty') or 1))
    except ValueError:
        qty = 1
    try:
        price = Decimal(str(request.POST.get('unit_price')))
    except (InvalidOperation, ValueError):
        price = item.sell_price
    if price < 0:
        price = item.sell_price

    try:
        with transaction.atomic():
            _take_stock(kind, item.pk, qty, item.name, job.job_number,
                        request.user, reason='repair_use')
            RepairPart.objects.create(
                repair=job, part_type=kind, part_id=item.pk, name=item.name,
                sku=item.sku, qty=qty, cost=item.cost_price, unit_price=price,
                added_by=request.user)
            job.recalc_total()
            job.save()
    except OutOfStock as e:
        messages.error(request, str(e))
    else:
        messages.success(request, f'Added {qty} × {item.name} to the repair (stock deducted).')
    return redirect('web:repair_detail', pk=pk)


@login_required(login_url='web:login')
@require_POST
def repair_part_remove(request, part_id):
    """Remove a part from the repair and return it to stock."""
    from django.db import transaction
    from django.contrib import messages
    from apps.repairs.models import RepairPart
    part = get_object_or_404(RepairPart.objects.select_related('repair'), pk=part_id)
    job = part.repair
    with transaction.atomic():
        if part.part_id:
            _return_stock(part.part_type, part.part_id, part.qty, job.job_number,
                          request.user, reason='repair_return')
        part.delete()
        job.recalc_total()
        job.save()
    messages.success(request, f'Removed {part.name}; {part.qty} returned to stock.')
    return redirect('web:repair_detail', pk=job.pk)


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
    job.labour_charge = dec(p.get('labour_charge'), job.labour_charge)
    job.amount_paid = dec(p.get('amount_paid'), job.amount_paid)
    job.extra_cost = max(Decimal('0'), dec(p.get('extra_cost'), job.extra_cost))
    job.recalc_total()
    if 'accessories_present' in p:           # checklist was on the form
        job.accessories_received = ', '.join(p.getlist('accessories'))
    tech = p.get('technician')
    job.technician_id = int(tech) if tech else None
    # Profit counts a repair when it is first finished (Ready / Delivered).
    if job.status in ('ready', 'delivered') and not job.completed_at:
        job.completed_at = timezone.now()
    job.save()

    note = (p.get('note') or '').strip()
    if job.status != old_status or note:
        RepairStatusLog.objects.create(
            repair=job, status=job.status, note=note, actor=request.user)

    return redirect('web:repair_detail', pk=job.pk)


@login_required(login_url='web:login')
def repair_new(request):
    from apps.repairs.models import RepairJob
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
                technician_id=p.get('technician') or None,
                estimated_cost=p.get('estimated_cost') or 0,
                accessories_received=', '.join(p.getlist('accessories')),
                created_by=request.user,
            )
            return redirect('web:repair_detail', pk=job.pk)
        except Exception as e:
            error = str(e)
    from apps.settings_app.choices import options
    technicians = User.objects.filter(is_active=True)
    return render(request, 'web/repair_form.html', _ctx('workshop',
        title='New Repair Job', technicians=technicians, error=error,
        accessory_options=options('repair_accessory')))


# ── Procurement — Purchases ───────────────────────────────────────────────────

@login_required(login_url='web:login')
def purchases(request):
    # Buying stock happens in one place: Purchases (procurement).
    return redirect('web:procurement_list')

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


# ── Send Stock Out (transfers to another shop / person) ──────────────────────

def _stock_choices():
    """Everything in stock, for the "which item" pickers: (value, label)."""
    from apps.inventory.models import Product, Unit
    phones = [(f'unit:{u.pk}', f'{u.brand} {u.model} — IMEI {u.imei1}', 1)
              for u in Unit.objects.filter(lifecycle_state='in_stock').order_by('brand', 'model')]
    products = [(f'product:{p.pk}', f'{p.name} ({p.sku})', p.stock_qty)
                for p in Product.objects.filter(stock_qty__gt=0).order_by('name')]
    spares = [(f'spare:{s.pk}', f'{s.name} ({s.sku})', s.stock)
              for s in _spare_stock_qs().filter(stock__gt=0).order_by('name')]
    return [('Mobile Phones', phones), ('Accessories & Products', products), ('Spare Parts', spares)]


@login_required(login_url='web:login')
def transfers(request):
    from apps.transfers.models import Transfer
    qs = Transfer.objects.prefetch_related('items').order_by('-created_at')
    q = request.GET.get('q', '')
    if q:
        qs = qs.filter(Q(transfer_number__icontains=q) | Q(recipient_name__icontains=q) |
                       Q(recipient_phone__icontains=q) | Q(destination__icontains=q) |
                       Q(items__item_name__icontains=q) | Q(items__imei__icontains=q)).distinct()
    return render(request, 'web/transfers.html', _ctx('procurement',
        title='Send Stock Out', transfers=qs[:200], q=q))


@login_required(login_url='web:login')
def transfer_add(request):
    """Send goods to another shop / person: who, where, which items, how many.
    Stock is deducted immediately (all-or-nothing)."""
    from django.db import transaction
    from django.contrib import messages
    from apps.transfers.models import Transfer, TransferItem
    from apps.inventory.models import Product, Unit
    from apps.spare_parts.models import SparePart
    error, p = '', request.POST
    if request.method == 'POST':
        rows = []
        for value, qty in zip(p.getlist('item'), p.getlist('qty')):
            kind, _, pk = (value or '').partition(':')
            if kind not in ('unit', 'product', 'spare') or not pk.isdigit():
                continue
            try:
                qty = 1 if kind == 'unit' else max(1, int(qty or 1))
            except ValueError:
                qty = 1
            rows.append((kind, int(pk), qty))
        if not (p.get('recipient_name') or '').strip():
            error = 'Enter who the goods are being sent to.'
        elif not (p.get('destination') or '').strip():
            error = 'Enter where the goods are being sent.'
        elif not rows:
            error = 'Add at least one item to send.'
        else:
            try:
                with transaction.atomic():
                    t = Transfer.objects.create(
                        recipient_name=p['recipient_name'].strip()[:150],
                        recipient_phone=(p.get('recipient_phone') or '').strip()[:30],
                        destination=p['destination'].strip()[:255],
                        notes=(p.get('notes') or '').strip(),
                        status='dispatched', dispatched_at=timezone.now(),
                        dispatched_by=request.user, created_by=request.user)
                    for kind, pk, qty in rows:
                        model = {'unit': Unit, 'spare': SparePart}.get(kind, Product)
                        obj = get_object_or_404(model, pk=pk)
                        name = f'{obj.brand} {obj.model}' if kind == 'unit' else obj.name
                        _take_stock(kind, pk, qty, name, f'Sent out {t.transfer_number}',
                                    request.user, reason='transfer_out')
                        TransferItem.objects.create(
                            transfer=t, item_type=kind, item_id=pk, item_name=name, qty=qty,
                            imei=getattr(obj, 'imei1', '') or '', sku=getattr(obj, 'sku', '') or '')
            except OutOfStock as e:
                error = str(e)
            else:
                messages.success(request, f'{t.transfer_number} saved — stock deducted.')
                return redirect('web:transfer_detail', pk=t.pk)
    return render(request, 'web/transfer_form.html', _ctx('procurement',
        title='Send Stock Out', choices=_stock_choices(), error=error, post=p))


@login_required(login_url='web:login')
def transfer_detail(request, pk):
    from apps.transfers.models import Transfer
    from apps.settings_app.models import CompanySettings
    t = get_object_or_404(Transfer.objects.prefetch_related('items'), pk=pk)
    company, _ = CompanySettings.objects.get_or_create(id=1)
    meta = [('Transfer #', t.transfer_number),
            ('Date', timezone.localtime(t.created_at).strftime('%d-%m-%Y %I:%M %p')),
            ('Sent to', t.recipient_name)]
    if t.recipient_phone:
        meta.append(('Phone', t.recipient_phone))
    meta.append(('Destination', t.destination))
    rows = [{'name': i.item_name, 'sub': f'IMEI {i.imei}' if i.imei else i.sku, 'qty': i.qty}
            for i in t.items.all()]
    slip = {'title': 'GOODS SENT OUT', 'meta': meta, 'rows': rows, 'note': t.notes,
            'total_qty': sum(i.qty for i in t.items.all())}
    return render(request, 'web/transfer_detail.html', _ctx('procurement',
        title=t.transfer_number, t=t, company=company, slip=slip))


@login_required(login_url='web:login')
@require_POST
def transfer_cancel(request, pk):
    """Goods came back / sending cancelled: return every item to stock."""
    from django.db import transaction
    from django.contrib import messages
    from apps.transfers.models import Transfer
    t = get_object_or_404(Transfer, pk=pk)
    if t.status == 'cancelled':
        return redirect('web:transfer_detail', pk=pk)
    with transaction.atomic():
        for i in t.items.all():
            _return_stock(i.item_type, i.item_id, i.qty, f'Cancelled {t.transfer_number}',
                          request.user, reason='transfer_in')
        t.status = 'cancelled'
        t.save(update_fields=['status', 'updated_at'])
    messages.success(request, f'{t.transfer_number} cancelled — items returned to stock.')
    return redirect('web:transfer_detail', pk=pk)


# ── Finance — Cash & Expenses ─────────────────────────────────────────────────

@login_required(login_url='web:login')
def profit(request):
    """Profit & Loss — real profit from phones, accessories, spare parts and
    repairs, minus expenses (see profit.py for the exact rules)."""
    from .profit import profit_summary, unsold_stock_margin
    period, start, period_label, periods = _period(request)
    return render(request, 'web/profit.html', _ctx('finance',
        title='Profit & Loss', p=profit_summary(start), stock_margin=unsold_stock_margin(),
        period=period, period_label=period_label, periods=periods))


@login_required(login_url='web:login')
def expenses(request):
    from apps.cash.models import Expense, CashSession
    qs = Expense.objects.order_by('-expense_date')
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

SETTINGS_UNLOCK_SECONDS = 30 * 60   # idle time before Developer Options lock again


def _settings_key_ok(key):
    """The Developer Options access key: the owner's own key if set, else the installation key."""
    from django.contrib.auth.hashers import check_password
    from apps.settings_app.models import CompanySettings
    from .activation import check_key
    company = CompanySettings.objects.first()
    if company and company.settings_key:
        return check_password((key or '').strip(), company.settings_key)
    return check_key(key)


def settings_key_required(view):
    """Settings needs the access key; unlocking lasts for the session
    until SETTINGS_UNLOCK_SECONDS of inactivity, Lock, or sign-out."""
    import time
    from functools import wraps
    from django.urls import reverse

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        at = request.session.get('settings_unlocked_at', 0)
        if time.time() - at > SETTINGS_UNLOCK_SECONDS:
            request.session.pop('settings_unlocked_at', None)
            # a form posted after the unlock expired returns to Developer Options
            nxt = request.get_full_path() if request.method == 'GET' else reverse('web:settings')
            return redirect(f"{reverse('web:settings_unlock')}?next={nxt}")
        request.session['settings_unlocked_at'] = time.time()   # sliding timeout
        return view(request, *args, **kwargs)
    return wrapper


@login_required(login_url='web:login')
def settings_unlock(request):
    import time
    from django.utils.http import url_has_allowed_host_and_scheme
    nxt = request.POST.get('next') or request.GET.get('next') or ''
    if not url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
        nxt = ''
    error = ''
    if request.method == 'POST':
        if _settings_key_ok(request.POST.get('key')):
            request.session['settings_unlocked_at'] = time.time()
            return redirect(nxt or 'web:settings')
        error = 'Wrong access key.'
    return render(request, 'web/settings_unlock.html', _ctx('settings',
        title='Enter Access Key', next=nxt, error=error))


@login_required(login_url='web:login')
@require_POST
def settings_lock(request):
    request.session.pop('settings_unlocked_at', None)
    return redirect('web:dashboard')


@login_required(login_url='web:login')
@settings_key_required
@require_POST
def theme_save(request):
    from django.contrib import messages
    from apps.settings_app.models import CompanySettings, THEMES
    theme = request.POST.get('theme')
    if request.user.is_superuser and theme in dict(THEMES):
        company, _ = CompanySettings.objects.get_or_create(id=1)
        company.theme = theme
        company.save(update_fields=['theme', 'updated_at'])
        messages.success(request, f'Theme changed to {dict(THEMES)[theme]}.')
    return redirect('web:settings')


@login_required(login_url='web:login')
@settings_key_required
@require_POST
def settings_key_save(request):
    """Owner changes the key that unlocks Settings."""
    from django.contrib import messages
    from django.contrib.auth.hashers import make_password
    from apps.settings_app.models import CompanySettings
    if not request.user.is_superuser:
        return redirect('web:settings')
    p = request.POST
    new, confirm = (p.get('new_key') or '').strip(), (p.get('confirm_key') or '').strip()
    if not _settings_key_ok(p.get('current_key')):
        messages.error(request, 'Current access key is wrong — key not changed.')
    elif len(new) < 4:
        messages.error(request, 'New access key must be at least 4 characters.')
    elif new != confirm:
        messages.error(request, 'New key and confirmation do not match.')
    else:
        company, _ = CompanySettings.objects.get_or_create(id=1)
        company.settings_key = make_password(new)
        company.save(update_fields=['settings_key', 'updated_at'])
        messages.success(request, 'Access key changed. Use the new key next time.')
    return redirect('web:settings')


@login_required(login_url='web:login')
@settings_key_required
@require_POST
def printing_save(request):
    """Owner picks the paper the bills are printed on."""
    from django.contrib import messages
    from apps.settings_app.models import CompanySettings, RECEIPT_PAPERS
    if request.user.is_superuser:
        company, _ = CompanySettings.objects.get_or_create(id=1)
        paper = request.POST.get('receipt_paper')
        if paper in dict(RECEIPT_PAPERS):
            company.receipt_paper = paper
        company.receipt_show_logo = bool(request.POST.get('receipt_show_logo'))
        company.bill_disclaimer = (request.POST.get('bill_disclaimer') or '').strip()
        company.save(update_fields=['receipt_paper', 'receipt_show_logo', 'bill_disclaimer', 'updated_at'])
        messages.success(request, 'Printing settings saved.')
    return redirect('web:settings')


@login_required(login_url='web:login')
@settings_key_required
@require_POST
def option_save(request):
    """Add / edit / delete one owner-editable dropdown option."""
    from django.contrib import messages
    from django.db import IntegrityError, transaction
    from apps.settings_app.models import ChoiceOption
    from apps.inventory.models import Unit
    from apps.procurement.models import ProcurementItem
    if not request.user.is_superuser:
        return redirect('web:settings')
    p = request.POST
    action = p.get('action')
    group = p.get('group')
    if group not in dict(ChoiceOption.GROUPS):
        return redirect('web:settings')
    label = (p.get('label') or '').strip()[:50]
    color = p.get('color') if p.get('color') in dict(ChoiceOption.COLORS) else 'gray'
    try:
        order = max(0, int(p.get('sort_order') or 0))
    except ValueError:
        order = 0
    # Existing records store the label, so a rename is carried over to them.
    renames = {'pta_status': [(Unit, 'pta_status'), (ProcurementItem, 'pta_status')],
               'device_condition': [(Unit, 'condition'), (ProcurementItem, 'condition')]}
    try:
        with transaction.atomic():
            if action == 'add':
                if not label:
                    messages.error(request, 'Enter a name for the new option.')
                    return redirect('web:settings')
                if not p.get('sort_order'):
                    last = ChoiceOption.objects.filter(group=group).order_by('-sort_order').first()
                    order = (last.sort_order + 1) if last else 0
                ChoiceOption.objects.create(group=group, label=label, color=color, sort_order=order)
                messages.success(request, f'Added "{label}".')
            else:
                opt = get_object_or_404(ChoiceOption, pk=p.get('id'), group=group)
                if action == 'delete':
                    if ChoiceOption.objects.filter(group=group, is_active=True).exclude(pk=opt.pk).count() == 0:
                        messages.error(request, 'Keep at least one active option.')
                        return redirect('web:settings')
                    opt.delete()
                    messages.success(request, f'Deleted "{opt.label}". Existing records keep their value.')
                else:
                    if not label:
                        messages.error(request, 'Option name cannot be empty.')
                        return redirect('web:settings')
                    old = opt.label
                    opt.label, opt.color, opt.sort_order = label, color, order
                    opt.is_active = bool(p.get('is_active'))
                    opt.save()
                    if old != label:
                        for model, field in renames.get(group, []):
                            model.objects.filter(**{field: old}).update(**{field: label})
                    messages.success(request, f'Saved "{label}".')
    except IntegrityError:
        messages.error(request, f'"{label}" already exists in this list.')
    from django.urls import reverse
    return redirect(reverse('web:settings') + '#options')


@login_required(login_url='web:login')
def backup_page(request):
    return render(request, 'web/backup.html', _ctx('backup',
        title='Settings', can_edit=request.user.is_superuser,
        restored=request.GET.get('restored'), restore_error=request.GET.get('restore_error')))


@login_required(login_url='web:login')
@settings_key_required
def settings_page(request):
    from apps.settings_app.models import CompanySettings
    from apps.users.models import User
    company, _ = CompanySettings.objects.get_or_create(id=1)
    users    = User.objects.order_by('username')[:30]
    from apps.settings_app.models import THEMES, RECEIPT_PAPERS, ChoiceOption
    option_groups = [
        {'key': key, 'label': label,
         'items': ChoiceOption.objects.filter(group=key).order_by('sort_order', 'id')}
        for key, label in ChoiceOption.GROUPS]
    return render(request, 'web/settings.html', _ctx('settings',
        title='Developer Options', company=company, users=users,
        themes=THEMES, papers=RECEIPT_PAPERS, option_groups=option_groups,
        option_colors=ChoiceOption.COLORS, can_edit=request.user.is_superuser))


@login_required(login_url='web:login')
@settings_key_required
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
        return redirect('web:backup')

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
        return redirect('web:backup')

    f = request.FILES.get('backup')
    if not f:
        return redirect(f"{reverse('web:backup')}?restore_error=Choose+a+backup+file+first.")
    try:
        z = zipfile.ZipFile(f)
    except zipfile.BadZipFile:
        return redirect(f"{reverse('web:backup')}?restore_error=Not+a+valid+backup+zip.")

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
            return redirect(f"{reverse('web:backup')}?restore_error=Backup+has+no+database.")

        # Restore uploaded media files.
        media = str(dj_settings.MEDIA_ROOT)
        for n in names:
            if n.startswith('media/') and not n.endswith('/'):
                target = os.path.join(media, n[len('media/'):])
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with open(target, 'wb') as out:
                    out.write(z.read(n))
    except Exception as e:
        return redirect(f"{reverse('web:backup')}?restore_error=Restore+failed:+{str(e)[:80]}")

    return redirect(f"{reverse('web:backup')}?restored=1")


@login_required(login_url='web:login')
@settings_key_required
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
    qs = stock_queryset('spare_parts', request.GET)
    category = request.GET.get('category', '')
    q        = request.GET.get('q', '')
    low      = request.GET.get('low', '')

    categories = SparePart.Category.choices
    return render(request, 'web/spare_parts.html', _ctx('stock',
        title='Spare Parts', parts=qs[:200], categories=categories,
        active_cat=category, q=q, low=low))


@login_required(login_url='web:login')
def spare_part_edit(request, pk):
    """Edit a spare part's details, prices and low-stock alert.

    Stock on hand stays ledger-derived and is not editable here."""
    from apps.spare_parts.models import SparePart
    from apps.audit.models import AuditTrail
    from apps.audit.recorder import record_audit

    part  = get_object_or_404(SparePart, pk=pk)
    error = ''
    if request.method == 'POST':
        p = request.POST
        name = (p.get('name') or '').strip()
        sku  = (p.get('sku') or '').strip()
        try:
            level = int(p.get('reorder_level') or 0)
        except ValueError:
            level = -1

        if not name:
            error = 'Part name is required.'
        elif not sku:
            error = 'SKU is required.'
        elif SparePart.objects.filter(sku__iexact=sku).exclude(pk=part.pk).exists():
            error = 'Another spare part already uses this SKU.'
        elif level < 0:
            error = 'Low stock alert must be 0 or more.'
        else:
            before = {'cost_price': part.cost_price, 'sell_price': part.sell_price,
                      'reorder_level': part.reorder_level}
            category = p.get('category') or part.category
            if category in dict(SparePart.Category.choices):
                part.category = category
            part.name = name
            part.sku  = sku
            part.brand_compat = (p.get('brand_compat') or '').strip()
            part.model_compat = (p.get('model_compat') or '').strip()
            part.description  = (p.get('description') or '').strip()
            part.cost_price   = _decimal(p.get('cost_price'), part.cost_price)
            part.sell_price   = _decimal(p.get('sell_price'), part.sell_price)
            part.reorder_level = level
            part.save()
            after = {'cost_price': part.cost_price, 'sell_price': part.sell_price,
                     'reorder_level': part.reorder_level}
            if before != after:
                record_audit(
                    actor=request.user, action_type=AuditTrail.PRICE_ADJUSTMENT,
                    entity_type='SparePart', entity_id=part.pk,
                    previous_values=before, new_values=after,
                    reason='Edited from the spare part page', request=request,
                )
            return redirect('web:spare_part_detail', pk=part.pk)

    stock = part.ledger.aggregate(s=Sum('qty'))['s'] or 0
    return render(request, 'web/spare_part_form.html', _ctx('stock',
        title=f'Edit {part.name}', part=part, stock=stock, error=error,
        categories=SparePart.Category.choices))


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
        # "+ Add Device / Accessory…" buttons pre-select the item category.
        cat = request.GET.get('category')
        valid = {'imei', 'accessory', 'spare_part', 'product'}
        formset = ProcurementItemFormSet(initial=[{'category': cat}] if cat in valid else None)

    recent_ids = request.session.get('recent_procurements', [])
    recent = list(Procurement.objects.filter(pk__in=recent_ids)
                  .select_related('supplier').prefetch_related('items'))
    recent.sort(key=lambda p: recent_ids.index(p.pk))   # keep newest-first order
    return render(request, 'web/procurement_form.html', _ctx('procurement',
        title='New Purchase', form=form, formset=formset, mode='add',
        existing_catalog=_existing_catalog(), recent=recent, **_device_options()))


def _device_options():
    """PTA / condition choices for the procurement 'add row' template."""
    from apps.settings_app.choices import options
    from apps.spare_parts.models import SparePart
    return {'pta_options': options('pta_status'),
            'condition_options': options('device_condition'),
            'spare_categories': SparePart.Category.choices}


@login_required(login_url='web:login')
def procurement_edit(request, pk):
    from django.db import transaction
    from apps.procurement.models import Procurement
    from apps.procurement.forms import ProcurementForm, ProcurementItemFormSet
    from django.contrib import messages
    from apps.procurement.stock_sync import (apply_procurement, reverse_procurement,
                                             affected_stock, check_no_negative_stock,
                                             StockConflict)

    proc = get_object_or_404(Procurement, pk=pk)
    if request.method == 'POST':
        form = ProcurementForm(request.POST, instance=proc)
        formset = ProcurementItemFormSet(request.POST, instance=proc)
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    before_p, before_s = affected_stock(proc)
                    reverse_procurement(proc, request.user)   # undo old stock effect
                    form.save()
                    formset.save()                            # apply edits / adds / deletes
                    proc.refresh_from_db()
                    apply_procurement(proc, request.user)     # re-apply new stock effect
                    after_p, after_s = affected_stock(proc)
                    check_no_negative_stock(before_p | after_p, before_s | after_s)
            except StockConflict as e:
                messages.error(request, f'Not saved — stock from this purchase was already sold: {e}.')
                return redirect('web:procurement_edit', pk=proc.pk)
            return redirect('web:procurement_detail', pk=proc.pk)
    else:
        form = ProcurementForm(instance=proc)
        formset = ProcurementItemFormSet(instance=proc)
    return render(request, 'web/procurement_form.html', _ctx('procurement',
        title=f'Edit Purchase #{proc.pk}', form=form, formset=formset, mode='edit', proc=proc,
        existing_catalog=_existing_catalog(), **_device_options()))


@login_required(login_url='web:login')
@require_POST
def procurement_delete(request, pk):
    from django.db import transaction
    from django.contrib import messages
    from apps.procurement.models import Procurement
    from apps.procurement.stock_sync import (reverse_procurement, affected_stock,
                                             check_no_negative_stock, StockConflict)

    proc = get_object_or_404(Procurement, pk=pk)
    try:
        with transaction.atomic():
            products, spares = affected_stock(proc)
            reverse_procurement(proc, request.user)   # reverse stock, then delete
            check_no_negative_stock(products, spares)
            proc.delete()
    except StockConflict as e:
        messages.error(request, f'Cannot delete — stock from this purchase was already sold: {e}.')
        return redirect('web:procurement_detail', pk=proc.pk)
    return redirect('web:procurement_list')
