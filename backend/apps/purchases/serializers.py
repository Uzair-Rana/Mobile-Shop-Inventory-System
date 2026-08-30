from rest_framework import serializers
from .models import PurchaseOrder, PurchaseOrderLine, Acquisition


class PurchaseOrderLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderLine
        fields = '__all__'
        read_only_fields = ['line_total']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    lines = PurchaseOrderLineSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = '__all__'
        read_only_fields = ['order_number', 'created_by', 'grand_total', 'created_at', 'updated_at']


class PurchaseOrderCreateSerializer(serializers.ModelSerializer):
    lines = PurchaseOrderLineSerializer(many=True)

    class Meta:
        model = PurchaseOrder
        fields = '__all__'
        read_only_fields = ['order_number', 'created_by', 'grand_total']

    def create(self, validated_data):
        lines_data = validated_data.pop('lines', [])
        order = PurchaseOrder.objects.create(**validated_data)
        subtotal = 0
        for ld in lines_data:
            line = PurchaseOrderLine.objects.create(order=order, **ld)
            subtotal += line.line_total
        order.subtotal = subtotal
        order.save()
        return order


class AcquisitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Acquisition
        fields = '__all__'
        read_only_fields = ['acquisition_number', 'created_by', 'created_at']
