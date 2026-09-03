from rest_framework import serializers
from .models import DashboardReport, OperationalMetric, HajjYear, Notification


class HajjYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = HajjYear
        fields = ['id', 'year', 'name', 'description', 'start_date', 'end_date', 'is_active', 'first_deposit_amount', 'total_package_fee', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


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


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'type', 'title', 'message', 'read', 'action_url', 'created_at']
        read_only_fields = ['created_at']
