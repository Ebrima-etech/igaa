from django.contrib import admin
from .models import Pilgrim, PilgrimDocument


@admin.register(Pilgrim)
class PilgrimAdmin(admin.ModelAdmin):
    list_display = ['registration_id', 'full_name', 'email', 'phone', 'status', 'total_amount_paid', 'created_at']
    list_filter = ['status', 'gender', 'nationality', 'created_at']
    search_fields = ['registration_id', 'first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Personal Information', {
            'fields': ('registration_id', 'first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'gender')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'postal_code', 'country')
        }),
        ('Travel Documents', {
            'fields': ('nationality', 'passport_number')
        }),
        ('Payment Status', {
            'fields': ('status', 'total_amount_due', 'total_amount_paid')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_email')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PilgrimDocument)
class PilgrimDocumentAdmin(admin.ModelAdmin):
    list_display = ['pilgrim', 'document_type', 'uploaded_at']
    list_filter = ['document_type', 'uploaded_at']
    search_fields = ['pilgrim__registration_id', 'pilgrim__first_name', 'pilgrim__last_name']
    readonly_fields = ['uploaded_at']
