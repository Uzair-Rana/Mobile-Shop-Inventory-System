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
        details = dict(brand=item.brand or '', model=item.product,
                       pta_status=item.pta_status or 'PTA Approved',
                       condition=item.condition or 'Grade A',
                       cost_price=item.unit_cost or 0, sell_price=item.sell_price or 0)
        for imei in item.imei_list():
            unit = Unit.objects.filter(imei1=imei).first()
            if unit is None:
                Unit.objects.create(imei1=imei, lifecycle_state='in_stock', added_by=actor, **details)
            elif unit.lifecycle_state != 'in_stock':
                # Buy-back / re-stock of a phone sold (or returned) earlier:
                # the same IMEI comes back into stock with the new details.
                for k, v in details.items():
                    setattr(unit, k, v)
                unit.lifecycle_state = 'in_stock'
                unit.save()
            # already in stock → the form rejects this, nothing to add

    elif cat in ('accessory', 'product'):
        from apps.inventory.models import Product, StockMovement
        # A typed SKU is authoritative (never fall back to a same-named item
        # with a different SKU); without a SKU, match by name.
        if item.sku:
            prod = Product.objects.filter(sku__iexact=item.sku).first()
        else:
            prod = Product.objects.filter(name__iexact=item.product).first()
        if prod:
            prod.stock_qty = (prod.stock_qty or 0) + item.qty
            if item.unit_cost:
                prod.cost_price = item.unit_cost
            if item.sell_price:
                prod.sell_price = item.sell_price
            fields = ['stock_qty', 'cost_price', 'sell_price', 'updated_at']
            # A threshold typed on this line updates the item's alert level;
            # leaving it blank keeps the level the item already has.
            if item.low_stock_alert is not None:
                prod.reorder_level = item.low_stock_alert
                fields.append('reorder_level')
            prod.save(update_fields=fields)
        else:
            prod = Product.objects.create(
                name=item.product,
                sku=item.sku or _unique_sku(Product, item.product),
                brand=item.brand or '',
                category='Accessory' if cat == 'accessory' else 'Product',
                cost_price=item.unit_cost or 0, sell_price=item.sell_price or 0,
                stock_qty=item.qty,
                **({'reorder_level': item.low_stock_alert}
                   if item.low_stock_alert is not None else {}),
            )
        # Audit trail — mirror the ledger entry spare parts get.
        StockMovement.objects.create(
            product=prod, type='purchase', qty_change=item.qty, actor=actor,
            note=f'Procurement #{item.procurement_id}',
        )
        item.linked_product = prod

    elif cat == 'spare_part':
        from apps.spare_parts.models import SparePart, SparePartLedger
        if item.sku:
            part = SparePart.objects.filter(sku__iexact=item.sku).first()
        else:
            part = SparePart.objects.filter(name__iexact=item.product).first()
        if not part:
            valid = dict(SparePart.Category.choices)
            part = SparePart.objects.create(
                sku=item.sku or _unique_sku(SparePart, item.product),
                name=item.product,
                category=item.spare_category if item.spare_category in valid else 'display_panel',
                brand_compat=item.brand or '',
                cost_price=item.unit_cost or 0, sell_price=item.sell_price or 0,
                created_by=actor,
                **({'reorder_level': item.low_stock_alert}
                   if item.low_stock_alert is not None else {}),
            )
        elif item.low_stock_alert is not None:
            part.reorder_level = item.low_stock_alert
            part.save(update_fields=['reorder_level'])
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
        from apps.sales.models import InvoiceLine
        # Only units still in stock are taken back (sold ones stay sold). A unit
        # with sales history (a buy-back) goes back to "sold" instead of being
        # deleted, so its old invoices still point at it.
        for unit in Unit.objects.filter(imei1__in=item.imei_list(), lifecycle_state='in_stock'):
            if InvoiceLine.objects.filter(product_type='unit', product_id=unit.pk).exists():
                unit.lifecycle_state = 'sold'
                unit.save(update_fields=['lifecycle_state', 'updated_at'])
            else:
                unit.delete()

    elif cat in ('accessory', 'product'):
        if item.linked_product_id:
            from apps.inventory.models import StockMovement
            prod = item.linked_product
            # May go below zero here; check_no_negative_stock() then rejects the
            # whole edit/delete if items from this purchase were already sold.
            prod.stock_qty = (prod.stock_qty or 0) - item.qty
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


class StockConflict(Exception):
    """Raised when an edit/delete would remove stock that was already sold."""


def affected_stock(procurement):
    """Product / spare-part ids a procurement touches (take before edits)."""
    items = list(procurement.items.all())
    return ({i.linked_product_id for i in items if i.linked_product_id},
            {i.linked_spare_id for i in items if i.linked_spare_id})


def check_no_negative_stock(product_ids, spare_ids):
    """Call after reversing / re-applying inside the same transaction; raises
    StockConflict so the caller can roll the whole change back."""
    from apps.inventory.models import Product
    from apps.spare_parts.models import SparePart
    from django.db.models import Sum
    problems = [f'{p.name}: {-p.stock_qty} already sold'
                for p in Product.objects.filter(pk__in=product_ids, stock_qty__lt=0)]
    for part in SparePart.objects.filter(pk__in=spare_ids):
        bal = part.ledger.aggregate(t=Sum('qty'))['t'] or 0
        if bal < 0:
            problems.append(f'{part.name}: {-bal} already used/sold')
    if problems:
        raise StockConflict('; '.join(problems))
