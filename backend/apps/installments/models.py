from django.db import models
from django.conf import settings
from django.utils import timezone


class InstallmentPlan(models.Model):
    STATUS = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
        ('defaulted', 'Defaulted'),
    ]

    plan_number = models.CharField(max_length=30, unique=True)
    customer = models.ForeignKey(
        'customers.Customer', on_delete=models.PROTECT, related_name='installment_plans'
    )
    invoice = models.OneToOneField(
        'sales.Invoice', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='installment_plan'
    )
    branch = models.ForeignKey('branches.Branch', null=True, on_delete=models.SET_NULL)

    sale_amount = models.DecimalField(max_digits=12, decimal_places=2)
    down_payment = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    markup_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)   # % markup
    financed_amount = models.DecimalField(max_digits=12, decimal_places=2)          # sale - down
    total_payable = models.DecimalField(max_digits=12, decimal_places=2)            # financed × (1 + markup/100)
    installment_count = models.IntegerField()
    installment_amount = models.DecimalField(max_digits=12, decimal_places=2)       # total_payable / count
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance_remaining = models.DecimalField(max_digits=12, decimal_places=2)

    start_date = models.DateField()
    next_due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='active')

    guarantor_name = models.CharField(max_length=255, blank=True)
    guarantor_cnic = models.CharField(max_length=20, blank=True)
    guarantor_phone = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.plan_number:
            last = InstallmentPlan.objects.order_by('-id').first()
            num = (last.id + 1) if last else 1
            self.plan_number = f'INST-{num:04d}'
        self.balance_remaining = self.total_payable - self.amount_paid
        super().save(*args, **kwargs)

    def __str__(self):
        return self.plan_number


class InstallmentSchedule(models.Model):
    """One row per installment in the plan."""
    STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('partial', 'Partial'),
    ]
    plan = models.ForeignKey(InstallmentPlan, on_delete=models.CASCADE, related_name='schedule')
    installment_number = models.IntegerField()
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='pending')

    class Meta:
        ordering = ['installment_number']

    def __str__(self):
        return f'{self.plan.plan_number} #{self.installment_number}'


class InstallmentPayment(models.Model):
    """Actual payment record for a plan."""
    plan = models.ForeignKey(InstallmentPlan, on_delete=models.CASCADE, related_name='payments')
    schedule_item = models.ForeignKey(
        InstallmentSchedule, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='payments'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=30, default='cash')
    reference = models.CharField(max_length=100, blank=True)
    collected_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    collected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.plan.plan_number} payment {self.amount}'
