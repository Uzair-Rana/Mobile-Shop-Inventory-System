"""Read the owner-editable dropdown options (see ChoiceOption)."""
from .models import ChoiceOption

# Badge colour → existing CSS badge class.
BADGE = {'green': 'badge-green', 'yellow': 'badge-yellow', 'red': 'badge-red',
         'blue': 'badge-blue', 'orange': 'badge-orange', 'gray': 'badge-gray'}


def options(group, include=None):
    """Active option labels for a group, in order. `include` keeps a record's
    current value selectable even if that option was hidden or renamed."""
    labels = list(ChoiceOption.objects.filter(group=group, is_active=True)
                  .values_list('label', flat=True))
    if include and include not in labels:
        labels.insert(0, include)
    return labels


def badge_classes():
    """{group: {label: css badge class}} — loaded once per page."""
    out = {}
    for group, label, color in ChoiceOption.objects.values_list('group', 'label', 'color'):
        out.setdefault(group, {})[label] = BADGE.get(color, 'badge-gray')
    return out
