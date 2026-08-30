import json
from .models import AuditLog


TRACKED_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}

# Paths to skip (auth tokens, admin static, etc.)
SKIP_PATHS = ['/admin/', '/static/', '/media/', '/api/v1/auth/login/', '/api/v1/auth/logout/']


def _get_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _entity_from_path(path):
    """Best-effort entity type from URL path."""
    parts = [p for p in path.strip('/').split('/') if p]
    # /api/v1/<app>/<entity>/<id>/  →  parts = ['api', 'v1', app, entity, id]
    if len(parts) >= 4:
        return parts[3].replace('-', '_').title(), parts[4] if len(parts) > 4 else ''
    if len(parts) >= 3:
        return parts[2].replace('-', '_').title(), ''
    return 'Unknown', ''


class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only log mutating API calls from authenticated users
        if (
            request.method in TRACKED_METHODS
            and request.path.startswith('/api/')
            and not any(request.path.startswith(p) for p in SKIP_PATHS)
            and hasattr(request, 'user')
            and request.user.is_authenticated
        ):
            entity_type, entity_id = _entity_from_path(request.path)

            action_map = {
                'POST': 'create',
                'PUT': 'update',
                'PATCH': 'update',
                'DELETE': 'delete',
            }
            action = action_map.get(request.method, 'update')

            # Try to extract a more specific action from custom action URLs
            path_lower = request.path.lower()
            if 'void' in path_lower:
                action = 'void'
            elif 'approve' in path_lower or 'finalize' in path_lower:
                action = 'approve'

            # Capture request body as "changes" for create/update
            changes = {}
            if request.method in {'POST', 'PUT', 'PATCH'}:
                try:
                    body = json.loads(request.body.decode('utf-8'))
                    # Exclude sensitive fields
                    for key in ('password', 'old_password', 'new_password', 'token'):
                        body.pop(key, None)
                    changes = body
                except Exception:
                    pass

            AuditLog.objects.create(
                actor=request.user,
                action=action,
                entity_type=entity_type,
                entity_id=str(entity_id),
                changes=changes,
                ip_address=_get_ip(request),
            )

        return response
