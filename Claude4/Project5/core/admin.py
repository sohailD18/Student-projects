"""
Admin configuration for AI Trip Planner models.
"""
from django.contrib import admin
from .models import Location, TripHistory, UserPreference, RouteSuggestion


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Admin interface for Location model."""
    list_display = ['name', 'city', 'state', 'country', 'location_type', 'is_popular', 'created_at']
    list_filter = ['location_type', 'is_popular', 'city', 'state']
    search_fields = ['name', 'city', 'state', 'address']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['name']


@admin.register(TripHistory)
class TripHistoryAdmin(admin.ModelAdmin):
    """Admin interface for TripHistory model."""
    list_display = ['source', 'destination', 'distance', 'traffic_level', 'travel_time', 'weather_condition', 'transport_mode', 'date_of_travel']
    list_filter = ['transport_mode', 'weather_condition', 'traffic_level', 'route_type', 'date_of_travel']
    search_fields = ['source__name', 'destination__name']
    readonly_fields = ['id', 'timestamp']
    ordering = ['-date_of_travel']

    fieldsets = (
        ('Route Information', {
            'fields': ('source', 'destination', 'distance', 'route_type')
        }),
        ('Travel Conditions', {
            'fields': ('traffic_level', 'weather_condition', 'transport_mode')
        }),
        ('Results', {
            'fields': ('travel_time', 'fuel_cost')
        }),
        ('Metadata', {
            'fields': ('date_of_travel', 'timestamp')
        }),
    )


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    """Admin interface for UserPreference model."""
    list_display = ['user', 'session_id', 'preferred_transport_mode', 'route_priority', 'avoid_tolls', 'created_at']
    list_filter = ['preferred_transport_mode', 'route_priority', 'avoid_tolls', 'avoid_highways']
    search_fields = ['user__username', 'session_id']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(RouteSuggestion)
class RouteSuggestionAdmin(admin.ModelAdmin):
    """Admin interface for RouteSuggestion model."""
    list_display = ['route_name', 'source', 'destination', 'distance_km', 'estimated_time_mins', 'route_type', 'hit_count', 'created_at']
    list_filter = ['route_type', 'created_at']
    search_fields = ['route_name', 'source__name', 'destination__name']
    readonly_fields = ['id', 'created_at']
    ordering = ['-hit_count']


# Customize admin site
admin.site.site_header = 'AI Trip Planner Admin'
admin.site.site_title = 'AI Trip Planner'
admin.site.index_title = 'Welcome to AI Trip Planner Administration'
