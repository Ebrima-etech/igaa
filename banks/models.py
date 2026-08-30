from django.db import models
import uuid


class Bank(models.Model):
    PAYMENT_ACCESS_CHOICES = [
        ('date_restricted', 'Date Filter Only - Admin can only view payments using date filter'),
        ('unrestricted', 'Unrestricted - Admin can view all payments without date filter'),
    ]

    name = models.CharField(max_length=100, unique=True, db_index=True)
    code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    logo = models.ImageField(upload_to='banks/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    payment_view_access = models.CharField(
        max_length=20,
        choices=PAYMENT_ACCESS_CHOICES,
        default='date_restricted',
        help_text='Controls what payment data bank admins can view'
    )
    access_restricted = models.BooleanField(default=False, help_text='Enable time-based access restrictions for this bank')
    allowed_days = models.CharField(max_length=100, default='Mon,Tue,Wed,Thu,Fri', blank=True, help_text='Comma-separated days (Mon,Tue,Wed,Thu,Fri,Sat,Sun)')
    access_start_time = models.TimeField(null=True, blank=True, help_text='Start time for access (HH:MM format)')
    access_end_time = models.TimeField(null=True, blank=True, help_text='End time for access (HH:MM format)')
    location_restricted = models.BooleanField(default=False, help_text='Enable location-based access restrictions for this bank')
    location_latitude = models.FloatField(null=True, blank=True, help_text='Latitude coordinate for access location')
    location_longitude = models.FloatField(null=True, blank=True, help_text='Longitude coordinate for access location')
    location_radius = models.FloatField(default=1, help_text='Allowed access radius in kilometers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class BankAccount(models.Model):
    bank = models.OneToOneField(Bank, on_delete=models.CASCADE, related_name='account')
    account_username = models.CharField(max_length=100, unique=True)
    api_key = models.CharField(max_length=255, unique=True)
    api_secret = models.CharField(max_length=255)
    webhook_url = models.URLField(blank=True)
    webhook_secret = models.CharField(max_length=255, blank=True)
    is_verified = models.BooleanField(default=False)
    last_sync = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Bank Accounts'

    def __str__(self):
        return f"{self.bank.name} Account"


class BankPaymentSubmission(models.Model):
    SUBMISSION_STATUS = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('failed', 'Failed'),
    ]

    SUBMISSION_METHOD = [
        ('manual_form', 'Manual Form'),
        ('csv_upload', 'CSV Upload'),
        ('api_webhook', 'API Webhook'),
    ]

    GENDER_CHOICES = [
        ('M', 'Male (Alagie)'),
        ('F', 'Female (Aja)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='submissions')
    pilgrim = models.ForeignKey('pilgrim.Pilgrim', on_delete=models.SET_NULL, null=True, blank=True, related_name='bank_submissions')
    pilgrim_registration_id = models.CharField(max_length=20, db_index=True, blank=True, help_text='Pilgrim registration ID from bank submission')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference_number = models.CharField(max_length=100, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=SUBMISSION_STATUS, default='pending', db_index=True)
    submission_method = models.CharField(max_length=20, choices=SUBMISSION_METHOD)
    payment_date = models.DateField()
    description = models.TextField(blank=True)
    error_message = models.TextField(blank=True)

    # Pilgrim Information (collected at bank)
    pilgrim_first_name = models.CharField(max_length=100, blank=True)
    pilgrim_last_name = models.CharField(max_length=100, blank=True)
    pilgrim_gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    pilgrim_phone = models.CharField(max_length=20, blank=True)
    pilgrim_email = models.EmailField(blank=True)

    # Payer Information (who made the deposit)
    payer_name = models.CharField(max_length=100, blank=True)
    payer_contact = models.CharField(max_length=100, blank=True)
    payer_relationship = models.CharField(max_length=50, blank=True, help_text='Relationship to pilgrim: Self, Parent, Spouse, etc.')

    # Link to created pilgrim (after GIA creates them)
    created_pilgrim_id = models.IntegerField(null=True, blank=True, db_index=True)

    submitted_by_user = models.CharField(max_length=100, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['bank', 'status']),
            models.Index(fields=['pilgrim_id', 'status']),
            models.Index(fields=['submitted_at']),
        ]

    def __str__(self):
        return f"{self.bank.name} - {self.reference_number}"


class PaymentMethod(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='payment_methods')
    method_type = models.CharField(max_length=20, choices=[
        ('manual_form', 'Manual Form Entry'),
        ('csv_upload', 'CSV Bulk Upload'),
        ('api_webhook', 'API Webhook Integration'),
    ])
    is_enabled = models.BooleanField(default=True)
    config = models.JSONField(default=dict, blank=True, help_text='JSON configuration for the payment method')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('bank', 'method_type')
        verbose_name_plural = 'Payment Methods'

    def __str__(self):
        return f"{self.bank.name} - {self.get_method_type_display()}"
