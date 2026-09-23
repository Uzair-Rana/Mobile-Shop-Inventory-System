"""Inject the company profile into every template so shared chrome
(sidebar brand, page title) reflects the configured shop name."""


# Developer details shown by the ⓘ Info button. Fill in phone / website /
# address and they appear automatically (empty values are hidden).
DEVELOPER = {
    'name': 'DevNest System',
    'tagline': 'Software development — POS, inventory & business apps',
    'email': 'devnestsystem@gmail.com',
    'phone': '',
    'website': '',
    'address': '',
}
APP_VERSION = '1.1.0'


def company(request):
    from apps.settings_app.models import CompanySettings
    return {'site_company': CompanySettings.objects.first(),
            'developer': DEVELOPER, 'app_version': APP_VERSION}


def low_stock(request):
    """Count for the sidebar badge and the top-bar bell. Kept cheap and quiet:
    a broken/unmigrated database must never take the whole UI down."""
    if not getattr(request, 'user', None) or not request.user.is_authenticated:
        return {'low_stock_count': 0, 'low_stock_times': []}
    from apps.settings_app.models import CompanySettings
    from .views import low_stock_count
    try:
        company = CompanySettings.objects.first()
        return {'low_stock_count': low_stock_count(),
                'low_stock_times': company.alert_times() if company else ['09:00', '11:00']}
    except Exception:
        return {'low_stock_count': 0, 'low_stock_times': []}


def option_badges(request):
    """Badge colours for owner-editable options (PTA status, condition…)."""
    from apps.settings_app.choices import badge_classes
    return {'option_badges': badge_classes()}
