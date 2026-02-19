"""
Admin configuration for Employee Performance Analysis System
"""
from django.contrib import admin
from .models import Employee, PerformanceRecord


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'role', 'join_date', 'performance_category', 'get_record_count']
    list_filter = ['department', 'performance_category', 'join_date']
    search_fields = ['name', 'role', 'email']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email', 'department', 'role', 'join_date')
        }),
        ('Performance', {
            'fields': ('performance_category',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_record_count(self, obj):
        return obj.get_record_count()
    get_record_count.short_description = 'Records'


@admin.register(PerformanceRecord)
class PerformanceRecordAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'efficiency', 'quality', 'tasks_completed', 'hours_worked', 'get_overall_score']
    list_filter = ['date', 'employee__department', 'employee']
    search_fields = ['employee__name', 'manager_notes']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'

    fieldsets = (
        ('Record Information', {
            'fields': ('employee', 'date', 'hours_worked', 'tasks_completed')
        }),
        ('Performance Metrics', {
            'fields': ('efficiency', 'quality')
        }),
        ('Additional Information', {
            'fields': ('manager_notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_overall_score(self, obj):
        return obj.get_overall_score()
    get_overall_score.short_description = 'Overall Score'
