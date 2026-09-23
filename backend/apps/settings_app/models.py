from django.db import models


THEMES = [
    ('crimson', 'Crimson'), ('blue', 'Ocean Blue'), ('emerald', 'Emerald'),
    ('violet', 'Royal Violet'), ('orange', 'Sunset Orange'), ('teal', 'Teal'),
]


BILL_DISCLAIMER = 'کسی بھی کارگو کے ذریعے بھیجے گئے سامان کے نقصان کا دکاندار ذمہ دار نہیں ہوگا۔'

RECEIPT_PAPERS = [
    ('80mm', 'Thermal 80 mm (standard receipt)'),
    ('58mm', 'Thermal 58 mm (small receipt)'),
    ('a5', 'A5 page'),
    ('a4', 'A4 page'),
]


class CompanySettings(models.Model):
    """Singleton table — only one row expected."""
    name = models.CharField(max_length=255, default='My Mobile Shop')
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    ntn = models.CharField(max_length=50, blank=True, verbose_name='NTN / Tax Number')
    currency = models.CharField(max_length=10, default='PKR')
    receipt_footer = models.TextField(blank=True, help_text='Printed at the bottom of receipts')
    logo = models.FileField(upload_to='company/', null=True, blank=True)
    theme = models.CharField(max_length=20, choices=THEMES, default='crimson')
    # Printed bills: paper the receipt is laid out for (Developer Options → Printing)
    receipt_paper = models.CharField(max_length=10, choices=RECEIPT_PAPERS, default='80mm')
    receipt_show_logo = models.BooleanField(default=True)
    bill_disclaimer = models.TextField(
        blank=True, default=BILL_DISCLAIMER,
        help_text='Printed at the bottom of every bill')
    # Hashed key that unlocks Settings. Blank = the installation key.
    settings_key = models.CharField(max_length=128, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Company Settings'
        verbose_name_plural = 'Company Settings'

    def __str__(self):
        return self.name


class ChoiceOption(models.Model):
    """Owner-editable dropdown options (Developer Options → Dropdown Options).

    Records store the option's *label* as plain text, so renaming or hiding an
    option never breaks existing records."""
    GROUPS = [
        ('pta_status', 'PTA Status'),
        ('device_condition', 'Device Condition'),
        ('payment_method', 'Payment Methods'),
        ('repair_accessory', 'Received With Device (Repairs)'),
    ]
    COLORS = [
        ('green', 'Green'), ('yellow', 'Yellow'), ('red', 'Red'),
        ('blue', 'Blue'), ('orange', 'Orange'), ('gray', 'Gray'),
    ]
    group = models.CharField(max_length=30, choices=GROUPS, db_index=True)
    label = models.CharField(max_length=50)
    color = models.CharField(max_length=10, choices=COLORS, default='gray')
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['group', 'sort_order', 'id']
        unique_together = [('group', 'label')]

    def __str__(self):
        return f'{self.get_group_display()}: {self.label}'
