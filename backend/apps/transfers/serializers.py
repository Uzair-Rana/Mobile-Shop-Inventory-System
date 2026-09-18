from rest_framework import serializers
from .models import Transfer, TransferItem


class TransferItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferItem
        fields = '__all__'
        read_only_fields = ['transfer']


class TransferSerializer(serializers.ModelSerializer):
    items = TransferItemSerializer(many=True, read_only=True)
    from_branch_name = serializers.CharField(source='from_branch.name', read_only=True)
    to_branch_name = serializers.CharField(source='to_branch.name', read_only=True)

    class Meta:
        model = Transfer
        fields = '__all__'
        read_only_fields = [
            'transfer_number', 'created_by',
            'dispatched_by', 'received_by',
            'dispatched_at', 'received_at',
            'created_at', 'updated_at',
            'from_branch_name', 'to_branch_name',
        ]


class TransferCreateSerializer(serializers.ModelSerializer):
    items = TransferItemSerializer(many=True)

    class Meta:
        model = Transfer
        fields = '__all__'
        read_only_fields = ['transfer_number', 'created_by']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        transfer = Transfer.objects.create(**validated_data)
        for item in items_data:
            TransferItem.objects.create(transfer=transfer, **item)
        return transfer
