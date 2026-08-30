from django.db import models


class Branch(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    # Business settings per branch
    discount_threshold = models.DecimalField(
        max_digits=5, decimal_places=2, default=10.00,
        help_text='Max discount % a cashier can apply without approval'
    )
    tax_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00,
        help_text='Default tax rate % for this branch'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
