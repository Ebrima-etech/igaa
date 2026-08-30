from django.db import models
from django.contrib.auth.models import User


class UserRole(models.Model):
    ROLE_CHOICES = [
        ('hajj_admin', 'Hajj Company Admin'),
        ('hajj_staff', 'Hajj Company Staff'),
        ('bank_admin', 'Bank Admin'),
        ('bank_staff', 'Bank Staff'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    bank = models.ForeignKey('banks.Bank', on_delete=models.SET_NULL, null=True, blank=True,
                            help_text='Set only for bank users')
    is_active = models.BooleanField(default=True)
    access_restricted = models.BooleanField(default=False, help_text='Enable time-based access restrictions for this user')
    allowed_days = models.CharField(max_length=100, default='Mon,Tue,Wed,Thu,Fri', blank=True, help_text='Comma-separated days (Mon,Tue,Wed,Thu,Fri,Sat,Sun)')
    access_start_time = models.TimeField(null=True, blank=True, help_text='Start time for access (HH:MM format)')
    access_end_time = models.TimeField(null=True, blank=True, help_text='End time for access (HH:MM format)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('payment_submit', 'Payment Submitted'),
        ('payment_confirm', 'Payment Confirmed'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.IntegerField()
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_action_display()} - {self.model_name} by {self.user}"
