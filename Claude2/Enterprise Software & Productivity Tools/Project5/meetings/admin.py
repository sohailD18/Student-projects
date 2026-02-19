"""
Admin configuration for Meeting Analyzer models.
"""
from django.contrib import admin
from .models import Meeting, ActionItem, AnalysisResult, MeetingReport


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    """
    Admin interface for Meeting model.
    """
    list_display = ['title', 'date', 'duration', 'created_at', 'get_action_items_count']
    list_filter = ['date', 'created_at', 'duration']
    search_fields = ['title', 'participants', 'transcript']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'date', 'duration', 'participants')
        }),
        ('Meeting Content', {
            'fields': ('transcript',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_action_items_count(self, obj):
        """Display the count of action items."""
        return obj.get_action_items_count()
    get_action_items_count.short_description = 'Action Items'


@admin.register(ActionItem)
class ActionItemAdmin(admin.ModelAdmin):
    """
    Admin interface for ActionItem model.
    """
    list_display = ['description_preview', 'meeting', 'assignee', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'meeting']
    search_fields = ['description', 'assignee', 'meeting__title']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Action Item Details', {
            'fields': ('meeting', 'description', 'assignee', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def description_preview(self, obj):
        """Display a preview of the description."""
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_preview.short_description = 'Description'


@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    """
    Admin interface for AnalysisResult model.
    """
    list_display = ['meeting', 'sentiment', 'sentiment_score', 'productivity_score',
                   'word_count', 'action_items_extracted', 'created_at']
    list_filter = ['sentiment', 'created_at']
    search_fields = ['meeting__title', 'summary', 'keywords']
    date_hierarchy = 'created_at'
    readonly_fields = ['meeting', 'summary', 'sentiment', 'sentiment_score',
                      'productivity_score', 'word_count', 'action_items_extracted',
                      'keywords', 'follow_up_recommendations', 'created_at']

    fieldsets = (
        ('Analysis Results', {
            'fields': ('meeting', 'summary', 'sentiment', 'sentiment_score')
        }),
        ('Metrics', {
            'fields': ('productivity_score', 'word_count', 'action_items_extracted', 'keywords')
        }),
        ('Recommendations', {
            'fields': ('follow_up_recommendations',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(MeetingReport)
class MeetingReportAdmin(admin.ModelAdmin):
    """
    Admin interface for MeetingReport model.
    """
    list_display = ['title', 'generated_at', 'get_meetings_count']
    list_filter = ['generated_at']
    search_fields = ['title', 'content']
    date_hierarchy = 'generated_at'
    readonly_fields = ['generated_at']
    filter_horizontal = ['meetings_covered']

    fieldsets = (
        ('Report Details', {
            'fields': ('title', 'meetings_covered', 'content')
        }),
        ('Timestamps', {
            'fields': ('generated_at',),
            'classes': ('collapse',)
        }),
    )

    def get_meetings_count(self, obj):
        """Display the count of meetings covered."""
        return obj.meetings_covered.count()
    get_meetings_count.short_description = 'Meetings Covered'


# Customize admin site
admin.site.site_header = 'Meeting Analyzer Administration'
admin.site.site_title = 'Meeting Analyzer Admin'
admin.site.index_title = 'Welcome to Meeting Analyzer Administration'
