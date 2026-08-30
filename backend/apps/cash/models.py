from django.db import models
from django.conf import settings


class CashSession(models.Model):
    STATUS = [
        ('open', 'Open'),
        ('pending_count', 'Pending Count'),
        ('reconciled', 'Reconciled'),
        ('closed', 'Closed'),
    ]

    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE)
    opened_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='opened_sessions'
    )
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='closed_sessions'
    )

    opening_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expected_closing = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    counted_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    variance = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS, default='open')
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-opened_at']

    def __str__(self):
        return f'Session {self.id} — {self.branch} ({self.status})'


class CashEntry(models.Model):
    """Inflow or outflow within a cash session."""
    TYPES = [('inflow', 'Inflow'), ('outflow', 'Outflow')]
    CATEGORIES = [
        ('sale', 'Sale'),
        ('repair_payment', 'Repair Payment'),
        ('installment_collection', 'Installment Collection'),
        ('expense', 'Expense'),
        ('salary', 'Salary'),
        ('purchase_payment', 'Purchase Payment'),
        ('refund', 'Refund'),
        ('other', 'Other'),
    ]

    session = models.ForeignKey(CashSession, on_delete=models.CASCADE, related_name='entries')
    type = models.CharField(max_length=10, choices=TYPES)
    category = models.CharField(max_length=30, choices=CATEGORIES, default='other')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.TextField(blank=True)
    reference = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.type} {self.amount} ({self.category})'


class Expense(models.Model):
    """Standalone expense record (may or may not be tied to a session)."""
    CATEGORIES = [
        ('rent', 'Rent'),
        ('utilities', 'Utilities'),
        ('salary', 'Salary'),
        ('maintenance', 'Maintenance'),
        ('marketing', 'Marketing'),
        ('supplies', 'Supplies'),
        ('other', 'Other'),
    ]

    branch = models.ForeignKey('branches.Branch', null=True, on_delete=models.SET_NULL)
    session = models.ForeignKey(CashSession, null=True, blank=True, on_delete=models.SET_NULL)
    category = models.CharField(max_length=30, choices=CATEGORIES, default='other')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255)
    reference = models.CharField(max_length=100, blank=True)
    expense_date = models.DateField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-expense_date', '-created_at']

    def __str__(self):
        return f'{self.category} {self.amount}'
