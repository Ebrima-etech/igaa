from rest_framework import serializers
from .models import Pilgrim, PilgrimDocument


class PilgrimDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PilgrimDocument
        fields = ['id', 'document_type', 'document_file', 'issue_date', 'expiry_date', 'uploaded_at']
        read_only_fields = ['uploaded_at']


class PilgrimSerializer(serializers.ModelSerializer):
    documents = PilgrimDocumentSerializer(many=True, read_only=True)
    amount_remaining = serializers.SerializerMethodField()

    class Meta:
        model = Pilgrim
        fields = [
            'id', 'registration_id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'date_of_birth', 'gender', 'nationality', 'passport_number', 'address', 'city',
            'state', 'postal_code', 'country', 'status', 'total_amount_due', 'total_amount_paid',
            'amount_remaining', 'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_email', 'documents', 'created_at', 'updated_at'
        ]
        read_only_fields = ['registration_id', 'created_at', 'updated_at', 'full_name', 'amount_remaining']

    def get_amount_remaining(self, obj):
        return obj.amount_remaining


class PilgrimListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return obj.full_name

    class Meta:
        model = Pilgrim
        fields = [
            'id', 'registration_id', 'full_name', 'phone', 'status',
            'total_amount_due', 'total_amount_paid', 'created_at'
        ]
        read_only_fields = ['registration_id', 'created_at', 'full_name']
