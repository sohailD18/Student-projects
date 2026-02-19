"""
Django Admin configuration for InfraGuard
"""

from django.contrib import admin
from .models import UserProfile, Incident, Claim


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    readonly_fields = ['created_at']


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ['id', 'incident_type', 'location', 'status', 'severity_score', 'reported_by', 'timestamp']
    list_filter = ['status', 'incident_type', 'timestamp']
    search_fields = ['location', 'description', 'reported_by__username']
    readonly_fields = ['timestamp', 'verified_at', 'resolved_at']
    ordering = ['-timestamp']

    fieldsets = (
        ('Basic Information', {
            'fields': ('location', 'description', 'incident_type', 'status')
        }),
        ('Evidence', {
            'fields': ('image', 'latitude', 'longitude')
        }),
        ('AI Analysis', {
            'fields': ('severity_score',)
        }),
        ('Reporter', {
            'fields': ('reported_by',)
        }),
        ('Timestamps', {
            'fields': ('timestamp', 'verified_at', 'resolved_at')
        }),
        ('Authority Notes', {
            'fields': ('authority_notes',)
        }),
    )


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ['id', 'victim_name', 'incident', 'claim_amount', 'status', 'filed_date', 'reviewed_by']
    list_filter = ['status', 'filed_date']
    search_fields = ['victim_name', 'incident__location', 'evidence_description']
    readonly_fields = ['filed_date', 'reviewed_at']
    ordering = ['-filed_date']

    fieldsets = (
        ('Claim Information', {
            'fields': ('incident', 'victim_name', 'claim_amount', 'status')
        }),
        ('Evidence', {
            'fields': ('evidence_description',)
        }),
        ('Review', {
            'fields': ('reviewed_by', 'review_notes', 'approved_amount')
        }),
        ('Timestamps', {
            'fields': ('filed_date', 'reviewed_at')
        }),
    )
