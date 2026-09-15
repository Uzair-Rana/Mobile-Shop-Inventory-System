"""
Spare Parts Master Catalog
───────────────────────────────────────────────────────────────────────────────
Two-table design:

  SparePart       – master record for each distinct part SKU
  SparePartLedger – one immutable row per stock movement (IN / OUT)

Stock-on-hand is NEVER stored as a column.  It is always derived as:
    SUM(qty) over all ledger rows for that part.
This means history is fully reconstructible at any point in time.

Categories (exactly as specified):
  display_panel     Mobile Display Panels & Touch Assemblies (LCD/OLED/AMOLED)
  oca_glass         OCA Glass & Sheets
  battery           Replacement Batteries & Internal Battery Packs
  charging_flex     Charging Flex, Strips, and Connectors
  body_frame        Bodies, Back Glass, Middle Frames, Camera Lens Housings
  camera_module     Internal Camera Modules (Front & Rear)
"""
from django.db import models
from django.db.models import Sum
from django.conf import settings


class SparePart(models.Model):
    """Master catalog entry — one row per distinct part SKU."""

    class Category(models.TextChoices):
        DISPLAY_PANEL  = 'display_panel',  'Display Panels & Touch Assemblies'
        OCA_GLASS      = 'oca_glass',      'OCA Glass & Sheets'
        BATTERY        = 'battery',        'Batteries & Internal Battery Packs'
        CHARGING_FLEX  = 'charging_flex',  'Charging Flex, Strips & Connectors'
        BODY_FRAME     = 'body_frame',     'Bodies, Frames & Camera Lens Housings'
        CAMERA_MODULE  = 'camera_module',  'Camera Modules (Front & Rear)'

    class DisplayType(models.TextChoices):
        LCD    = 'LCD',    'LCD'
        OLED   = 'OLED',   'OLED'
        AMOLED = 'AMOLED', 'AMOLED'
        NA     = 'N/A',    'N/A'

    class CameraPosition(models.TextChoices):
        FRONT  = 'front',  'Front'
        REAR   = 'rear',   'Rear'
        BOTH   = 'both',   'Front & Rear'
        NA     = 'N/A',    'N/A'

    # Identity
    sku           = models.CharField(max_length=100, unique=True)
    name          = models.CharField(max_length=255)
    category      = models.CharField(max_length=30, choices=Category.choices, db_index=True)
    brand_compat  = models.CharField(max_length=100, blank=True,
                                     help_text='Compatible phone brand(s), e.g. "Samsung, Oppo"')
    model_compat  = models.CharField(max_length=255, blank=True,
                                     help_text='Compatible model(s), e.g. "A54, A53, A52"')
    description   = models.TextField(blank=True)

    # Category-specific attributes (nullable; populate only what's relevant)
    display_type     = models.CharField(
        max_length=10, choices=DisplayType.choices,
        default=DisplayType.NA, blank=True,
        help_text='LCD / OLED / AMOLED — relevant for display_panel category')
    with_frame       = models.BooleanField(
        default=False,
        help_text='True if the display assembly includes the frame/chassis')
    camera_position  = models.CharField(
        max_length=10, choices=CameraPosition.choices,
        default=CameraPosition.NA, blank=True,
        help_text='Front / Rear — relevant for camera_module category')
    battery_capacity = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='mAh — relevant for battery category')

    # Pricing
    cost_price  = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sell_price  = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Thresholds
    reorder_level = models.PositiveIntegerField(default=3)

    # Branch
    branch = models.ForeignKey(
        'branches.Branch', null=True, blank=True, on_delete=models.SET_NULL)

    # Timestamps
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
        related_name='spare_parts_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active  = models.BooleanField(default=True)

    class Meta:
        ordering = ['category', 'name']
        indexes  = [models.Index(fields=['category', 'brand_compat'])]

    def __str__(self):
        return f'[{self.sku}] {self.name}'

    # ── Derived stock helpers (no stored counter) ─────────────────────────────

    @property
    def stock_on_hand(self) -> int:
        """Current balance derived entirely from the ledger."""
        result = self.ledger.aggregate(total=Sum('qty'))['total']
        return result if result is not None else 0

    def balance_at(self, dt) -> int:
        """Balance at a specific point in time (for historical reconstruction)."""
        result = self.ledger.filter(created_at__lte=dt).aggregate(total=Sum('qty'))['total']
        return result if result is not None else 0


