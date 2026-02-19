from django.contrib import admin
from .models import Vehicle, ChargingStation, UserProfile

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['user', 'make', 'model', 'year', 'battery_capacity', 'range_km']
    list_filter = ['make', 'year']
    search_fields = ['make', 'model']

@admin.register(ChargingStation)
class ChargingStationAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'connector_type', 'power_kw', 'price_per_kwh', 'is_available']
    list_filter = ['connector_type', 'is_available', 'fast_charging']
    search_fields = ['name', 'location']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'created_at']
    search_fields = ['user__username', 'user__email']
