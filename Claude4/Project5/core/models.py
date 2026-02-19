"""
Database models for AI Trip Planner System.
Includes: Location, TripHistory, UserPreference
"""
from django.db import models
from django.contrib.auth.models import User
import uuid


class Location(models.Model):
    """
    Model to store geographical locations with coordinates.
    Used as sources and destinations for trips.
    """
    LOCATION_TYPES = [
        ('city', 'City'),
        ('landmark', 'Landmark'),
        ('address', 'Address'),
        ('airport', 'Airport'),
        ('station', 'Station'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text="Name of the location")
    address = models.TextField(blank=True, help_text="Full address")
    city = models.CharField(max_length=100, help_text="City name")
    state = models.CharField(max_length=100, blank=True, help_text="State or region")
    country = models.CharField(max_length=100, default='India', help_text="Country name")
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="Latitude coordinate (-90 to 90)"
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        help_text="Longitude coordinate (-180 to 180)"
    )
    location_type = models.CharField(
        max_length=20,
        choices=LOCATION_TYPES,
        default='city',
        help_text="Type of location"
    )
    is_popular = models.BooleanField(
        default=False,
        help_text="Mark as popular destination"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Locations"
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['city', 'state']),
            models.Index(fields=['latitude', 'longitude']),
        ]

    def __str__(self):
        return f"{self.name}, {self.city}"


class TripHistory(models.Model):
    """
    Model to store historical trip data for AI model training and analysis.
    This data helps the system learn travel patterns and predict travel times.
    """
    TRAFFIC_LEVELS = [
        (1, 'Very Low'),
        (2, 'Low'),
        (3, 'Moderate-Low'),
        (4, 'Moderate'),
        (5, 'Moderate-High'),
        (6, 'High'),
        (7, 'Very High'),
        (8, 'Severe'),
        (9, 'Extreme'),
        (10, 'Gridlock'),
    ]

    WEATHER_CONDITIONS = [
        ('clear', 'Clear'),
        ('cloudy', 'Cloudy'),
        ('rain', 'Rain'),
        ('heavy_rain', 'Heavy Rain'),
        ('snow', 'Snow'),
        ('fog', 'Fog'),
        ('storm', 'Storm'),
    ]

    TRANSPORT_MODES = [
        ('car', 'Car'),
        ('bike', 'Motorcycle'),
        ('bus', 'Bus'),
        ('train', 'Train'),
        ('walking', 'Walking'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='trips_from',
        help_text="Starting location"
    )
    destination = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='trips_to',
        help_text="Destination location"
    )
    distance = models.FloatField(
        help_text="Distance in kilometers"
    )
    traffic_level = models.IntegerField(
        choices=TRAFFIC_LEVELS,
        default=4,
        help_text="Traffic congestion level (1-10)"
    )
    travel_time = models.FloatField(
        help_text="Actual travel time in minutes"
    )
    weather_condition = models.CharField(
        max_length=20,
        choices=WEATHER_CONDITIONS,
        default='clear',
        help_text="Weather during travel"
    )
    transport_mode = models.CharField(
        max_length=20,
        choices=TRANSPORT_MODES,
        default='car',
        help_text="Mode of transport used"
    )
    route_type = models.CharField(
        max_length=50,
        help_text="Type of route taken (fastest, shortest, scenic)"
    )
    fuel_cost = models.FloatField(
        null=True,
        blank=True,
        help_text="Estimated fuel cost in local currency"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When this trip record was created"
    )
    date_of_travel = models.DateTimeField(
        help_text="Actual date and time of travel"
    )

    class Meta:
        ordering = ['-date_of_travel']
        verbose_name_plural = "Trip Histories"
        indexes = [
            models.Index(fields=['source', 'destination']),
            models.Index(fields=['traffic_level']),
            models.Index(fields=['weather_condition']),
            models.Index(fields=['-date_of_travel']),
        ]

    def __str__(self):
        return f"{self.source} to {self.destination} - {self.travel_time} mins"


class UserPreference(models.Model):
    """
    Model to store user preferences for personalized trip recommendations.
    Can be linked to Django User accounts or used anonymously.
    """
    PRIORITY_CHOICES = [
        ('time', 'Fastest Route'),
        ('distance', 'Shortest Distance'),
        ('cost', 'Lowest Cost'),
        ('scenic', 'Scenic Route'),
        ('eco', 'Eco-Friendly'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='trip_preferences',
        help_text="Linked user account (optional)"
    )
    session_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        help_text="Session ID for anonymous users"
    )
    preferred_transport_mode = models.CharField(
        max_length=20,
        choices=TripHistory.TRANSPORT_MODES,
        default='car',
        help_text="Default transport mode"
    )
    route_priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='time',
        help_text="What user prioritizes in routes"
    )
    avoid_tolls = models.BooleanField(
        default=False,
        help_text="Prefer toll-free routes"
    )
    avoid_highways = models.BooleanField(
        default=False,
        help_text="Avoid highways"
    )
    default_home_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users_home',
        help_text="User's home location"
    )
    default_work_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users_work',
        help_text="User's work location"
    )
    notification_enabled = models.BooleanField(
        default=True,
        help_text="Enable traffic notifications"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user']
        verbose_name_plural = "User Preferences"

    def __str__(self):
        if self.user:
            return f"Preferences for {self.user.username}"
        return f"Preferences for session {self.session_id}"


class RouteSuggestion(models.Model):
    """
    Model to cache route suggestions and improve response time.
    Stores AI-generated route options for common queries.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='route_suggestions_from'
    )
    destination = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='route_suggestions_to'
    )
    route_name = models.CharField(max_length=100)
    distance_km = models.FloatField()
    estimated_time_mins = models.FloatField()
    traffic_factor = models.FloatField(default=1.0)
    fuel_cost = models.FloatField(null=True, blank=True)
    route_type = models.CharField(
        max_length=50,
        choices=[
            ('fastest', 'Fastest'),
            ('shortest', 'Shortest'),
            ('scenic', 'Scenic'),
            ('eco', 'Eco-Friendly'),
        ]
    )
    coordinates = models.JSONField(
        help_text="Route coordinates as JSON array of [lat, lng] pairs"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    hit_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-hit_count']
        verbose_name_plural = "Route Suggestions"

    def __str__(self):
        return f"{self.route_name}: {self.source} to {self.destination}"
