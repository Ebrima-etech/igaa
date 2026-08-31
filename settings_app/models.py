# settings_app/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class CurrencySettings(models.Model):
    """Store user's currency preferences and settings"""

    CURRENCY_CHOICES = [
        ('GMD', 'Gambian Dalasi'),
        ('USD', 'US Dollar'),
        ('GBP', 'British Pound'),
        ('EUR', 'Euro'),
    ]

    MODE_CHOICES = [
        ('manual', 'Manual - Admin configured rates'),
        ('realtime', 'Real-Time - API-based rates'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='currency_settings',
        help_text='User who owns these currency settings'
    )
    default_currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='USD',
        help_text='Default currency for displays'
    )
    base_currency = models.CharField(
        max_length=3,
        default='GMD',
        help_text='Base currency for conversions'
    )
    mode = models.CharField(
        max_length=20,
        choices=MODE_CHOICES,
        default='manual',
        help_text='Currency rate mode (manual or realtime)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Currency Settings'
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.user.username} - {self.mode.title()} Mode'


class CurrencyRate(models.Model):
    """Individual currency rates associated with user settings"""

    CURRENCY_CODES = [
        ('GMD', 'GMD'),
        ('USD', 'USD'),
        ('GBP', 'GBP'),
        ('EUR', 'EUR'),
    ]

    settings = models.ForeignKey(
        CurrencySettings,
        on_delete=models.CASCADE,
        related_name='currencies',
        help_text='Parent currency settings'
    )
    code = models.CharField(
        max_length=3,
        choices=CURRENCY_CODES,
        help_text='ISO 4217 currency code'
    )
    name = models.CharField(
        max_length=100,
        help_text='Full currency name'
    )
    symbol = models.CharField(
        max_length=5,
        help_text='Currency symbol (e.g., $, £, €)'
    )
    rate = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        validators=[MinValueValidator(0)],
        help_text='Exchange rate relative to base currency'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('settings', 'code')
        verbose_name_plural = 'Currency Rates'
        ordering = ['code']

    def __str__(self):
        return f'{self.code} - {float(self.rate):.6f} ({self.name})'


class SystemSettings(models.Model):
    """Global system settings for Hajj operations"""

    hajj_package_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Default Hajj package price used for all pilgrims'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'System Settings'

    def __str__(self):
        return f'System Settings - Hajj Package: D{self.hajj_package_price}'
