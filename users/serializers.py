from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserRole, AuditLog


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'is_active']
        read_only_fields = ['id']


class BankDisplaySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

class UserRoleSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    bank_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    bank = BankDisplaySerializer(read_only=True)

    class Meta:
        model = UserRole
        fields = ['id', 'user', 'user_id', 'role', 'bank', 'bank_id', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'bank': {'required': False, 'allow_null': True}
        }

    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        bank_id = validated_data.pop('bank_id', None)

        user = User.objects.get(id=user_id)
        validated_data['user'] = user

        if bank_id:
            from banks.models import Bank
            try:
                bank = Bank.objects.get(id=bank_id)
                validated_data['bank'] = bank
            except Bank.DoesNotExist:
                raise serializers.ValidationError({'bank_id': 'Bank not found'})

        return super().create(validated_data)


class AuditLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'action', 'model_name', 'object_id', 'description', 'ip_address', 'created_at']
        read_only_fields = ['id', 'created_at']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
