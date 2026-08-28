from django.contrib import admin
from .models import DashboardReport, OperationalMetric


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
