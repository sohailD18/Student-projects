from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'rating', 'sentiment', 'sentiment_score', 'created_at']
    list_filter = ['sentiment', 'rating', 'product_name', 'created_at']
    search_fields = ['review_text', 'product_name']
    readonly_fields = ['sentiment', 'sentiment_score', 'created_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Review Information', {
            'fields': ('product_name', 'review_text', 'rating')
        }),
        ('Sentiment Analysis (Auto-generated)', {
            'fields': ('sentiment', 'sentiment_score'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
