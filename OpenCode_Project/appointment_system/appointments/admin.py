from django.contrib import admin
from .models import Service, Provider, TimeSlot, Appointment, Booking, Reminder

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'duration', 'price', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']

@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'is_available', 'created_at']
    list_filter = ['is_available', 'created_at']
    search_fields = ['user__username', 'user__email']
    filter_horizontal = ['services']

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['provider', 'day_of_week', 'start_time', 'end_time', 'is_active']
    list_filter = ['day_of_week', 'is_active', 'provider']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['client', 'provider', 'service', 'appointment_date', 'start_time', 'status']
    list_filter = ['status', 'appointment_date', 'provider']
    search_fields = ['client__username', 'provider__user__username']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'service', 'provider', 'booking_date', 'booking_time', 'status', 'total_amount']
    list_filter = ['status', 'booking_date']
    search_fields = ['user__username']

@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'reminder_type', 'scheduled_time', 'is_sent']
    list_filter = ['reminder_type', 'is_sent']
