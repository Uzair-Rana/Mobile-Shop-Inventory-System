from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    ACTIONS = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('approve', 'Approve'),
        ('void', 'Void'),
    ]

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='audit_logs',
    )
    action = models.CharField(max_length=20, choices=ACTIONS)
    entity_type = models.CharField(max_length=100)   # e.g. 'Invoice', 'User'
    entity_id = models.CharField(max_length=50, blank=True)
    changes = models.JSONField(default=dict, blank=True)  # {'field': [old, new]}
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.action} {self.entity_type}#{self.entity_id} by {self.actor}'


class AuditTrailQuerySet(models.QuerySet):
    """Append-only: bulk UPDATE / DELETE are refused (DB triggers back this up)."""

    def update(self, **kwargs):
        raise PermissionError('AuditTrail is append-only: UPDATE is not allowed')

    def delete(self):
        raise PermissionError('AuditTrail is append-only: DELETE is not allowed')


class AuditTrail(models.Model):
    """Immutable record of sensitive changes (stock counts, voids, prices).

    Rows are only ever inserted — see apps.audit.recorder.record_audit(). The
    table also has database triggers (migration 0002) that block UPDATE and
    DELETE, so no code path can rewrite history."""
    INVENTORY_COUNT_MODIFICATION = 'inventory_count_modification'
    BILL_VOIDING = 'bill_voiding'
    PRICE_ADJUSTMENT = 'price_adjustment'
    MANUAL_STOCK_ADJUSTMENT = 'manual_stock_adjustment'
    ACTION_TYPES = [
        (INVENTORY_COUNT_MODIFICATION, 'Inventory count modification'),
        (BILL_VOIDING, 'Bill voiding'),
        (PRICE_ADJUSTMENT, 'Price adjustment'),
        (MANUAL_STOCK_ADJUSTMENT, 'Manual stock adjustment'),
    ]

    action_type = models.CharField(max_length=40, choices=ACTION_TYPES, db_index=True)
    entity_type = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=50, db_index=True)
    previous_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    reason = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='audit_trail_entries',
    )

    objects = AuditTrailQuerySet.as_manager()

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['action_type', 'timestamp'], name='audit_audit_action__f8a047_idx'),
            models.Index(fields=['entity_type', 'entity_id'], name='audit_audit_entity__318542_idx'),
        ]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise PermissionError('AuditTrail is append-only: UPDATE is not allowed')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionError('AuditTrail is append-only: DELETE is not allowed')

    def __str__(self):
        return f'{self.action_type} {self.entity_type}#{self.entity_id} by {self.actor}'
