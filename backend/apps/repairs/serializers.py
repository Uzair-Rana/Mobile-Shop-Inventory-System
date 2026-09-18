from rest_framework import serializers
from .models import RepairJob, RepairStatusLog, RepairPart


class RepairStatusLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairStatusLog
        fields = '__all__'


class RepairPartSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairPart
        fields = '__all__'


class RepairJobSerializer(serializers.ModelSerializer):
    logs = RepairStatusLogSerializer(many=True, read_only=True)
    parts = RepairPartSerializer(many=True, read_only=True)

    class Meta:
        model = RepairJob
        fields = '__all__'
        read_only_fields = ['job_number', 'created_by']
