from rest_framework import serializers
from .models import Supplier, SupplierLedger


class SupplierLedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierLedger
        fields = '__all__'


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'