class SparePartLedger(models.Model):
    """
    Immutable ledger entry — one row per stock movement.

    Rules:
      • qty > 0  → stock-in  (purchase, return, opening balance …)
      • qty < 0  → stock-out (used in repair, damaged, sold …)
      • qty == 0 is rejected by a model-level clean() / DB check.

    The running balance at any point = SUM(qty WHERE created_at <= t).
    """

    class EntryType(models.TextChoices):
        OPENING_BALANCE = 'opening_balance', 'Opening Balance'
        PURCHASE        = 'purchase',        'Purchase / Stock-In'
        REPAIR_USE      = 'repair_use',      'Used in Repair'
        SALE            = 'sale',            'Sold to Customer'
        RETURN_IN       = 'return_in',       'Return from Customer / Tech'
        RETURN_OUT      = 'return_out',      'Returned to Supplier'
        ADJUSTMENT_IN   = 'adjustment_in',   'Manual Adjustment (In)'
        ADJUSTMENT_OUT  = 'adjustment_out',  'Manual Adjustment (Out)'
        TRANSFER_IN     = 'transfer_in',     'Transfer In'
        TRANSFER_OUT    = 'transfer_out',    'Transfer Out'
        DAMAGED         = 'damaged',         'Damaged / Written-Off'
        TESTING         = 'testing',         'Used for Testing / Demo'

    # IN types (qty must be positive)
    IN_TYPES  = {
        'opening_balance', 'purchase', 'return_in',
        'adjustment_in', 'transfer_in',
    }
    # OUT types (qty must be negative)
    OUT_TYPES = {
        'repair_use', 'sale', 'return_out',
        'adjustment_out', 'transfer_out', 'damaged', 'testing',
    }

    part       = models.ForeignKey(SparePart, on_delete=models.CASCADE, related_name='ledger')
    entry_type = models.CharField(max_length=20, choices=EntryType.choices, db_index=True)

    # Positive = in, Negative = out.  Zero is forbidden (see clean).
    qty        = models.IntegerField()

    unit_cost  = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text='Unit cost at the time of this movement (for purchase/in entries)')

    reference  = models.CharField(
        max_length=100, blank=True,
        help_text='PO number, repair job number, invoice, etc.')
    note       = models.TextField(blank=True)

    # WHO
    actor      = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL,
        related_name='spare_ledger_entries')

    # WHEN — set once, never updated
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # Running balance snapshot (denormalized for fast display; derived is authoritative)
    balance_after = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['part', 'created_at']),
            models.Index(fields=['entry_type', 'created_at']),
        ]

    def __str__(self):
        direction = '+' if self.qty > 0 else ''
        return f'{self.part.sku} {direction}{self.qty} ({self.entry_type})'

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.qty == 0:
            raise ValidationError('Ledger qty cannot be zero.')
        if self.entry_type in self.IN_TYPES and self.qty < 0:
            raise ValidationError(
                f'Entry type "{self.entry_type}" must have a positive qty.')
        if self.entry_type in self.OUT_TYPES and self.qty > 0:
            raise ValidationError(
                f'Entry type "{self.entry_type}" must have a negative qty.')

    def save(self, *args, **kwargs):
        # Compute and snapshot the balance at write time (advisory — not authoritative)
        if self._state.adding:
            current = self.part.stock_on_hand   # before this entry
            self.balance_after = current + self.qty
        super().save(*args, **kwargs)
