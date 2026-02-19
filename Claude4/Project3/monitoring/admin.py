"""
Django Admin Configuration for Monitoring App
"""

from django.contrib import admin
from .models import SafetyIncident, SystemMetrics, RestrictedZone, CameraConfig


@admin.register(SafetyIncident)
class SafetyIncidentAdmin(admin.ModelAdmin):
    """Admin interface for SafetyIncident model."""
    list_display = ['incident_id', 'hazard_type', 'timestamp', 'confidence_percentage', 'camera_id', 'is_resolved']
    list_filter = ['hazard_type', 'is_resolved', 'timestamp', 'camera_id']
    search_fields = ['camera_id', 'notes']
    readonly_fields = ['timestamp', 'incident_id']
    date_hierarchy = 'timestamp'
    list_per_page = 25


@admin.register(SystemMetrics)
class SystemMetricsAdmin(admin.ModelAdmin):
    """Admin interface for SystemMetrics model."""
    list_display = ['date', 'workers_detected', 'total_violations', 'safety_score', 'monitoring_hours']
    list_filter = ['date']
    readonly_fields = ['date']


@admin.register(RestrictedZone)
class RestrictedZoneAdmin(admin.ModelAdmin):
    """Admin interface for RestrictedZone model."""
    list_display = ['name', 'coordinates', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']

    def coordinates(self, obj):
        """Display zone coordinates."""
        return f"({obj.x1}, {obj.y1}) to ({obj.x2}, {obj.y2})"


@admin.register(CameraConfig)
class CameraConfigAdmin(admin.ModelAdmin):
    """Admin interface for CameraConfig model."""
    list_display = ['camera_id', 'name', 'camera_type', 'source_path', 'is_active', 'fps']
    list_filter = ['camera_type', 'is_active']
    search_fields = ['camera_id', 'name', 'source_path']
