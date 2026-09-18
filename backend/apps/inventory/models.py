from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Non-serialised product / accessory (has stock_qty)."""
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    brand = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    sell_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stock_qty = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=5)
    branch = models.ForeignKey('branches.Branch', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class StockMovement(models.Model):
    TYPES = [
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
        ('adjustment_in', 'Adjustment In'),
        ('adjustment_out', 'Adjustment Out'),
        ('transfer_in', 'Transfer In'),
        ('transfer_out', 'Transfer Out'),
        ('return', 'Return'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements')
    type = models.CharField(max_length=30, choices=TYPES)
    qty_change = models.IntegerField()
    note = models.TextField(blank=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.type} {self.qty_change} x {self.product}'


class Unit(models.Model):
    """Serialised unit — one IMEI/serial per row."""
    LIFECYCLE = [
        ('in_stock', 'In Stock'),
        ('sold', 'Sold'),
        ('in_repair', 'In Repair'),
        ('reserved', 'Reserved'),
        ('returned', 'Returned'),
        ('defective', 'Defective'),
        ('transferred', 'Transferred'),
    ]
    CONDITIONS = [
        ('Grade A', 'Grade A'),
        ('Grade B', 'Grade B'),
        ('Grade C', 'Grade C'),
        ('Refurbished', 'Refurbished'),
        ('For Parts', 'For Parts'),
    ]
    PTA = [
        ('PTA Approved', 'PTA Approved'),
        ('Non-PTA', 'Non-PTA'),
        ('PTA Blocked', 'PTA Blocked'),
    ]
    imei1 = models.CharField(max_length=20, unique=True)
    imei2 = models.CharField(max_length=20, blank=True, null=True)
    serial = models.CharField(max_length=100, blank=True)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=200)
    condition = models.CharField(max_length=20, choices=CONDITIONS, default='Grade A')
    pta_status = models.CharField(max_length=20, choices=PTA, default='PTA Approved')
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sell_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    lifecycle_state = models.CharField(max_length=20, choices=LIFECYCLE, default='in_stock')
    branch = models.ForeignKey('branches.Branch', null=True, blank=True, on_delete=models.SET_NULL)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.brand} {self.model} ({self.imei1})'
