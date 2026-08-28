from django.db import models
import uuid


class Bank(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='submissions')
    pilgrim_id = models.CharField(max_length=20, db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference_number = models.CharField(max_length=100, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=SUBMISSION_STATUS, default='pending', db_index=True)
    submission_method = models.CharField(max_length=20, choices=SUBMISSION_METHOD)
    payment_date = models.DateField()
    description = models.TextField(blank=True)
    error_message = models.TextField(blank=True)

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
