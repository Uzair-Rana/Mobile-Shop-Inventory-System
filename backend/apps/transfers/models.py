from django.db import models
from django.conf import settings


class Transfer(models.Model):
    STATUS = [
        ('draft', 'Draft'),
        ('dispatched', 'Dispatched'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]

    transfer_number = models.CharField(max_length=30, unique=True)
    from_branch = models.ForeignKey(
        'branches.Branch', on_delete=models.PROTECT, related_name='transfers_out'
    )
    to_branch = models.ForeignKey(
        'branches.Branch', on_delete=models.PROTECT, related_name='transfers_in'
    )
    status = models.CharField(max_length=20, choices=STATUS, default='draft')
    notes = models.TextField(blank=True)

    dispatched_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='dispatched_transfers'
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='received_transfers'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True,
        on_delete=models.SET_NULL, related_name='created_transfers'
    )
    dispatched_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.transfer_number:
            last = Transfer.objects.order_by('-id').first()
            num = (last.id + 1) if last else 1
            self.transfer_number = f'TRF-{num:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.transfer_number


class TransferItem(models.Model):
    """One row per item (unit or product) in a transfer."""
    ITEM_TYPES = [('unit', 'Device Unit'), ('product', 'Accessory/Product')]

    transfer = models.ForeignKey(Transfer, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=10, choices=ITEM_TYPES)
    item_id = models.IntegerField()           # PK of Unit or Product
    item_name = models.CharField(max_length=255)
    imei = models.CharField(max_length=20, blank=True)
    sku = models.CharField(max_length=100, blank=True)
    qty = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.item_type} #{self.item_id} x{self.qty}'
