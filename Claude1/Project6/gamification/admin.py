from django.contrib import admin
from .models import Badge, UserBadge


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'badge_type', 'requirement_value', 'icon_name')
    list_filter = ('badge_type',)
    search_fields = ('name', 'description')


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'earned_at')
    list_filter = ('earned_at', 'badge')
    search_fields = ('user__username', 'badge__name')
    readonly_fields = ('earned_at',)
