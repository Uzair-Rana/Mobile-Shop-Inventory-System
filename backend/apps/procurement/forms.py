from django import forms
from django.forms import inlineformset_factory

from .models import Procurement, ProcurementItem


class ProcurementForm(forms.ModelForm):
    # Optional: create a brand-new supplier inline instead of picking an existing one.
    new_supplier = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input',
                                      'placeholder': '…or type a new supplier name'}),
    )

    class Meta:
        model = Procurement
        fields = ['supplier', 'date', 'invoice_no', 'notes']
        widgets = {
            'supplier':   forms.Select(attrs={'class': 'form-select'}),
            'date':       forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'invoice_no': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Supplier invoice #'}),
            'notes':      forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show every supplier in the dropdown, alphabetically.
        from apps.suppliers.models import Supplier
        self.fields['supplier'].queryset = Supplier.objects.order_by('name')
        self.fields['supplier'].empty_label = '— Select a supplier —'

    def save(self, commit=True):
        obj = super().save(commit=False)
        name = (self.cleaned_data.get('new_supplier') or '').strip()
        if name:
            from apps.suppliers.models import Supplier
            supplier = Supplier.objects.filter(name__iexact=name).first()
            if not supplier:
                supplier = Supplier.objects.create(name=name)
            obj.supplier = supplier
        if commit:
            obj.save()
            self.save_m2m()
        return obj


class ProcurementItemForm(forms.ModelForm):
    class Meta:
        model = ProcurementItem
        fields = ['category', 'product', 'sku', 'brand', 'qty', 'unit_cost', 'sell_price',
                  'low_stock_alert', 'imeis', 'pta_status', 'condition', 'spare_category']
        widgets = {
            'category':   forms.Select(attrs={'class': 'form-select cat-select'}),
            'product':    forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Name / model',
                                                 'list': 'existing-product-names', 'autocomplete': 'off'}),
            'sku':        forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'SKU (optional)',
                                                 'list': 'existing-product-skus', 'autocomplete': 'off'}),
            'brand':      forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Brand'}),
            'qty':        forms.NumberInput(attrs={'class': 'form-input', 'min': 1}),
            'unit_cost':  forms.NumberInput(attrs={'class': 'form-input', 'min': 0, 'step': '0.01'}),
            'sell_price': forms.NumberInput(attrs={'class': 'form-input', 'min': 0, 'step': '0.01'}),
            'low_stock_alert': forms.NumberInput(attrs={'class': 'form-input low-stock-field', 'min': 0,
                                                        'placeholder': 'e.g. 5'}),
            'imeis':      forms.Textarea(attrs={'class': 'form-textarea imei-field', 'rows': 2,
                                                'placeholder': 'One IMEI per line (or comma separated)'}),
            'pta_status': forms.Select(attrs={'class': 'form-select'}),
            'condition':  forms.Select(attrs={'class': 'form-select'}),
            'spare_category': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # PTA / condition choices come from Developer Options → Dropdown Options.
        from apps.settings_app.choices import options
        for name, group in (('pta_status', 'pta_status'), ('condition', 'device_condition')):
            current = getattr(self.instance, name, '') or None
            self.fields[name].widget.choices = [(o, o) for o in options(group, include=current)]
        from apps.spare_parts.models import SparePart
        self.fields['spare_category'].widget.choices = SparePart.Category.choices

    def clean(self):
        data = super().clean()
        if data.get('DELETE'):
            return data
        category = data.get('category')
        product = data.get('product')
        qty = data.get('qty') or 0
        if not category or not product:
            return data  # blank/extra row — formset handles emptiness

        if category == 'imei':
            import re
            imeis = [t for t in re.split(r'[\s,]+', (data.get('imeis') or '').strip()) if t]
            if not imeis:
                self.add_error('imeis', 'Enter at least one IMEI for IMEI devices.')
            elif len(imeis) != qty:
                self.add_error('qty', f'Qty ({qty}) must equal number of IMEIs entered ({len(imeis)}).')
            # unique within this line
            if len(set(imeis)) != len(imeis):
                self.add_error('imeis', 'Duplicate IMEIs in this line.')
            # An IMEI already in stock can't be bought again (a sold phone can —
            # that's a buy-back). On edit, this line's own IMEIs are fine.
            from apps.inventory.models import Unit
            own = set(self.instance.imei_list()) if self.instance.pk else set()
            clash = (Unit.objects.filter(imei1__in=imeis, lifecycle_state='in_stock')
                     .exclude(imei1__in=own).values_list('imei1', flat=True))
            if clash:
                self.add_error('imeis', 'Already in stock: ' + ', '.join(clash))
            from apps.settings_app.choices import options
            if not data.get('pta_status'):
                data['pta_status'] = (options('pta_status') or ['PTA Approved'])[0]
            if not data.get('condition'):
                data['condition'] = (options('device_condition') or ['Grade A'])[0]
            data['low_stock_alert'] = None   # serialised devices have no threshold
        else:
            if qty < 1:
                self.add_error('qty', 'Quantity must be at least 1.')
        return data


ProcurementItemFormSet = inlineformset_factory(
    Procurement, ProcurementItem, form=ProcurementItemForm,
    extra=1, can_delete=True,
)
