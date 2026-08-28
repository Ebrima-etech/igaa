from rest_framework import serializers
from .models import DashboardReport, OperationalMetric


class DashboardReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardReport
        fields = ['id', 'report_type', 'title', 'description', 'data', 'generated_at', 'valid_until']
        read_only_fields = ['generated_at']


class OperationalMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationalMetric
        fields = ['id', 'metric_type', 'value', 'numeric_value', 'unit', 'timestamp']
        read_only_fields = ['timestamp']
