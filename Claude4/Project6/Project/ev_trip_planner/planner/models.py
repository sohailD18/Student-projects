from django.db import models
from django.contrib.auth.models import User
from core.models import Vehicle, ChargingStation


class Trip(models.Model):
    """Trip planning model"""
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)

    # Trip details
    start_location = models.CharField(max_length=200)
    start_lat = models.FloatField(null=True, blank=True)
    start_lng = models.FloatField(null=True, blank=True)

    destination = models.CharField(max_length=200)
    destination_lat = models.FloatField(null=True, blank=True)
    destination_lng = models.FloatField(null=True, blank=True)

    # Route information
    estimated_distance = models.FloatField(help_text='Distance in kilometers')
    estimated_duration = models.IntegerField(help_text='Duration in minutes')
    battery_consumption = models.FloatField(help_text='Estimated battery consumption in kWh')

    # Battery status
    initial_battery_percent = models.IntegerField(help_text='Starting battery percentage')
    final_battery_percent = models.IntegerField(help_text='Expected final battery percentage')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    travel_date = models.DateField(null=True, blank=True)

    # Additional notes
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.start_location} to {self.destination}"


class ChargingStop(models.Model):
    """Charging stops along a trip route"""
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='charging_stops')
    station = models.ForeignKey(ChargingStation, on_delete=models.CASCADE)

    stop_order = models.IntegerField(help_text='Order of this stop in the trip')
    estimated_charge_time = models.IntegerField(help_text='Estimated charging time in minutes')
    estimated_cost = models.DecimalField(max_digits=6, decimal_places=2, help_text='Estimated charging cost')
    battery_before_charge = models.IntegerField(help_text='Battery % before charging')
    battery_after_charge = models.IntegerField(help_text='Battery % after charging')

    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['stop_order']

    def __str__(self):
        return f"Stop {self.stop_order}: {self.station.name}"
