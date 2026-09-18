"""Inject the company profile into every template so shared chrome
(sidebar brand, page title) reflects the configured shop name."""


def company(request):
    from apps.settings_app.models import CompanySettings
    return {'site_company': CompanySettings.objects.first()}
