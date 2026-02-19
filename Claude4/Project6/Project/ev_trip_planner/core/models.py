from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    """Extended user profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Vehicle(models.Model):
    """User's EV vehicle information"""
    EV_TYPE_CHOICES = [
        ('BEV', 'Battery Electric Vehicle'),
        ('PHEV', 'Plug-in Hybrid Electric Vehicle'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles')
    make = models.CharField(max_length=100)  # e.g., Tata, Mahindra, Hyundai, MG
    model = models.CharField(max_length=100)  # e.g., Nexon, XUV400, Kona, ZS EV
    year = models.IntegerField()
    ev_type = models.CharField(max_length=4, choices=EV_TYPE_CHOICES, default='BEV')
    battery_capacity = models.FloatField(help_text='Battery capacity in kWh')
    range_km = models.IntegerField(default=300, help_text='Estimated range in kilometers')
    charging_speed = models.FloatField(default=50, help_text='Max charging speed in kW')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.year} {self.make} {self.model}"


class ChargingStation(models.Model):
    """Charging station information"""
    CONNECTOR_TYPES = [
        ('Type2', 'Type 2 (AC)'),
        ('CCS2', 'CCS Combo 2 (DC Fast)'),
        ('CHAdeMO', 'CHAdeMO (DC Fast)'),
        ('Bharat_DC', 'Bharat DC DC-001 (India Standard)'),
        ('Tesla', 'Tesla Supercharger'),
        ('GB_T', 'GB/T (Chinese Standard)'),
    ]

    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.TextField()
    connector_type = models.CharField(max_length=20, choices=CONNECTOR_TYPES)
    power_kw = models.FloatField(help_text='Charging power in kW')
    price_per_kwh = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)
    fast_charging = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    total_ports = models.IntegerField(default=2)
    available_ports = models.IntegerField(default=2)
    amenities = models.TextField(blank=True, help_text='Comma-separated amenities (WiFi, Restroom, etc.)')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.location}"

    def update_availability(self):
        """Update availability based on ports"""
        self.is_available = self.available_ports > 0
        self.save()
