from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('task', 'reviewer', 'reviewee', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('reviewer__username', 'reviewee__username', 'task__title', 'comment')
    readonly_fields = ('created_at',)
