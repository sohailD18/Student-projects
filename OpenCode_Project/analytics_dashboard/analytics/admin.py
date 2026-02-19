from django.contrib import admin
from .models import (
    DataSource, Metric, Dashboard, Widget,
    MetricData, Report, Alert, AlertLog
)


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'source_type', 'is_active', 'last_refreshed', 'created_by', 'created_at']
    list_filter = ['source_type', 'is_active', 'created_at']
    search_fields = ['name', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ['name', 'metric_type', 'unit', 'aggregation_period', 'data_source', 'created_by']
    list_filter = ['metric_type', 'aggregation_period', 'created_at']
    search_fields = ['name', 'description', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at']


class WidgetInline(admin.TabularInline):
    model = Widget
    extra = 0
    fields = ['title', 'widget_type', 'metric', 'position_x', 'position_y', 'width', 'height']


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_public', 'created_by', 'created_at', 'widget_count']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'description', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['viewers']
    inlines = [WidgetInline]

    def widget_count(self, obj):
        return obj.widgets.count()
    widget_count.short_description = 'Widgets'


@admin.register(Widget)
class WidgetAdmin(admin.ModelAdmin):
    list_display = ['title', 'widget_type', 'dashboard', 'metric', 'position_x', 'position_y']
    list_filter = ['widget_type', 'dashboard']
    search_fields = ['title', 'dashboard__name', 'metric__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(MetricData)
class MetricDataAdmin(admin.ModelAdmin):
    list_display = ['metric', 'value', 'timestamp']
    list_filter = ['metric', 'timestamp']
    search_fields = ['metric__name']
    readonly_fields = ['timestamp']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'schedule', 'format', 'is_active', 'last_generated', 'created_by']
    list_filter = ['report_type', 'schedule', 'format', 'is_active', 'created_at']
    search_fields = ['name', 'created_by__username']
    readonly_fields = ['created_at']
    filter_horizontal = ['dashboards', 'recipients']


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['name', 'metric', 'condition_type', 'threshold_value', 'severity', 'is_active', 'trigger_count']
    list_filter = ['condition_type', 'severity', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'metric__name']
    readonly_fields = ['created_at', 'last_triggered', 'trigger_count']


@admin.register(AlertLog)
class AlertLogAdmin(admin.ModelAdmin):
    list_display = ['alert', 'metric_value', 'severity', 'is_acknowledged', 'triggered_at']
    list_filter = ['severity', 'is_acknowledged', 'triggered_at']
    search_fields = ['alert__name', 'message']
    readonly_fields = ['triggered_at', 'acknowledged_at']
