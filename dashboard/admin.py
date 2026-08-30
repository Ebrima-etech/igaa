from django.contrib import admin
from .models import DashboardReport, OperationalMetric, HajjYear


@admin.register(HajjYear)
class HajjYearAdmin(admin.ModelAdmin):
    list_display = ['year', 'name', 'is_active', 'start_date', 'end_date']
    list_filter = ['is_active', 'year', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Year Information', {
            'fields': ('year', 'name', 'description')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DashboardReport)
class DashboardReportAdmin(admin.ModelAdmin):
    list_display = ['report_type', 'title', 'generated_at']
    list_filter = ['report_type', 'generated_at']
    search_fields = ['title', 'description']
    readonly_fields = ['generated_at']


@admin.register(OperationalMetric)
class OperationalMetricAdmin(admin.ModelAdmin):
    list_display = ['metric_type', 'value', 'unit', 'timestamp']
    list_filter = ['metric_type', 'timestamp']
    readonly_fields = ['timestamp']
