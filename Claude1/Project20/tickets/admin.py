from django.contrib import admin
from .models import Complaint, Ticket, Feedback


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    """Admin interface for Complaint model."""

    list_display = ['name', 'email', 'category', 'priority', 'created_at']
    list_filter = ['category', 'priority', 'created_at']
    search_fields = ['name', 'email', 'description']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """Admin interface for Ticket model."""

    list_display = ['unique_ticket_id', 'complaint', 'status', 'assigned_staff', 'created_at']
    list_filter = ['status', 'complaint__priority', 'created_at']
    search_fields = ['unique_ticket_id', 'complaint__name', 'assigned_staff']
    readonly_fields = ['unique_ticket_id', 'created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Ticket Information', {
            'fields': ('unique_ticket_id', 'complaint', 'status')
        }),
        ('Assignment', {
            'fields': ('assigned_staff',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    """Admin interface for Feedback model."""

    list_display = ['ticket', 'rating_display', 'comments_preview', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['ticket__unique_ticket_id', 'comments']
    readonly_fields = ['ticket', 'rating', 'comments', 'created_at']
    ordering = ['-created_at']

    def rating_display(self, obj):
        """Display star rating."""
        return obj.get_stars()
    rating_display.short_description = 'Rating'

    def comments_preview(self, obj):
        """Preview of comments."""
        if obj.comments:
            return obj.comments[:100] + '...' if len(obj.comments) > 100 else obj.comments
        return '-'
    comments_preview.short_description = 'Comments'

    fieldsets = (
        ('Feedback Information', {
            'fields': ('ticket', 'rating_display', 'comments')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
