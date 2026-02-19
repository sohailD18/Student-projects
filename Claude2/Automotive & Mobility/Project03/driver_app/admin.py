from django.contrib import admin
from .models import DriverData


@admin.register(DriverData)
class DriverDataAdmin(admin.ModelAdmin):
    """
    Admin interface for DriverData model.
    Provides a comprehensive view of driver behavior records.
    """
    list_display = [
        'driver_name',
        'trip_date',
        'average_speed',
        'max_speed',
        'harsh_braking_events',
        'rapid_acceleration_events',
        'risk_score',
        'behavior_class',
    ]
    list_filter = ['behavior_class', 'trip_date']
    search_fields = ['driver_name']
    date_hierarchy = 'trip_date'

    fieldsets = (
        ('Driver Information', {
            'fields': ('driver_name', 'trip_date')
        }),
        ('Driving Metrics', {
            'fields': (
                'average_speed',
                'max_speed',
                'cornering_speed',
                'harsh_braking_events',
                'rapid_acceleration_events'
            )
        }),
        ('AI Analysis Results', {
            'fields': ('risk_score', 'behavior_class', 'recommendations'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('risk_score', 'behavior_class', 'recommendations')
