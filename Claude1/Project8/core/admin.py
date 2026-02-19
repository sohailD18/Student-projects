from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Incident, Comment, UserProfile, IncidentCategory,
    IncidentVerification, Notification, SafetyAlert, CommentLike
)


@admin.register(IncidentCategory)
class IncidentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon_preview', 'incident_count', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']

    def icon_preview(self, obj):
        return format_html('<i class="{}" style="font-size: 1.5rem;"></i>', obj.icon)
    icon_preview.short_description = 'Icon'

    def incident_count(self, obj):
        return obj.incidents.count()
    incident_count.short_description = 'Incidents'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'reputation_score', 'notification_enabled', 'joined_at']
    list_filter = ['notification_enabled', 'email_alerts', 'joined_at']
    search_fields = ['user__username', 'location', 'phone_number']
    readonly_fields = ['joined_at', 'last_activity']


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'location', 'status', 'severity', 'is_verified', 'verification_count', 'view_count', 'user', 'created_at']
    list_filter = ['status', 'severity', 'is_verified', 'category', 'created_at']
    search_fields = ['title', 'description', 'location', 'address']
    readonly_fields = ['created_at', 'updated_at', 'verification_count', 'view_count']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category', 'user')
        }),
        ('Location', {
            'fields': ('location', 'address', 'latitude', 'longitude')
        }),
        ('Details', {
            'fields': ('image', 'timestamp', 'severity', 'status', 'is_anonymous')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verified_by', 'verified_at', 'verification_count', 'view_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['incident', 'user', 'content_preview', 'likes_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'incident__title', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'likes_count']

    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ['comment', 'user', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['created_at']


@admin.register(IncidentVerification)
class IncidentVerificationAdmin(admin.ModelAdmin):
    list_display = ['incident', 'user', 'is_confirmed', 'created_at']
    list_filter = ['is_confirmed', 'created_at']
    search_fields = ['incident__title', 'user__username', 'comments']
    readonly_fields = ['created_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'recipient__username']
    readonly_fields = ['created_at']

    def mark_all_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f'Marked {queryset.count()} notifications as read.')
    mark_all_as_read.short_description = 'Mark selected as read'

    actions = ['mark_all_as_read']


@admin.register(SafetyAlert)
class SafetyAlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'severity', 'affected_areas', 'is_active', 'expires_at', 'created_by', 'created_at']
    list_filter = ['severity', 'is_active', 'created_at']
    search_fields = ['title', 'message', 'affected_areas']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'message', 'severity')
        }),
        ('Details', {
            'fields': ('affected_areas', 'is_active', 'expires_at', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
