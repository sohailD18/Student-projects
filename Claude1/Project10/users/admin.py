from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Badge


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'points_required', 'sessions_required', 'created_at']
    list_filter = ['points_required', 'sessions_required', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ['bio', 'skills_to_teach', 'skills_to_learn', 'points_earned', 'badges']
    filter_horizontal = ['badges']


class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'get_points', 'get_badges']
    search_fields = ['username', 'email', 'first_name', 'last_name']

    def get_points(self, obj):
        return obj.profile.points_earned if hasattr(obj, 'profile') else 0
    get_points.short_description = 'Points'

    def get_badges(self, obj):
        return obj.profile.badges.count() if hasattr(obj, 'profile') and obj.profile else 0
    get_badges.short_description = 'Badges'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
