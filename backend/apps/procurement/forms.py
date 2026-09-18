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
        fields = ['category', 'product', 'sku', 'brand', 'qty', 'unit_cost', 'sell_price', 'imeis']
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
            'imeis':      forms.Textarea(attrs={'class': 'form-textarea imei-field', 'rows': 2,
                                                'placeholder': 'One IMEI per line (or comma separated)'}),
        }

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
        else:
            if qty < 1:
                self.add_error('qty', 'Quantity must be at least 1.')
        return data


ProcurementItemFormSet = inlineformset_factory(
    Procurement, ProcurementItem, form=ProcurementItemForm,
    extra=1, can_delete=True,
)
