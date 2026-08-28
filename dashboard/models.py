from django.db import models


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
