from rest_framework import serializers
from .models import DashboardReport, OperationalMetric, HajjYear, Notification, ChatMessage, ChatGroup, GroupMessage
from django.contrib.auth.models import User


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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    recipient_username = serializers.CharField(source='recipient.username', read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'sender_username', 'recipient', 'recipient_username', 'message', 'read', 'created_at']
        read_only_fields = ['created_at', 'sender', 'sender_username', 'recipient_username']


class GroupMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = GroupMessage
        fields = ['id', 'group', 'sender', 'sender_username', 'message', 'created_at']
        read_only_fields = ['created_at', 'sender', 'sender_username']


class ChatGroupSerializer(serializers.ModelSerializer):
    members_data = UserSerializer(source='members', many=True, read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = ChatGroup
        fields = ['id', 'name', 'description', 'created_by', 'created_by_username', 'members', 'members_data', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'created_by_username']
