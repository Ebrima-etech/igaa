# settings_app/serializers.py
from rest_framework import serializers
from .models import CurrencySettings, CurrencyRate


class CurrencyRateSerializer(serializers.ModelSerializer):
    """Serializer for individual currency rates"""

    class Meta:
        model = CurrencyRate
        fields = ['code', 'name', 'symbol', 'rate']
        read_only_fields = ['created_at', 'updated_at']

    def validate_rate(self, value):
        """Ensure rate is positive"""
        if value < 0:
            raise serializers.ValidationError("Rate must be positive")
        return value


class CurrencySettingsSerializer(serializers.ModelSerializer):
    """Serializer for currency settings with nested rates"""

    currencies = CurrencyRateSerializer(many=True, write_only=True)

    class Meta:
        model = CurrencySettings
        fields = ['default_currency', 'base_currency', 'mode', 'currencies', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_default_currency(self, value):
        """Validate currency code"""
        valid_codes = ['GMD', 'USD', 'GBP', 'EUR']
        if value not in valid_codes:
            raise serializers.ValidationError(
                f"Invalid currency: {value}. Valid options: {valid_codes}"
            )
        return value

    def validate_base_currency(self, value):
        """Validate base currency code"""
        valid_codes = ['GMD', 'USD', 'GBP', 'EUR']
        if value not in valid_codes:
            raise serializers.ValidationError(
                f"Invalid currency: {value}. Valid options: {valid_codes}"
            )
        return value

    def validate_currencies(self, value):
        """Validate currency list"""
        if not value or len(value) == 0:
            raise serializers.ValidationError("At least one currency is required")

        if not isinstance(value, list):
            raise serializers.ValidationError("Currencies must be a list")

        codes = set()
        for currency in value:
            code = currency.get('code')

            if not code:
                raise serializers.ValidationError("Currency code is required")

            if code in codes:
                raise serializers.ValidationError(f"Duplicate currency code: {code}")

            codes.add(code)

            # Validate all required fields
            if not currency.get('name'):
                raise serializers.ValidationError(f"Currency name is required for {code}")

            if not currency.get('symbol'):
                raise serializers.ValidationError(f"Currency symbol is required for {code}")

            if 'rate' not in currency:
                raise serializers.ValidationError(f"Currency rate is required for {code}")

        return value

    def create(self, validated_data):
        """Create currency settings with nested rates"""
        currencies_data = validated_data.pop('currencies', [])
        user = self.context['request'].user

        # Get or create settings
        settings, created = CurrencySettings.objects.get_or_create(
            user=user,
            defaults=validated_data
        )

        if not created:
            # Update existing settings
            for attr, value in validated_data.items():
                setattr(settings, attr, value)
            settings.save()

        # Delete old rates and create new ones
        settings.currencies.all().delete()

        for currency_data in currencies_data:
            CurrencyRate.objects.create(settings=settings, **currency_data)

        return settings

    def update(self, instance, validated_data):
        """Update currency settings with nested rates"""
        currencies_data = validated_data.pop('currencies', None)

        # Update settings fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update rates if provided
        if currencies_data is not None:
            instance.currencies.all().delete()
            for currency_data in currencies_data:
                CurrencyRate.objects.create(settings=instance, **currency_data)

        return instance

    def to_representation(self, instance):
        """Include currencies in response"""
        ret = super().to_representation(instance)
        ret['currencies'] = CurrencyRateSerializer(
            instance.currencies.all(),
            many=True
        ).data
        return ret
