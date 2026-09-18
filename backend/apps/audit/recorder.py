"""
Helper for writing entries to the append-only AuditTrail.

Business code should call `record_audit(...)` rather than constructing
AuditTrail rows directly, so that value normalisation (Decimals, etc.) and
actor/IP extraction stay consistent across call sites.
"""
from decimal import Decimal

from .models import AuditTrail


def _jsonable(value):
    """Coerce values into JSON-serialisable primitives (Decimal -> str)."""
    if isinstance(value, Decimal):
        return str(value)
    return value


def _normalise(values):
    if not values:
        return {}
    return {k: _jsonable(v) for k, v in values.items()}


def _client_ip(request):
    if request is None:
        return None
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def record_audit(*, actor, action_type, entity_type, entity_id,
                 previous_values=None, new_values=None, reason='', request=None):
    """
    Append one immutable row to the audit trail.

    Args:
        actor:        User instance (or None for system actions).
        action_type:  One of AuditTrail.ACTION_TYPES values.
        entity_type:  Model name of the affected record, e.g. 'Product'.
        entity_id:    PK of the affected record.
        previous_values / new_values: dicts of the changed fields.
        reason:       Optional human-supplied justification.
        request:      Optional DRF/Django request, used to capture IP.

    Returns the created AuditTrail instance.
    """
    return AuditTrail.objects.create(
        actor=actor if getattr(actor, 'is_authenticated', False) else None,
        action_type=action_type,
        entity_type=entity_type,
        entity_id=str(entity_id),
        previous_values=_normalise(previous_values),
        new_values=_normalise(new_values),
        reason=reason or '',
        ip_address=_client_ip(request),
    )
