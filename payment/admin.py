from django.contrib import admin
from .models import Payment, PaymentSynchronization, Transaction, Receipt


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['reference_number', 'pilgrim', 'bank', 'amount', 'status', 'payment_date', 'created_at']
    list_filter = ['status', 'bank', 'payment_date', 'created_at']
    search_fields = ['reference_number', 'pilgrim__registration_id', 'pilgrim__email']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Payment Information', {
            'fields': ('pilgrim', 'bank', 'amount', 'reference_number', 'status')
        }),
        ('Details', {
            'fields': ('payment_date', 'description', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PaymentSynchronization)
class PaymentSynchronizationAdmin(admin.ModelAdmin):
    list_display = ['payment', 'sync_status', 'submission_method', 'sync_timestamp']
    list_filter = ['sync_status', 'submission_method', 'sync_timestamp']
    search_fields = ['payment__reference_number', 'bank_submission_id']
    readonly_fields = ['sync_timestamp']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['payment', 'action', 'previous_status', 'new_status', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['payment__reference_number']
    readonly_fields = ['created_at']


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'payment', 'signatory', 'created_at']
    list_filter = ['signatory', 'created_at']
    search_fields = ['receipt_number', 'payment__reference_number']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Receipt Information', {
            'fields': ('receipt_number', 'payment', 'signatory')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
