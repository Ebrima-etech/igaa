from rest_framework import serializers
from .models import Bank, BankAccount, BankPaymentSubmission, PaymentMethod


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = [
            'id', 'name', 'code', 'country', 'contact_email', 'contact_phone', 'logo', 'is_active',
            'payment_view_access',
            'access_restricted', 'allowed_days', 'access_start_time', 'access_end_time',
            'location_restricted', 'location_latitude', 'location_longitude', 'location_radius',
            'created_at'
        ]
        read_only_fields = ['created_at']

    def to_representation(self, obj):
        data = super().to_representation(obj)
        if obj.logo:
            request = self.context.get('request')
            if request:
                data['logo'] = request.build_absolute_uri(obj.logo.url)
            else:
                data['logo'] = obj.logo.url
        return data
        extra_kwargs = {
            'code': {'required': False, 'allow_blank': True},
            'country': {'required': False, 'allow_blank': True},
            'contact_email': {'required': False, 'allow_blank': True},
            'contact_phone': {'required': False, 'allow_blank': True},
        }


class BankDisplaySerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()

    def get_logo(self, obj):
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None

    class Meta:
        model = Bank
        fields = ['id', 'name', 'logo', 'is_active']


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
            'submitted_by_user', 'submitted_at', 'verified_at',
            'pilgrim_first_name', 'pilgrim_last_name', 'pilgrim_gender', 'pilgrim_phone', 'pilgrim_email',
            'payer_name', 'payer_contact', 'payer_relationship', 'created_pilgrim_id'
        ]
        read_only_fields = ['submitted_at', 'verified_at', 'bank_name', 'created_pilgrim_id']


class ManualPaymentSubmissionSerializer(serializers.Serializer):
    # Pilgrim Information - Basic
    pilgrim_first_name = serializers.CharField(max_length=100)
    pilgrim_last_name = serializers.CharField(max_length=100)
    pilgrim_gender = serializers.CharField(max_length=1)
    pilgrim_phone = serializers.CharField(max_length=20)
    pilgrim_email = serializers.EmailField(required=False, allow_blank=True)

    # Pilgrim Information - Personal
    pilgrim_date_of_birth = serializers.DateField()
    pilgrim_nationality = serializers.CharField(max_length=100)
    pilgrim_passport_number = serializers.CharField(max_length=50)

    # Pilgrim Information - Address
    pilgrim_address = serializers.CharField()
    pilgrim_city = serializers.CharField(max_length=100)
    pilgrim_state = serializers.CharField(max_length=100, required=False, allow_blank=True)
    pilgrim_postal_code = serializers.CharField(max_length=20, required=False, allow_blank=True)
    pilgrim_country = serializers.CharField(max_length=100)

    # Payer Information
    payer_name = serializers.CharField(max_length=100)
    payer_contact = serializers.CharField(max_length=100, required=False, allow_blank=True)
    payer_relationship = serializers.CharField(max_length=50, required=False, allow_blank=True)

    # Payment Information
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    reference_number = serializers.CharField(max_length=100)
    payment_date = serializers.DateField()
    description = serializers.CharField(required=False, allow_blank=True)


class CSVPaymentUploadSerializer(serializers.Serializer):
    csv_file = serializers.FileField()
