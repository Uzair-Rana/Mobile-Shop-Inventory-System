from django.db import models
from django.conf import settings


class PurchaseOrder(models.Model):
    STATUS = [
        ('draft', 'Draft'),
        ('ordered', 'Ordered'),
        ('partially_received', 'Partially Received'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]

    order_number = models.CharField(max_length=30, unique=True)
    supplier = models.ForeignKey(
        'suppliers.Supplier', null=True, blank=True, on_delete=models.SET_NULL
    )
    branch = models.ForeignKey('branches.Branch', null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=25, choices=STATUS, default='draft')

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    expected_date = models.DateField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            last = PurchaseOrder.objects.order_by('-id').first()
            num = (last.id + 1) if last else 1
            self.order_number = f'PO-{num:04d}'
        self.grand_total = self.subtotal + self.tax_amount - self.discount_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class PurchaseOrderLine(models.Model):
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='lines')
    product_name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, blank=True)
    qty_ordered = models.IntegerField(default=1)
    qty_received = models.IntegerField(default=0)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)
    product_id = models.IntegerField(null=True, blank=True)  # links to Product or Unit

    def save(self, *args, **kwargs):
        self.line_total = self.unit_cost * self.qty_ordered
        super().save(*args, **kwargs)


class Acquisition(models.Model):
    """Used-phone / trade-in intake."""
    STATUS = [
        ('pending', 'Pending Inspection'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    acquisition_number = models.CharField(max_length=30, unique=True)
    customer = models.ForeignKey(
        'customers.Customer', null=True, blank=True, on_delete=models.SET_NULL
    )
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=20, blank=True)
    branch = models.ForeignKey('branches.Branch', null=True, on_delete=models.SET_NULL)

    device_brand = models.CharField(max_length=100)
    device_model = models.CharField(max_length=200)
    imei = models.CharField(max_length=20, blank=True)
    condition = models.CharField(max_length=50, blank=True)
    faults = models.TextField(blank=True)

    offered_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    accepted_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')

    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.acquisition_number:
            last = Acquisition.objects.order_by('-id').first()
            num = (last.id + 1) if last else 1
            self.acquisition_number = f'ACQ-{num:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.acquisition_number
