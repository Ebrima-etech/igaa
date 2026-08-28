from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserRole, AuditLog


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active']
        read_only_fields = ['id']


class UserRoleSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserRole
        fields = ['id', 'user', 'role', 'bank', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class AuditLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'action', 'model_name', 'object_id', 'description', 'ip_address', 'created_at']
        read_only_fields = ['id', 'created_at']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
