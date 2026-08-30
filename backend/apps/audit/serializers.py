from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source='actor.username', read_only=True, default='system')

    class Meta:
        model = AuditLog
        fields = [
            'id', 'actor', 'actor_username', 'action',
            'entity_type', 'entity_id', 'changes',
            'ip_address', 'timestamp',
        ]
        read_only_fields = fields
