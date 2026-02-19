"""
Admin configuration for AgriSense models.
"""
from django.contrib import admin
from .models import SoilData, ContactMessage


@admin.register(SoilData)
class SoilDataAdmin(admin.ModelAdmin):
    """
    Admin interface for SoilData model.
    """
    list_display = ['id', 'nitrogen', 'phosphorus', 'potassium', 'ph_level',
                   'moisture', 'recommended_crop', 'timestamp']
    list_filter = ['recommended_crop', 'timestamp']
    search_fields = ['recommended_crop', 'fertilizer_suggestion']
    readonly_fields = ['timestamp']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """
    Admin interface for ContactMessage model.
    """
    list_display = ['name', 'email', 'is_read', 'timestamp']
    list_filter = ['is_read', 'timestamp']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['timestamp']
