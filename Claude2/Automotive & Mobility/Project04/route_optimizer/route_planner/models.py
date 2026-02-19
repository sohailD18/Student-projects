"""
Database models for Route Planner Application
"""
from django.db import models
from django.contrib.auth.models import User
import json


class Location(models.Model):
    """
    Represents a geographic location with coordinates
    """
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default='USA')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.latitude}, {self.longitude})"

    @property
    def coordinates(self):
        """Return coordinates as a tuple"""
        return (self.latitude, self.longitude)


class TrafficData(models.Model):
    """
    Simulated traffic data for route optimization
    """
    # Route segment identifier (e.g., "lat1,lng1-lat2,lng2")
    segment_id = models.CharField(max_length=255, unique=True)

    # Current traffic conditions
    traffic_level = models.FloatField(default=1.0)  # 1.0 = normal, >1 = congestion
    avg_speed = models.FloatField(default=60.0)  # km/h

    # Time-based patterns
    hour = models.IntegerField(default=12)  # Hour of day (0-23)
    day_of_week = models.IntegerField(default=1)  # 1-7 (Monday-Sunday)

    # Historical data
    historical_congestion = models.JSONField(default=dict)  # Hourly congestion data

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Traffic Data"
        verbose_name_plural = "Traffic Data"

    def __str__(self):
        return f"Segment {self.segment_id} - Traffic: {self.traffic_level}"


class Route(models.Model):
    """
    Represents a route between two locations
    """
    ROUTE_TYPE_CHOICES = [
        ('fastest', 'Fastest'),
        ('shortest', 'Shortest'),
        ('scenic', 'Most Scenic'),
        ('eco', 'Eco-Friendly'),
    ]

    origin = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='routes_from')
    destination = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='routes_to')

    # Route characteristics
    route_type = models.CharField(max_length=20, choices=ROUTE_TYPE_CHOICES, default='fastest')
    distance_km = models.FloatField()
    estimated_time_minutes = models.IntegerField()

    # Route geometry (polyline coordinates)
    path_coordinates = models.JSONField(default=list)  # List of [lat, lng] pairs

    # Traffic and cost factors
    traffic_factor = models.FloatField(default=1.0)
    fuel_cost_estimate = models.FloatField(default=0.0)  # USD
    co2_emission_kg = models.FloatField(default=0.0)

    # Route metadata
    is_recommended = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Route"
        verbose_name_plural = "Routes"
        ordering = ['is_recommended', 'estimated_time_minutes']

    def __str__(self):
        return f"{self.origin.name} → {self.destination.name} ({self.get_route_type_display()})"

    @property
    def coordinates_list(self):
        """Return coordinates in Leaflet-compatible format"""
        return [[coord[0], coord[1]] for coord in self.path_coordinates]


class RouteHistory(models.Model):
    """
    Tracks historical route calculations and user selections
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    origin_name = models.CharField(max_length=255)
    origin_lat = models.FloatField()
    origin_lng = models.FloatField()

    destination_name = models.CharField(max_length=255)
    destination_lat = models.FloatField()
    destination_lng = models.FloatField()

    # Selected route information
    selected_route_type = models.CharField(max_length=20)
    distance_km = models.FloatField()
    estimated_time_minutes = models.IntegerField()
    fuel_cost = models.FloatField(default=0.0)

    # All available routes (stored as JSON)
    available_routes = models.JSONField(default=dict)

    # AI optimization score
    optimization_score = models.FloatField(default=0.0)  # 0-100

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Route History"
        verbose_name_plural = "Route History"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.origin_name} → {self.destination_name} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class OptimizationMetrics(models.Model):
    """
    Tracks AI optimization performance metrics
    """
    date = models.DateField(auto_now_add=True)

    # Performance metrics
    total_routes_calculated = models.IntegerField(default=0)
    avg_optimization_time_ms = models.FloatField(default=0.0)

    # User satisfaction
    avg_savings_minutes = models.FloatField(default=0.0)
    avg_cost_savings_usd = models.FloatField(default=0.0)

    # Traffic prediction accuracy
    traffic_prediction_accuracy = models.FloatField(default=0.0)  # Percentage

    # Historical data for analytics
    daily_stats = models.JSONField(default=dict)

    class Meta:
        verbose_name = "Optimization Metrics"
        verbose_name_plural = "Optimization Metrics"

    def __str__(self):
        return f"Metrics for {self.date}"
