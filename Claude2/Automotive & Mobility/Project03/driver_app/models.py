from django.db import models


class DriverData(models.Model):
    """
    Model to store driver behavior data for analysis.
    Tracks various metrics related to driving patterns and safety.
    """

    BEHAVIOR_CHOICES = [
        ('Safe', 'Safe'),
        ('Moderate', 'Moderate'),
        ('Risky', 'Risky'),
    ]

    # Basic Information
    driver_name = models.CharField(max_length=100, help_text="Name of the driver")
    trip_date = models.DateField(help_text="Date of the trip")

    # Speed Metrics
    average_speed = models.FloatField(help_text="Average speed during trip (km/h)")
    max_speed = models.FloatField(help_text="Maximum speed reached (km/h)")

    # Event Counts
    harsh_braking_events = models.IntegerField(default=0, help_text="Number of harsh braking incidents")
    rapid_acceleration_events = models.IntegerField(default=0, help_text="Number of rapid acceleration incidents")

    # Additional Metrics
    cornering_speed = models.FloatField(default=0, help_text="Average cornering speed (km/h)")

    # AI Analysis Results (calculated fields)
    risk_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Calculated risk score (0-100)"
    )
    behavior_class = models.CharField(
        max_length=20,
        choices=BEHAVIOR_CHOICES,
        null=True,
        blank=True,
        help_text="AI classified behavior category"
    )
    recommendations = models.TextField(
        null=True,
        blank=True,
        help_text="AI generated safety recommendations"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-trip_date', '-created_at']
        verbose_name = "Driver Data"
        verbose_name_plural = "Driver Data Records"

    def __str__(self):
        return f"{self.driver_name} - {self.trip_date}"

    @property
    def safety_percentage(self):
        """Returns safety percentage (inverse of risk score)"""
        if self.risk_score is not None:
            return round(100 - self.risk_score, 2)
        return None
