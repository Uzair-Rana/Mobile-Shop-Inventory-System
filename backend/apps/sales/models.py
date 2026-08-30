from django.db import models
from django.conf import settings


class Invoice(models.Model):
    STATUS = [
        ('draft', 'Draft'), ('finalized', 'Finalized'),
        ('partially_paid', 'Partially Paid'), ('paid', 'Paid'),
        ('returned', 'Returned'), ('voided', 'Voided'),
    ]
    PAYMENT_METHODS = [
        ('cash', 'Cash'), ('card', 'Card'), ('bank_transfer', 'Bank Transfer'),
        ('easypaisa', 'EasyPaisa'), ('jazzcash', 'JazzCash'),
        ('cheque', 'Cheque'), ('installment', 'Installment'),
    ]
    invoice_number = models.CharField(max_length=30, unique=True)
    customer = models.ForeignKey('customers.Customer', null=True, blank=True, on_delete=models.SET_NULL)
    customer_name = models.CharField(max_length=255, default='Walk-in')
    branch = models.ForeignKey('branches.Branch', null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, choices=STATUS, default='draft')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    trade_in_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    trade_in_unit_id = models.IntegerField(null=True, blank=True)  # Unit FK as int to avoid circular
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    notes = models.TextField(blank=True)
    void_reason = models.TextField(blank=True)
    voided_at = models.DateTimeField(null=True, blank=True)
    # Correction linkage
    corrected_invoice = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='corrections'
    )
    correction_type = models.CharField(
        max_length=20, blank=True,
        choices=[('return', 'Return'), ('exchange', 'Exchange'), ('void', 'Void')]
    )
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.invoice_number

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last = Invoice.objects.order_by('-id').first()
            num = (last.id + 1) if last else 1
            self.invoice_number = f'INV-{num:04d}'
        self.balance_due = self.grand_total - self.amount_paid
        super().save(*args, **kwargs)


class InvoiceLine(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='lines')
    product_type = models.CharField(max_length=20, default='accessory')  # accessory | unit
    product_id = models.IntegerField(null=True, blank=True)
    product_name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, blank=True)
    imei = models.CharField(max_length=20, blank=True)
    qty = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.line_total = (self.unit_price * self.qty) - self.discount
        super().save(*args, **kwargs)


class Payment(models.Model):
    METHODS = [
        ('cash', 'Cash'), ('card', 'Card'), ('bank_transfer', 'Bank Transfer'),
        ('easypaisa', 'EasyPaisa'), ('jazzcash', 'JazzCash'),
    ]
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHODS, default='cash')
    reference = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
