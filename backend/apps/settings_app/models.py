from django.db import models


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
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Company Settings'
        verbose_name_plural = 'Company Settings'

    def __str__(self):
        return self.name
