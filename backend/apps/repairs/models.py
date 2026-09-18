from django.db import models
from django.conf import settings


class RepairJob(models.Model):
    STATUS = [
        ('received', 'Received'), ('diagnosed', 'Diagnosed'),
        ('waiting_parts', 'Waiting Parts'), ('in_progress', 'In Progress'),
        ('ready', 'Ready for Pickup'), ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'), ('unrepairable', 'Unrepairable'),
    ]
    job_number = models.CharField(max_length=30, unique=True)
    customer = models.ForeignKey('customers.Customer', null=True, blank=True, on_delete=models.SET_NULL)
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=20, blank=True)
    device_model = models.CharField(max_length=200)
    device_imei = models.CharField(max_length=20, blank=True)
    fault_description = models.TextField()
    diagnosis = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='received')
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='repair_jobs'
    )
    branch = models.ForeignKey('branches.Branch', null=True, on_delete=models.SET_NULL)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    labour_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # final_cost = labour_charge + parts total (kept in sync by recalc_total()).
    final_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Items the customer left with the phone (charger, cover…), comma-separated.
    accessories_received = models.TextField(blank=True)
    # Other costs of doing this repair (outside work, courier…) — reduces profit.
    extra_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    completed_at = models.DateTimeField(null=True, blank=True)   # first set Ready / Delivered
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
        related_name='created_repairs'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.job_number:
            last = RepairJob.objects.order_by('-id').first()
            num = (last.id + 1) if last else 1
            self.job_number = f'JOB-{num:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.job_number

    @property
    def parts_total(self):
        return sum((p.line_total for p in self.parts.all()), 0)

    def recalc_total(self):
        self.final_cost = self.labour_charge + self.parts_total


class RepairStatusLog(models.Model):
    repair = models.ForeignKey(RepairJob, on_delete=models.CASCADE, related_name='logs')
    status = models.CharField(max_length=20)
    note = models.TextField(blank=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now_add=True)


class RepairPart(models.Model):
    """A part / product taken from stock and used in a repair."""
    TYPES = [('spare', 'Spare Part'), ('product', 'Accessory / Product')]
    repair = models.ForeignKey(RepairJob, on_delete=models.CASCADE, related_name='parts')
    part_type = models.CharField(max_length=10, choices=TYPES, default='spare')
    part_id = models.IntegerField(null=True, blank=True)  # SparePart / Product pk
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, blank=True)
    qty = models.IntegerField(default=1)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)        # cost price per unit
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # charged to customer
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    added_at = models.DateTimeField(auto_now_add=True, null=True)

    @property
    def line_total(self):
        return self.unit_price * self.qty
