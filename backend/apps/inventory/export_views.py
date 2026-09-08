"""
Inventory Excel export view.
GET /api/v1/inventory/export-excel/
Supports the same query params as the products list: search, category, brand.
Returns: { file_url, file_name }
"""
import os
import uuid
from datetime import date

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product


def _thin_border():
    s = Side(style='thin', color='DDDDDD')
    return Border(left=s, right=s, top=s, bottom=s)


@api_view(['GET'])
def export_products_excel(request):
    """
    Generate an Excel file of the filtered product list and return its URL.
    Filters: search (name/sku), category, brand, low_stock
    """
    qs = Product.objects.select_related('branch').all()

    # ── Apply filters (mirrors the DRF filterset behaviour) ────────────────
    search = request.query_params.get('search', '').strip()
    if search:
        from django.db.models import Q
        qs = qs.filter(
            Q(name__icontains=search) |
            Q(sku__icontains=search)  |
            Q(brand__icontains=search)
        )

    category = request.query_params.get('category', '').strip()
    if category:
        qs = qs.filter(category__iexact=category)

    brand = request.query_params.get('brand', '').strip()
    if brand:
        qs = qs.filter(brand__iexact=brand)

    branch_id = request.headers.get('X-Branch-ID', '').strip()
    if branch_id:
        qs = qs.filter(branch_id=branch_id)

    if request.query_params.get('low_stock'):
        from django.db.models import F
        qs = qs.filter(stock_qty__lte=F('reorder_level'))

    # ── Build workbook ─────────────────────────────────────────────────────
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Products'

    # Colour palette matching the brand
    BRAND_RED  = 'E11D48'
    HEADER_BG  = 'FFF1F2'
    ALT_ROW    = 'FEF2F5'

    # Header row
    headers = [
        'SKU', 'Product Name', 'Brand', 'Category',
        'Stock Qty', 'Reorder Level', 'Sell Price (PKR)', 'Cost Price (PKR)',
        'Branch',
    ]
    ws.append(headers)
    for col_idx, _ in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.font      = Font(bold=True, color='FFFFFF', size=10)
        cell.fill      = PatternFill('solid', fgColor=BRAND_RED)
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border    = _thin_border()

    ws.row_dimensions[1].height = 22

    # Data rows
    for i, p in enumerate(qs, 1):
        row = [
            p.sku,
            p.name,
            p.brand or '',
            p.category or '',
            p.stock_qty,
            p.reorder_level,
            float(p.sell_price),
            float(p.cost_price),
            p.branch.name if p.branch else '',
        ]
        ws.append(row)
        row_num = i + 1
        bg = ALT_ROW if i % 2 == 0 else 'FFFFFF'
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=row_num, column=col_idx)
            cell.fill   = PatternFill('solid', fgColor=bg)
            cell.border = _thin_border()
            cell.alignment = Alignment(vertical='center')
            if col_idx in (7, 8):   # price columns — right-align
                cell.number_format = '#,##0.00'
                cell.alignment = Alignment(horizontal='right', vertical='center')
            if col_idx == 5 and p.stock_qty <= p.reorder_level:
                cell.font = Font(color='DC2626', bold=True)

    # Column widths
    widths = [14, 36, 18, 18, 10, 12, 18, 18, 18]
    for idx, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(idx)].width = w

    # Summary footer
    last_row = qs.count() + 2
    ws.cell(row=last_row, column=1, value='Total Products').font = Font(bold=True)
    ws.cell(row=last_row, column=5, value=f'=SUM(E2:E{last_row-1})').font = Font(bold=True, color=BRAND_RED)

    # ── Save to MEDIA_ROOT/exports/ ────────────────────────────────────────
    export_dir = os.path.join(settings.MEDIA_ROOT, 'exports')
    os.makedirs(export_dir, exist_ok=True)

    file_name = f'products-{date.today()}-{uuid.uuid4().hex[:6]}.xlsx'
    file_path = os.path.join(export_dir, file_name)
    wb.save(file_path)

    # Build absolute URL
    base_url = request.build_absolute_uri('/').rstrip('/')
    file_url = f'{base_url}{settings.MEDIA_URL}exports/{file_name}'

    return Response({
        'file_name': file_name,
        'file_url':  file_url,
        'count':     qs.count(),
    })
