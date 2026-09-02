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
        default='GMD',
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


class Signatory(models.Model):
    """Individual signatory for official receipts"""

    signatory_name = models.CharField(
        max_length=255,
        help_text='Name of the authorized signatory'
    )
    signatory_title = models.CharField(
        max_length=255,
        help_text='Title/position of the signatory'
    )
    digital_signature = models.ImageField(
        upload_to='receipts/signatures/',
        blank=True,
        null=True,
        help_text='Digital signature image (PNG/JPG recommended, transparent background)'
    )
    official_stamp = models.ImageField(
        upload_to='receipts/stamps/',
        blank=True,
        null=True,
        help_text='Official stamp/seal image (PNG/JPG recommended, transparent background)'
    )
    stamp_color = models.CharField(
        max_length=7,
        default='#16a34a',
        help_text='Color of the stamp (hex format, e.g., #16a34a for green)'
    )
    email = models.EmailField(
        blank=True,
        help_text='Signatory email'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text='Signatory phone number'
    )
    is_active = models.BooleanField(
        default=False,
        help_text='Active signatory for receipt generation'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Signatories'
        ordering = ['-is_active', '-created_at']

    def __str__(self):
        return f'{self.signatory_name} ({self.signatory_title})'

    def save(self, *args, **kwargs):
        # Ensure only one active signatory
        if self.is_active:
            Signatory.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class SignatorySettings(models.Model):
    """Global signatory settings (bank contact info for receipts)"""

    bank_contact_email = models.EmailField(
        default='support@giabanking.gm',
        help_text='Bank contact email for receipt footer'
    )
    bank_contact_phone = models.CharField(
        max_length=20,
        default='+220 XXX XXXX',
        help_text='Bank contact phone for receipt footer'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Signatory Settings'

    def __str__(self):
        return 'Global Signatory Settings'


class EmailNotification(models.Model):
    """Store email addresses for payment and receipt notifications"""

    email = models.EmailField(unique=True)
    description = models.CharField(
        max_length=255,
        blank=True,
        help_text='Description for this email recipient (e.g., Admin, Finance Team)'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this email should receive notifications'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Email Notifications'

    def __str__(self):
        return f'{self.email} ({self.description or "No description"})' if self.description else self.email


class EmailNotificationSettings(models.Model):
    """Global configuration for email notifications"""

    enable_notifications = models.BooleanField(
        default=True,
        help_text='Enable or disable all email notifications'
    )
    notify_on_payment = models.BooleanField(
        default=True,
        help_text='Send notification when new payment is created'
    )
    notify_on_receipt = models.BooleanField(
        default=False,
        help_text='Send notification when receipt is generated'
    )
    notification_delay = models.IntegerField(
        default=0,
        help_text='Delay before sending notification in minutes (0 = immediate)'
    )
    email_from = models.EmailField(
        default='noreply@giabanking.gm',
        help_text='Email address to send notifications from'
    )
    email_subject = models.CharField(
        max_length=255,
        default='GIA Banking Notification',
        help_text='Subject line for notification emails'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Email Notification Settings'

    def __str__(self):
        return 'Email Notification Settings'

    @classmethod
    def get_settings(cls):
        """Get or create default settings"""
        settings, _ = cls.objects.get_or_create(id=1)
        return settings
