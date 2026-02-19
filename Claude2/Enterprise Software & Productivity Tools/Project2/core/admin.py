"""
OptiFlow - AI-Based Business Process Optimizer
Admin Interface Configuration
"""

from django.contrib import admin
from .models import BusinessProcess, ProcessStep, OperationalData, Recommendation, ProcessMetric


@admin.register(BusinessProcess)
class BusinessProcessAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'get_total_steps', 'get_completion_rate', 'get_average_cycle_time', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'status')
        }),
        ('Performance Targets', {
            'fields': ('target_cycle_time',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProcessStep)
class ProcessStepAdmin(admin.ModelAdmin):
    list_display = ['process', 'step_order', 'name', 'step_type', 'estimated_duration', 'is_active']
    list_filter = ['step_type', 'is_active', 'process']
    search_fields = ['name', 'description', 'process__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(OperationalData)
class OperationalDataAdmin(admin.ModelAdmin):
    list_display = ['run_id', 'process', 'step', 'status', 'priority', 'execution_time', 'created_at']
    list_filter = ['status', 'priority', 'process', 'created_at']
    search_fields = ['run_id', 'assigned_to', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['title', 'process', 'category', 'priority', 'status', 'impact_score', 'created_at']
    list_filter = ['category', 'priority', 'status', 'created_at']
    search_fields = ['title', 'description', 'recommendation']
    readonly_fields = ['created_at', 'updated_at', 'implemented_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'category', 'priority', 'status')
        }),
        ('Relationships', {
            'fields': ('process', 'step')
        }),
        ('Analysis', {
            'fields': ('description', 'recommendation')
        }),
        ('Metrics', {
            'fields': ('current_value', 'target_value', 'potential_savings', 'impact_score')
        }),
        ('Metadata', {
            'fields': ('analysis_data', 'created_at', 'updated_at', 'implemented_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProcessMetric)
class ProcessMetricAdmin(admin.ModelAdmin):
    list_display = ['process', 'get_metric_type_display', 'value', 'date', 'created_at']
    list_filter = ['metric_type', 'date', 'created_at']
    search_fields = ['process__name']
    readonly_fields = ['created_at']
