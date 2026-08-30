from rest_framework import serializers
from .models import InstallmentPlan, InstallmentSchedule, InstallmentPayment


class InstallmentScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallmentSchedule
        fields = '__all__'
        read_only_fields = ['plan']


class InstallmentPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallmentPayment
        fields = '__all__'
        read_only_fields = ['collected_by', 'collected_at']


class InstallmentPlanSerializer(serializers.ModelSerializer):
    schedule = InstallmentScheduleSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)

    class Meta:
        model = InstallmentPlan
        fields = '__all__'
        read_only_fields = [
            'plan_number', 'created_by', 'balance_remaining',
            'created_at', 'updated_at', 'customer_name',
        ]


class InstallmentPlanCreateSerializer(serializers.ModelSerializer):
    """Used for POST — auto-generates the schedule on create."""

    class Meta:
        model = InstallmentPlan
        exclude = ['plan_number', 'created_by', 'balance_remaining', 'schedule']
        extra_kwargs = {
            'financed_amount': {'required': False},
            'total_payable': {'required': False},
            'installment_amount': {'required': False},
            'balance_remaining': {'required': False},
        }

    def validate(self, data):
        sale = data.get('sale_amount', 0)
        down = data.get('down_payment', 0)
        markup = data.get('markup_rate', 0)
        count = data.get('installment_count', 1)

        financed = sale - down
        total_payable = financed * (1 + markup / 100)
        installment_amount = total_payable / count

        data['financed_amount'] = round(financed, 2)
        data['total_payable'] = round(total_payable, 2)
        data['installment_amount'] = round(installment_amount, 2)
        data['balance_remaining'] = round(total_payable, 2)
        return data


class CollectPaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    payment_method = serializers.CharField(default='cash')
    reference = serializers.CharField(required=False, allow_blank=True)
    schedule_item_id = serializers.IntegerField(required=False, allow_null=True)
