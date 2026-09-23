from django import template

register = template.Library()

_ICONS = {
    'home': '🏠', 'pos': '🧾', 'box': '📦', 'receipt': '🧾', 'wrench': '🔧',
    'truck': '🚚', 'cash': '💵', 'cog': '⚙️', 'backup': '💾', 'device': '📱', 'plug': '🔌',
    'tag': '🏷️', 'users': '👥', 'building': '🏢', 'transfer': '🔁',
    'expense': '💸', 'chart': '📊', 'alert': '🔔',
}


@register.filter
def nav_icon(name):
    return _ICONS.get(name, '•')


@register.filter
def underscores(value):
    """snake_case_status -> 'snake case status' (pair with text-transform)."""
    return str(value).replace('_', ' ')


@register.filter
def option_badge(label, group_map):
    """{{ u.pta_status|option_badge:option_badges.pta_status }} → badge class."""
    return (group_map or {}).get(label, 'badge-gray')
