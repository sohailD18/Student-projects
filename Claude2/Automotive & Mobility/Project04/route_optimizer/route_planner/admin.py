"""
Admin configuration for Route Planner models
"""
from django.contrib import admin
from .models import Location, TrafficData, Route, RouteHistory, OptimizationMetrics


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'latitude', 'longitude', 'city', 'country', 'created_at']
    list_filter = ['city', 'country', 'created_at']
    search_fields = ['name', 'address', 'city']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TrafficData)
class TrafficDataAdmin(admin.ModelAdmin):
    list_display = ['segment_id', 'traffic_level', 'avg_speed', 'hour', 'day_of_week', 'updated_at']
    list_filter = ['hour', 'day_of_week', 'updated_at']
    search_fields = ['segment_id']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ['origin', 'destination', 'route_type', 'distance_km', 'estimated_time_minutes',
                    'traffic_factor', 'fuel_cost_estimate', 'is_recommended', 'created_at']
    list_filter = ['route_type', 'is_recommended', 'created_at']
    search_fields = ['origin__name', 'destination__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RouteHistory)
class RouteHistoryAdmin(admin.ModelAdmin):
    list_display = ['origin_name', 'destination_name', 'selected_route_type', 'distance_km',
                    'estimated_time_minutes', 'optimization_score', 'created_at']
    list_filter = ['selected_route_type', 'created_at']
    search_fields = ['origin_name', 'destination_name']
    readonly_fields = ['created_at']


@admin.register(OptimizationMetrics)
class OptimizationMetricsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_routes_calculated', 'avg_optimization_time_ms',
                    'avg_savings_minutes', 'avg_cost_savings_usd', 'traffic_prediction_accuracy']
    list_filter = ['date']
    readonly_fields = ['date']
