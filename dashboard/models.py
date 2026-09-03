from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    TYPE_CHOICES = [
        ('success', 'Success'),
        ('error', 'Error'),
        ('warning', 'Warning'),
        ('info', 'Info'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    read = models.BooleanField(default=False)
    action_url = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'read']),
        ]

    def __str__(self):
        return f"{self.title} ({self.type})"


class HajjYear(models.Model):
    """Represents a yearly Hajj event"""
    year = models.IntegerField(unique=True, help_text="The year of the Hajj (e.g., 2026)")
    name = models.CharField(max_length=100, help_text="Display name (e.g., 'GIA Hajj 2026')")
    description = models.TextField(blank=True, help_text="Description of this Hajj year")
    start_date = models.DateField(help_text="Start date of Hajj activities")
    end_date = models.DateField(help_text="End date of Hajj activities")
    is_active = models.BooleanField(default=False, help_text="Currently active Hajj year")
    first_deposit_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Required first deposit amount for pilgrims"
    )
    total_package_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total Hajj package fee"
    )
    notes = models.TextField(blank=True, help_text="Additional notes about this Hajj year")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year']
        verbose_name_plural = "Hajj Years"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Ensure only one active Hajj year at a time
        if self.is_active:
            HajjYear.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class DashboardReport(models.Model):
    REPORT_TYPES = [
        ('payment_summary', 'Payment Summary'),
        ('pilgrim_status', 'Pilgrim Status'),
        ('bank_performance', 'Bank Performance'),
        ('daily_activity', 'Daily Activity'),
    ]

    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    data = models.JSONField(help_text='Report data in JSON format')
    generated_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField()

    class Meta:
        ordering = ['-generated_at']

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.generated_at}"

    def is_valid(self):
        from django.utils import timezone
        return timezone.now() < self.valid_until


class OperationalMetric(models.Model):
    METRIC_TYPES = [
        ('total_pilgrims', 'Total Pilgrims'),
        ('total_paid', 'Total Paid'),
        ('total_pending', 'Total Pending'),
        ('avg_payment_time', 'Average Payment Time'),
        ('bank_count', 'Number of Banks'),
        ('payments_today', 'Payments Today'),
        ('sync_status', 'Sync Status'),
    ]

    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    value = models.CharField(max_length=500)
    numeric_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['metric_type', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.get_metric_type_display()}: {self.value}"
