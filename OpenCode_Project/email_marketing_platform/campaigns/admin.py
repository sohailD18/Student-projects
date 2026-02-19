from django.contrib import admin
from .models import EmailList, Subscriber, EmailTemplate, Campaign, EmailLog, EmailAnalytics, Link


@admin.register(EmailList)
class EmailListAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'subscriber_count', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'status', 'is_active', 'subscribed_at']
    search_fields = ['email', 'first_name', 'last_name']
    list_filter = ['status', 'is_active', 'subscribed_at']
    filter_horizontal = ['email_list']


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'is_active', 'created_at']
    search_fields = ['name', 'subject']
    list_filter = ['is_active', 'created_at']


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'email_template', 'email_list', 'status', 'is_ab_test', 'scheduled_at', 'sent_at']
    search_fields = ['name']
    list_filter = ['status', 'is_ab_test', 'created_at']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email_template', 'email_list', 'status', 'created_by')
        }),
        ('A/B Testing', {
            'fields': ('is_ab_test', 'ab_test_variant_a', 'ab_test_variant_b',
                      'ab_test_split_percentage', 'ab_test_winner'),
            'classes': ('collapse',),
        }),
        ('Scheduling', {
            'fields': ('scheduled_at', 'sent_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['subscriber', 'campaign', 'status', 'variant', 'sent_at']
    search_fields = ['subscriber__email', 'campaign__name']
    list_filter = ['status', 'variant', 'sent_at']
    readonly_fields = ['id']


@admin.register(EmailAnalytics)
class EmailAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['email_log', 'opened_at', 'click_count', 'clicked_at', 'user_agent']
    list_filter = ['opened_at', 'clicked_at']
    readonly_fields = ['email_log', 'created_at', 'updated_at']


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ['url', 'campaign', 'total_clicks', 'unique_clicks']
    search_fields = ['url']
    list_filter = ['campaign']
