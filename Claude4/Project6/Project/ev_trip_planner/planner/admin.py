from django.contrib import admin
from .models import Trip, ChargingStop


@admin.register(ChargingStop)
class ChargingStopAdmin(admin.ModelAdmin):
    list_display = ['trip', 'station', 'stop_order', 'estimated_charge_time']
    list_filter = ['station']


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ['user', 'start_location', 'destination', 'estimated_distance', 'battery_consumption', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['start_location', 'destination']
