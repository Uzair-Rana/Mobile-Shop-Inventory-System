from rest_framework import serializers
from .models import CashSession, CashEntry, Expense


class CashEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = CashEntry
        fields = '__all__'
        read_only_fields = ['session', 'created_by', 'created_at']


class CashSessionSerializer(serializers.ModelSerializer):
    entries = CashEntrySerializer(many=True, read_only=True)
    total_inflows = serializers.SerializerMethodField()
    total_outflows = serializers.SerializerMethodField()

    class Meta:
        model = CashSession
        fields = '__all__'
        read_only_fields = [
            'opened_by', 'closed_by', 'opened_at', 'closed_at',
            'variance', 'expected_closing',
        ]

    def get_total_inflows(self, obj):
        from django.db.models import Sum
        total = obj.entries.filter(type='inflow').aggregate(t=Sum('amount'))['t']
        return str(total or 0)

    def get_total_outflows(self, obj):
        from django.db.models import Sum
        total = obj.entries.filter(type='outflow').aggregate(t=Sum('amount'))['t']
        return str(total or 0)


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at']


class CashEntryCreateSerializer(serializers.Serializer):
    category = serializers.CharField(default='other')
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    note = serializers.CharField(required=False, allow_blank=True)
    reference = serializers.CharField(required=False, allow_blank=True)


class CloseSessionSerializer(serializers.Serializer):
    counted_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    notes = serializers.CharField(required=False, allow_blank=True)
