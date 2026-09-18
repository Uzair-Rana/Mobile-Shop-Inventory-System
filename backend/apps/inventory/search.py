"""One search for every stock list (POS, Products, Accessories, Devices, Spare
Parts), so the same words find the same items everywhere.

Each word must match at least one field, e.g. "samsung charger" finds a
Samsung-brand item named "Fast Charger"."""
from django.db.models import Q

PRODUCT_FIELDS = ('name', 'sku', 'brand', 'category', 'description')
UNIT_FIELDS = ('imei1', 'imei2', 'serial', 'brand', 'model')
SPARE_FIELDS = ('name', 'sku', 'brand_compat', 'model_compat', 'description')


def word_search(qs, q, fields):
    for word in (q or '').split():
        cond = Q()
        for f in fields:
            cond |= Q(**{f'{f}__icontains': word})
        qs = qs.filter(cond)
    return qs
