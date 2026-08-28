from django.contrib import admin
from .models import Bank, BankAccount, BankPaymentSubmission, PaymentMethod


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'country', 'is_active', 'created_at']
    list_filter = ['is_active', 'country', 'created_at']
    search_fields = ['name', 'code', 'contact_email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['bank', 'account_username', 'is_verified', 'last_sync', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['bank__name', 'account_username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(BankPaymentSubmission)
class BankPaymentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'bank', 'pilgrim_id', 'amount', 'status', 'submission_method', 'submitted_at']
    list_filter = ['status', 'submission_method', 'bank', 'submitted_at']
    search_fields = ['reference_number', 'pilgrim_id', 'bank__name']
    readonly_fields = ['submitted_at', 'verified_at']


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['bank', 'method_type', 'is_enabled', 'created_at']
    list_filter = ['method_type', 'is_enabled', 'created_at']
    search_fields = ['bank__name']
    readonly_fields = ['created_at']
