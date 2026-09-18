"""
Stock synchronisation for Procurement.

apply_item / reverse_item translate a ProcurementItem into the correct stock
model. apply_procurement / reverse_procurement wrap the whole set in a single
transaction so procurement and stock never go out of sync.

Category rules:
  imei                       → one inventory.Unit per IMEI (unique).
  accessory / product        → inventory.Product; increment if it exists, else create.
  spare_part                 → spare_parts.SparePart + a +qty ledger entry.
"""
from django.db import transaction
from django.utils.text import slugify


# ── helpers ────────────────────────────────────────────────────────────────────

def _unique_sku(model, base):
    base = (slugify(base) or 'item').upper().replace('-', '')[:16] or 'ITEM'
    sku, n = base, 1
    while model.objects.filter(sku=sku).exists():
        n += 1
        sku = f'{base}-{n}'
    return sku


# ── apply ───────────────────────────────────────────────────────────────────────

def apply_item(item, actor=None):
    """Create/increment the matching stock record for one ProcurementItem."""
    if item.applied:
        return
    cat = item.category

    if cat == 'imei':
        from apps.inventory.models import Unit
        for imei in item.imei_list():
            if Unit.objects.filter(imei1=imei).exists():
                continue  # never duplicate an active IMEI
            Unit.objects.create(
                imei1=imei, brand=item.brand or '', model=item.product,
                cost_price=item.unit_cost or 0, sell_price=item.sell_price or 0,
                lifecycle_state='in_stock', added_by=actor,
            )

    elif cat in ('accessory', 'product'):
        from apps.inventory.models import Product, StockMovement
        prod = None
        if item.sku:
            prod = Product.objects.filter(sku=item.sku).first()
        if not prod:
            prod = Product.objects.filter(name__iexact=item.product).first()
        if prod:
            prod.stock_qty = (prod.stock_qty or 0) + item.qty
            if item.unit_cost:
                prod.cost_price = item.unit_cost
            if item.sell_price:
                prod.sell_price = item.sell_price
            prod.save(update_fields=['stock_qty', 'cost_price', 'sell_price', 'updated_at'])
        else:
            prod = Product.objects.create(
                name=item.product,
                sku=item.sku or _unique_sku(Product, item.product),
                brand=item.brand or '',
                category='Accessory' if cat == 'accessory' else 'Product',
                cost_price=item.unit_cost or 0, sell_price=item.sell_price or 0,
                stock_qty=item.qty,
            )
        # Audit trail — mirror the ledger entry spare parts get.
        StockMovement.objects.create(
            product=prod, type='purchase', qty_change=item.qty, actor=actor,
            note=f'Procurement #{item.procurement_id}',
        )
        item.linked_product = prod

    elif cat == 'spare_part':
        from apps.spare_parts.models import SparePart, SparePartLedger
        part = None
        if item.sku:
            part = SparePart.objects.filter(sku=item.sku).first()
        if not part:
            part = SparePart.objects.filter(name__iexact=item.product).first()
        if not part:
            part = SparePart.objects.create(
                sku=item.sku or _unique_sku(SparePart, item.product),
                name=item.product, category='display_panel',
                brand_compat=item.brand or '',
                cost_price=item.unit_cost or 0, sell_price=item.sell_price or 0,
                created_by=actor,
            )
        SparePartLedger.objects.create(
            part=part, entry_type='purchase', qty=item.qty,
            unit_cost=item.unit_cost or 0,
            reference=f'PROC-{item.procurement_id}', actor=actor,
        )
        item.linked_spare = part

    item.applied = True
    item.save(update_fields=['linked_product', 'linked_spare', 'applied'])


# ── reverse ─────────────────────────────────────────────────────────────────────

def reverse_item(item, actor=None):
    """Undo the stock effect of one ProcurementItem (for edit/delete)."""
    if not item.applied:
        return
    cat = item.category

    if cat == 'imei':
        from apps.inventory.models import Unit
        # Only remove units still in stock (not ones already sold/transferred).
        Unit.objects.filter(imei1__in=item.imei_list(), lifecycle_state='in_stock').delete()

    elif cat in ('accessory', 'product'):
        if item.linked_product_id:
            from apps.inventory.models import StockMovement
            prod = item.linked_product
            prod.stock_qty = max(0, (prod.stock_qty or 0) - item.qty)
            prod.save(update_fields=['stock_qty', 'updated_at'])
            StockMovement.objects.create(
                product=prod, type='adjustment_out', qty_change=-item.qty, actor=actor,
                note=f'Reversal of procurement #{item.procurement_id}',
            )

    elif cat == 'spare_part':
        if item.linked_spare_id:
            from apps.spare_parts.models import SparePartLedger
            SparePartLedger.objects.create(
                part=item.linked_spare, entry_type='return_out', qty=-item.qty,
                unit_cost=item.unit_cost or 0,
                reference=f'PROC-{item.procurement_id}-REV', actor=actor,
                note='Reversal of procurement stock-in',
            )

    item.applied = False
    item.save(update_fields=['applied'])


# ── whole-procurement wrappers ──────────────────────────────────────────────────

@transaction.atomic
def apply_procurement(procurement, actor=None):
    for item in procurement.items.all():
        apply_item(item, actor)
    procurement.recalc_total()


@transaction.atomic
def reverse_procurement(procurement, actor=None):
    for item in procurement.items.all():
        reverse_item(item, actor)
