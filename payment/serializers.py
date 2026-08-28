from rest_framework import serializers
from .models import Payment, PaymentSynchronization, Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'action', 'previous_status', 'new_status', 'description', 'created_at']
        read_only_fields = ['created_at']


class PaymentSynchronizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentSynchronization
        fields = ['id', 'payment', 'sync_status', 'submission_method', 'sync_timestamp', 'error_message']
        read_only_fields = ['sync_timestamp']


class PaymentSerializer(serializers.ModelSerializer):
    sync_record = PaymentSynchronizationSerializer(read_only=True)
    bank_name = serializers.CharField(source='bank.name', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'pilgrim', 'bank', 'bank_name', 'amount', 'reference_number', 'status',
            'payment_date', 'description', 'notes', 'sync_record', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'bank_name']


class PaymentListSerializer(serializers.ModelSerializer):
    pilgrim_name = serializers.CharField(source='pilgrim.full_name', read_only=True)
    bank_name = serializers.CharField(source='bank.name', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'reference_number', 'pilgrim', 'pilgrim_name', 'bank', 'bank_name',
            'amount', 'status', 'payment_date', 'created_at'
        ]
        read_only_fields = ['created_at', 'pilgrim_name', 'bank_name']
