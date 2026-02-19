from django.contrib import admin
from .models import Vehicle, Driver, Trip, MaintenanceRecord, Alert


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['plate', 'vin', 'vehicle_type', 'make', 'model', 'year', 'status', 'current_mileage']
    list_filter = ['vehicle_type', 'status', 'created_at']
    search_fields = ['plate', 'vin', 'make', 'model']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('vin', 'plate', 'vehicle_type', 'make', 'model', 'year', 'status')
        }),
        ('Specifications', {
            'fields': ('purchase_date', 'current_mileage', 'fuel_capacity')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'license_number', 'license_type', 'status', 'hire_date']
    list_filter = ['license_type', 'status', 'hire_date']
    search_fields = ['name', 'email', 'license_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ['vehicle', 'driver', 'start_date', 'distance', 'fuel_used', 'status']
    list_filter = ['status', 'start_date', 'vehicle']
    search_fields = ['vehicle__plate', 'driver__name', 'start_location', 'end_location']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_date'


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ['vehicle', 'maintenance_type', 'date', 'mileage_at_service', 'cost', 'severity']
    list_filter = ['maintenance_type', 'severity', 'date']
    search_fields = ['vehicle__plate', 'description', 'performed_by']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['vehicle', 'alert_type', 'severity', 'is_active', 'created_at']
    list_filter = ['alert_type', 'severity', 'is_active', 'created_at']
    search_fields = ['vehicle__plate', 'message']
    readonly_fields = ['created_at', 'updated_at', 'resolved_date']
    actions = ['mark_as_resolved']

    def mark_as_resolved(self, request, queryset):
        """Admin action to mark selected alerts as resolved"""
        count = 0
        for alert in queryset:
            if alert.is_active:
                alert.resolve()
                count += 1
        self.message_user(request, f'{count} alert(s) marked as resolved.')
    mark_as_resolved.short_description = "Mark selected alerts as resolved"
