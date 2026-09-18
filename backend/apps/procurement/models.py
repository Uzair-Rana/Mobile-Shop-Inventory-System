"""
Procurement module — single entry point for adding stock.

Admin creates ONE Procurement (supplier, date, invoice) with multiple line items.
Each item names a Stock Category; on save the matching stock model is
created/updated automatically. Admin never touches stock models directly.

Stock sync + reversal live in `stock_sync.py` and always run inside
transaction.atomic() so procurement and stock can never drift apart.
"""
from django.db import models
from django.conf import settings


class Procurement(models.Model):
    supplier    = models.ForeignKey('suppliers.Supplier', null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name='procurements')
    date        = models.DateField()
    invoice_no  = models.CharField(max_length=100, blank=True)
    total       = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    notes       = models.TextField(blank=True)
    created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                                    on_delete=models.SET_NULL, related_name='procurements')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f'Procurement #{self.pk} — {self.supplier or "?"} ({self.date})'

    def recalc_total(self, save=True):
        total = sum((it.qty or 0) * (it.unit_cost or 0) for it in self.items.all())
        self.total = total
        if save:
            super().save(update_fields=['total'])
        return total


class ProcurementItem(models.Model):
    class Category(models.TextChoices):
        IMEI       = 'imei',       'IMEI Devices'
        ACCESSORY  = 'accessory',  'Accessories'
        SPARE_PART = 'spare_part', 'Spare Parts'
        PRODUCT    = 'product',    'Products'

    procurement = models.ForeignKey(Procurement, on_delete=models.CASCADE, related_name='items')
    category    = models.CharField(max_length=20, choices=Category.choices)

    product     = models.CharField(max_length=255, help_text='Product / part / device name')
    sku         = models.CharField(max_length=100, blank=True,
                                   help_text='For accessory / spare / product matching & creation')
    brand       = models.CharField(max_length=100, blank=True)
    qty         = models.PositiveIntegerField(default=1)
    unit_cost   = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sell_price  = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                      help_text='Used when creating new stock')

    # IMEI category only — one IMEI per line, comma/space/newline separated
    imeis       = models.TextField(blank=True)
    pta_status  = models.CharField(max_length=50, blank=True)   # applied to every IMEI in the line
    condition   = models.CharField(max_length=50, blank=True)
    # Spare-part category for new spare parts (display, battery, flex…)
    spare_category = models.CharField(max_length=30, blank=True)

    # ── Reversal tracking (set when stock is applied) ─────────────────────────
    linked_product = models.ForeignKey('inventory.Product', null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='+')
    linked_spare   = models.ForeignKey('spare_parts.SparePart', null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='+')
    applied     = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.get_category_display()}: {self.product} × {self.qty}'

    def imei_list(self):
        """Parse the imeis field into a clean list of IMEI strings."""
        import re
        return [t for t in re.split(r'[\s,]+', (self.imeis or '').strip()) if t]

    @property
    def line_total(self):
        return (self.qty or 0) * (self.unit_cost or 0)
