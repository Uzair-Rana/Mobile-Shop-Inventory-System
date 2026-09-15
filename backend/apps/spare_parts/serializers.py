from rest_framework import serializers
from django.db.models import Sum
from .models import SparePart, SparePartLedger


class SparePartLedgerSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(
        source='actor.get_full_name', read_only=True, default='System')

    class Meta:
        model  = SparePartLedger
        fields = [
            'id', 'part', 'entry_type', 'qty', 'unit_cost',
            'reference', 'note', 'balance_after',
            'actor', 'actor_name', 'created_at',
        ]
        read_only_fields = ['id', 'balance_after', 'actor', 'actor_name', 'created_at']


class StockInSerializer(serializers.Serializer):
    """POST body for a stock-in (purchase/return/opening-balance/adjustment-in)."""
    entry_type = serializers.ChoiceField(choices=[
        'opening_balance', 'purchase', 'return_in', 'adjustment_in', 'transfer_in',
    ])
    qty        = serializers.IntegerField(min_value=1)
    unit_cost  = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False, allow_null=True)
    reference  = serializers.CharField(required=False, allow_blank=True, default='')
    note       = serializers.CharField(required=False, allow_blank=True, default='')


class StockOutSerializer(serializers.Serializer):
    """POST body for a stock-out (repair use / sale / damage / adjustment-out)."""
    entry_type = serializers.ChoiceField(choices=[
        'repair_use', 'sale', 'return_out',
        'adjustment_out', 'transfer_out', 'damaged', 'testing',
    ])
    qty        = serializers.IntegerField(min_value=1)   # we negate it on the backend
    reference  = serializers.CharField(required=False, allow_blank=True, default='')
    note       = serializers.CharField(required=False, allow_blank=True, default='')


class SparePartSerializer(serializers.ModelSerializer):
    stock_on_hand = serializers.SerializerMethodField()
    low_stock     = serializers.SerializerMethodField()
    category_display     = serializers.CharField(
        source='get_category_display', read_only=True)
    display_type_display = serializers.CharField(
        source='get_display_type_display', read_only=True)

    class Meta:
        model  = SparePart
        fields = [
            'id', 'sku', 'name', 'category', 'category_display',
            'brand_compat', 'model_compat', 'description',
            'display_type', 'display_type_display', 'with_frame',
            'camera_position', 'battery_capacity',
            'cost_price', 'sell_price', 'reorder_level',
            'branch', 'is_active',
            'stock_on_hand', 'low_stock',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'stock_on_hand', 'low_stock',
            'category_display', 'display_type_display',
            'created_at', 'updated_at',
        ]

    def get_stock_on_hand(self, obj):
        # Use annotated value if present (bulk-list), else compute
        if hasattr(obj, '_stock'):
            return obj._stock or 0
        return obj.stock_on_hand

    def get_low_stock(self, obj):
        return self.get_stock_on_hand(obj) <= obj.reorder_level


class SparePartDetailSerializer(SparePartSerializer):
    """Like SparePartSerializer but includes the full ledger."""
    ledger = SparePartLedgerSerializer(many=True, read_only=True)

    class Meta(SparePartSerializer.Meta):
        fields = SparePartSerializer.Meta.fields + ['ledger']
