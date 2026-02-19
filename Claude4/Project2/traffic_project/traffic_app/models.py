"""
Database Models for Traffic Congestion Prediction System

This module defines the TrafficData model which stores traffic information
for training and prediction purposes.
"""

from django.db import models
from django.core.validators import MinValueValidator


class TrafficData(models.Model):
    """
    Model to store traffic data for ML training and historical analysis.

    Fields:
        date_time: Timestamp of traffic recording
        location: Name of the road/junction/location
        vehicle_count: Number of vehicles passed during the recording period
        weather: Weather condition during recording
        congestion_level: Target label - Low, Medium, or High congestion
    """

    # Congestion level choices
    CONGESTION_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    # Weather condition choices
    WEATHER_CHOICES = [
        ('Sunny', 'Sunny'),
        ('Rainy', 'Rainy'),
        ('Cloudy', 'Cloudy'),
        ('Foggy', 'Foggy'),
    ]

    # Common traffic locations (can be extended)
    LOCATION_CHOICES = [
        ('Main Street Junction', 'Main Street Junction'),
        ('Highway Exit 45', 'Highway Exit 45'),
        ('City Center Square', 'City Center Square'),
        ('North Avenue Bridge', 'North Avenue Bridge'),
        ('Market Street Crossing', 'Market Street Crossing'),
        ('Railway Road Intersection', 'Railway Road Intersection'),
        ('University Gate', 'University Gate'),
        ('Hospital District', 'Hospital District'),
        ('Industrial Area', 'Industrial Area'),
        ('Suburb Entrance', 'Suburb Entrance'),
    ]

    # Model fields
    date_time = models.DateTimeField(
        help_text="Date and time of traffic recording"
    )

    location = models.CharField(
        max_length=100,
        choices=LOCATION_CHOICES,
        help_text="Location of the traffic recording"
    )

    vehicle_count = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Number of vehicles passed"
    )

    weather = models.CharField(
        max_length=20,
        choices=WEATHER_CHOICES,
        help_text="Weather condition during recording"
    )

    congestion_level = models.CharField(
        max_length=10,
        choices=CONGESTION_CHOICES,
        help_text="Predicted/Labeled congestion level"
    )

    class Meta:
        """
        Meta configuration for TrafficData model.
        Orders records by date_time (newest first).
        Ensures no duplicate entries for same location and time.
        """
        ordering = ['-date_time']
        verbose_name = "Traffic Data"
        verbose_name_plural = "Traffic Data Records"

    def __str__(self):
        """
        String representation of TrafficData instance.

        Returns:
            str: Human-readable string showing location and datetime
        """
        return f"{self.location} - {self.date_time.strftime('%Y-%m-%d %H:%M')} - {self.congestion_level}"

    @property
    def hour_of_day(self):
        """
        Extract hour from datetime for time-based analysis.

        Returns:
            int: Hour of day (0-23)
        """
        return self.date_time.hour

    @property
    def day_of_week(self):
        """
        Extract day of week from datetime.

        Returns:
            int: Day of week (0=Monday, 6=Sunday)
        """
        return self.date_time.weekday()
