# settings_app/admin.py
from django.contrib import admin
from .models import CurrencySettings, CurrencyRate, SignatorySettings, Signatory


class CurrencyRateInline(admin.TabularInline):
    """Inline admin for currency rates"""
    model = CurrencyRate
    extra = 0
    fields = ('code', 'name', 'symbol', 'rate', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('code',)

    def get_queryset(self, request):
        """Order by code"""
        qs = super().get_queryset(request)
        return qs.order_by('code')


@admin.register(CurrencySettings)
class CurrencySettingsAdmin(admin.ModelAdmin):
    """Admin interface for currency settings"""
    inlines = [CurrencyRateInline]

    list_display = (
        'user',
        'mode',
        'default_currency',
        'base_currency',
        'currency_count',
        'updated_at'
    )
    list_filter = ('mode', 'default_currency', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'currency_preview')

    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Currency Configuration', {
            'fields': (
                'mode',
                'default_currency',
                'base_currency',
                'currency_preview'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def currency_count(self, obj):
        """Display number of configured currencies"""
        count = obj.currencies.count()
        return f'{count} currencies'
    currency_count.short_description = 'Currencies'

    def currency_preview(self, obj):
        """Display preview of all configured currencies"""
        if not obj.pk:
            return 'Save the settings first to add currencies'

        currencies = obj.currencies.all()
        if not currencies.exists():
            return 'No currencies configured'

        html = '<table style="width: 100%; border-collapse: collapse;">'
        html += '<thead><tr style="background-color: #f8f9fa;">'
        html += '<th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Code</th>'
        html += '<th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Name</th>'
        html += '<th style="border: 1px solid #ddd; padding: 8px; text-align: center;">Symbol</th>'
        html += '<th style="border: 1px solid #ddd; padding: 8px; text-align: right;">Rate</th>'
        html += '</tr></thead><tbody>'

        for currency in currencies:
            html += f'<tr>'
            html += f'<td style="border: 1px solid #ddd; padding: 8px;"><strong>{currency.code}</strong></td>'
            html += f'<td style="border: 1px solid #ddd; padding: 8px;">{currency.name}</td>'
            html += f'<td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{currency.symbol}</td>'
            html += f'<td style="border: 1px solid #ddd; padding: 8px; text-align: right;">{currency.rate:.6f}</td>'
            html += f'</tr>'

        html += '</tbody></table>'
        return html

    currency_preview.short_description = 'Currency Rates Preview'

    def get_readonly_fields(self, request, obj=None):
        """Make certain fields read-only after creation"""
        if obj:  # Editing existing object
            return self.readonly_fields + ('user',)
        return self.readonly_fields


@admin.register(Signatory)
class SignatoryAdmin(admin.ModelAdmin):
    """Admin interface for individual signatories"""

    list_display = (
        'signatory_name',
        'signatory_title',
        'has_signature',
        'has_stamp',
        'is_active',
        'updated_at'
    )
    list_filter = ('is_active', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at', 'signature_preview', 'stamp_preview')

    fieldsets = (
        ('Signatory Information', {
            'fields': ('signatory_name', 'signatory_title', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone')
        }),
        ('Digital Signature', {
            'fields': ('digital_signature', 'signature_preview'),
            'description': 'Upload a digital signature image (PNG/JPG, transparent background recommended)'
        }),
        ('Official Stamp', {
            'fields': ('official_stamp', 'stamp_color', 'stamp_preview'),
            'description': 'Upload an official stamp/seal image (PNG/JPG, transparent background recommended)'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_signature(self, obj):
        """Display if signature is uploaded"""
        return '✓' if obj.digital_signature else '✗'
    has_signature.short_description = 'Signature'
    has_signature.boolean = True

    def has_stamp(self, obj):
        """Display if stamp is uploaded"""
        return '✓' if obj.official_stamp else '✗'
    has_stamp.short_description = 'Stamp'
    has_stamp.boolean = True

    def signature_preview(self, obj):
        """Display preview of uploaded signature"""
        if not obj.pk or not obj.digital_signature:
            return 'No signature uploaded'
        html = f'<img src="{obj.digital_signature.url}" style="max-width: 200px; max-height: 100px; border: 1px solid #ddd; padding: 5px;" />'
        return html
    signature_preview.short_description = 'Signature Preview'

    def stamp_preview(self, obj):
        """Display preview of uploaded stamp"""
        if not obj.pk or not obj.official_stamp:
            return 'No stamp uploaded'
        html = f'<img src="{obj.official_stamp.url}" style="max-width: 200px; max-height: 200px; border: 1px solid #ddd; padding: 5px;" />'
        return html
    stamp_preview.short_description = 'Stamp Preview'

    def get_readonly_fields(self, request, obj=None):
        """Make preview fields read-only"""
        readonly = list(self.readonly_fields)
        if obj and obj.pk:
            if obj.digital_signature:
                readonly.append('digital_signature')
            if obj.official_stamp:
                readonly.append('official_stamp')
        return readonly


@admin.register(SignatorySettings)
class SignatorySettingsAdmin(admin.ModelAdmin):
    """Admin interface for global signatory settings"""

    list_display = ('bank_contact_email', 'bank_contact_phone', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Contact Information', {
            'fields': ('bank_contact_email', 'bank_contact_phone')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
