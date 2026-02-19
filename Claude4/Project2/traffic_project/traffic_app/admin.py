"""
Django Admin Configuration for Traffic App

This module registers the TrafficData model with the Django admin interface,
allowing administrators to manage traffic data records manually.
"""

from django.contrib import admin
from .models import TrafficData


@admin.register(TrafficData)
class TrafficDataAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for TrafficData model.

    Features:
        - List display with key fields
        - Searchable by location
        - Filterable by weather and congestion level
        - Date hierarchy for easy navigation
        - Read-only calculated fields
    """

    # Columns displayed in list view
    list_display = [
        'date_time',
        'location',
        'vehicle_count',
        'weather',
        'congestion_level',
        'hour_of_day',
    ]

    # Add calculated field as read-only
    readonly_fields = ['hour_of_day', 'day_of_week']

    # Fields to search
    search_fields = ['location', 'congestion_level']

    # Fields to filter by
    list_filter = ['weather', 'congestion_level', 'location', 'date_time']

    # Date hierarchy for drilling down by date
    date_hierarchy = 'date_time'

    # Number of items per page
    list_per_page = 25

    # Ordering of items
    ordering = ['-date_time']

    # Fieldsets for organizing the form layout
    fieldsets = (
        ('Traffic Information', {
            'fields': ('date_time', 'location', 'vehicle_count'),
            'description': 'Enter the basic traffic recording details'
        }),
        ('Environmental Conditions', {
            'fields': ('weather', 'congestion_level'),
            'description': 'Specify weather conditions and congestion level'
        }),
        ('Computed Fields', {
            'fields': ('hour_of_day', 'day_of_week'),
            'classes': ('collapse',),
            'description': 'Automatically calculated fields'
        }),
    )

    # Customize the admin site header
    def get_model_perms(self, request):
        """
        Override to add custom permissions if needed.
        """
        perms = super().get_model_perms(request)
        return perms


# Customize admin site appearance
admin.site.site_header = "Traffic Prediction System Administration"
admin.site.site_title = "Traffic Prediction Admin"
admin.site.index_title = "Welcome to Traffic Prediction System Admin Portal"
