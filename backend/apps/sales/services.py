"""
Transactional sale operations.

Inventory deductions and payment commitments run inside a single DB
transaction: if any line cannot be fulfilled (insufficient stock, a unit
already sold) or any write fails, the ENTIRE operation rolls back and nothing
is persisted. Rows being decremented are locked with select_for_update() to
prevent two concurrent sales from overselling the same stock.
"""
from django.db import transaction

from rest_framework.exceptions import ValidationError

from apps.inventory.models import Product, Unit, StockMovement
from devnest.money import to_money, money_sum


class InsufficientStock(ValidationError):
    pass


@transaction.atomic
def finalize_invoice(invoice, actor):
    """
    Atomically deduct inventory for every line and mark the invoice finalized.

    All-or-nothing: raises (rolling back the whole transaction) if any line
    cannot be fulfilled, so a partially-deducted sale can never be committed.
    Idempotent — only a draft invoice deducts stock; re-finalizing is a no-op.
    """
    # Re-read under lock so a concurrent finalize can't double-deduct.
    invoice = invoice.__class__.objects.select_for_update().get(pk=invoice.pk)
    if invoice.status != 'draft':
        return invoice  # already committed; do not deduct again

    for line in invoice.lines.all():
        if not line.product_id:
            continue

        if line.product_type == 'unit':
            unit = (Unit.objects.select_for_update()
                    .filter(pk=line.product_id).first())
            if unit is None:
                raise ValidationError(f'Unit #{line.product_id} not found for line "{line.product_name}".')
            if unit.lifecycle_state != 'in_stock':
                raise InsufficientStock(
                    f'Unit {unit.imei1} is not available (state: {unit.lifecycle_state}).'
                )
            unit.lifecycle_state = 'sold'
            unit.save(update_fields=['lifecycle_state', 'updated_at'])
        else:
            product = (Product.objects.select_for_update()
                       .filter(pk=line.product_id).first())
            if product is None:
                raise ValidationError(f'Product #{line.product_id} not found for line "{line.product_name}".')
            if product.stock_qty < line.qty:
                raise InsufficientStock(
                    f'Insufficient stock for "{product.name}": '
                    f'have {product.stock_qty}, need {line.qty}.'
                )
            product.stock_qty -= line.qty
            product.save(update_fields=['stock_qty', 'updated_at'])
            StockMovement.objects.create(
                product=product,
                type='sale',
                qty_change=-line.qty,
                note=f'Sale via {invoice.invoice_number}',
                actor=actor if getattr(actor, 'is_authenticated', False) else None,
            )

    invoice.status = 'finalized'
    invoice.save(update_fields=['status', 'updated_at'])
    return invoice


@transaction.atomic
def commit_payment(invoice, payment_serializer, actor):
    """
    Atomically record a payment and recompute the invoice balance/status.

    The payment insert and the invoice update are one unit: if the invoice
    write fails, the payment is not left orphaned.
    """
    invoice = invoice.__class__.objects.select_for_update().get(pk=invoice.pk)
    payment = payment_serializer.save(invoice=invoice, created_by=actor)

    total_paid = money_sum(p.amount for p in invoice.payments.all())
    invoice.amount_paid = total_paid
    grand_total = to_money(invoice.grand_total)

    if total_paid >= grand_total:
        invoice.status = 'paid'
    elif total_paid > 0:
        invoice.status = 'partially_paid'
    invoice.save()
    return payment
