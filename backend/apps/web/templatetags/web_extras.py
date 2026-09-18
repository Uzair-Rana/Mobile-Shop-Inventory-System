from django import template

register = template.Library()

_ICONS = {
    'home': '🏠', 'pos': '🧾', 'box': '📦', 'receipt': '🧾', 'wrench': '🔧',
    'truck': '🚚', 'cash': '💵', 'cog': '⚙️', 'device': '📱', 'plug': '🔌',
    'tag': '🏷️', 'users': '👥', 'building': '🏢', 'transfer': '🔁',
    'expense': '💸', 'chart': '📊',
}


@register.filter
def nav_icon(name):
    return _ICONS.get(name, '•')


@register.filter
def underscores(value):
    """snake_case_status -> 'snake case status' (pair with text-transform)."""
    return str(value).replace('_', ' ')
