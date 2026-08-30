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
    final_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
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


class RepairStatusLog(models.Model):
    repair = models.ForeignKey(RepairJob, on_delete=models.CASCADE, related_name='logs')
    status = models.CharField(max_length=20)
    note = models.TextField(blank=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now_add=True)


class RepairPart(models.Model):
    repair = models.ForeignKey(RepairJob, on_delete=models.CASCADE, related_name='parts')
    name = models.CharField(max_length=255)
    qty = models.IntegerField(default=1)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
