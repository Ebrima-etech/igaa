from rest_framework import serializers
from .models import Bank, BankAccount, BankPaymentSubmission, PaymentMethod


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ['id', 'name', 'code', 'country', 'contact_email', 'contact_phone', 'is_active', 'created_at']
        read_only_fields = ['created_at']
        extra_kwargs = {
            'code': {'required': False, 'allow_blank': True},
            'country': {'required': False, 'allow_blank': True},
            'contact_email': {'required': False, 'allow_blank': True},
            'contact_phone': {'required': False, 'allow_blank': True},
        }


class BankAccountSerializer(serializers.ModelSerializer):
    bank = BankSerializer(read_only=True)

    class Meta:
        model = BankAccount
        fields = ['id', 'bank', 'account_username', 'api_key', 'webhook_url', 'is_verified', 'last_sync']
        read_only_fields = ['api_key', 'last_sync']
        extra_kwargs = {
            'api_secret': {'write_only': True}
        }


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['id', 'bank', 'method_type', 'is_enabled', 'config', 'created_at']
        read_only_fields = ['created_at']


class BankPaymentSubmissionSerializer(serializers.ModelSerializer):
    bank_name = serializers.CharField(source='bank.name', read_only=True)

    class Meta:
        model = BankPaymentSubmission
        fields = [
            'id', 'bank', 'bank_name', 'pilgrim_id', 'amount', 'reference_number', 'status',
            'submission_method', 'payment_date', 'description', 'error_message',
            'submitted_by_user', 'submitted_at', 'verified_at'
        ]
        read_only_fields = ['submitted_at', 'verified_at', 'bank_name']


class ManualPaymentSubmissionSerializer(serializers.Serializer):
    pilgrim_id = serializers.CharField(max_length=20)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    reference_number = serializers.CharField(max_length=100)
    payment_date = serializers.DateField()
    description = serializers.CharField(required=False, allow_blank=True)


class CSVPaymentUploadSerializer(serializers.Serializer):
    csv_file = serializers.FileField()
