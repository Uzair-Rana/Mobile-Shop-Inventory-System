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
