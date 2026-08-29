from django.db import models
from pilgrim.models import Pilgrim


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    pilgrim = models.ForeignKey(Pilgrim, on_delete=models.CASCADE, related_name='payments')
    bank = models.ForeignKey('banks.Bank', on_delete=models.SET_NULL, null=True, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference_number = models.CharField(max_length=100, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    payment_date = models.DateField()
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    # Payer Information (who made the deposit)
    payer_name = models.CharField(max_length=100, blank=True)
    payer_contact = models.CharField(max_length=100, blank=True)
    payer_relationship = models.CharField(max_length=50, blank=True, help_text='Relationship to pilgrim')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['pilgrim', 'status']),
            models.Index(fields=['bank', 'status']),
            models.Index(fields=['payment_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Payment {self.reference_number} - {self.pilgrim.full_name}"


class PaymentSynchronization(models.Model):
    SYNC_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('synced', 'Synced'),
        ('failed', 'Failed'),
    ]

    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='sync_record')
    bank_submission_id = models.CharField(max_length=100, unique=True, db_index=True)
    sync_status = models.CharField(max_length=20, choices=SYNC_STATUS_CHOICES, default='pending')
    submission_method = models.CharField(max_length=20, choices=[
        ('manual_form', 'Manual Form'),
        ('csv_upload', 'CSV Upload'),
        ('api_webhook', 'API Webhook'),
    ])
    sync_timestamp = models.DateTimeField(auto_now=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-sync_timestamp']

    def __str__(self):
        return f"Sync - {self.payment.reference_number} ({self.get_submission_method_display()})"


class Transaction(models.Model):
    ACTION_CHOICES = [
        ('payment_created', 'Payment Created'),
        ('payment_confirmed', 'Payment Confirmed'),
        ('payment_failed', 'Payment Failed'),
        ('payment_refunded', 'Payment Refunded'),
        ('status_updated', 'Status Updated'),
    ]

    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='transactions')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    previous_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.payment.reference_number} - {self.get_action_display()}"
