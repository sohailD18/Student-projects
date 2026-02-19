"""
Admin configuration for Users App
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """
    Inline admin for UserProfile to show in User admin
    """
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ['date_of_birth', 'category', 'highest_qualification', 'state',
              'preferred_exam_types', 'profile_completed']


# Extend UserAdmin to include profile
class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = UserAdmin.list_display + ('get_age', 'get_category')

    def get_age(self, obj):
        """Get user's age from profile"""
        try:
            return obj.profile.age
        except UserProfile.DoesNotExist:
            return None
    get_age.short_description = 'Age'

    def get_category(self, obj):
        """Get user's category from profile"""
        try:
            return obj.profile.get_category_display()
        except UserProfile.DoesNotExist:
            return None
    get_category.short_description = 'Category'


# Unregister default User admin and register custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for UserProfile model (also accessible via User)
    """
    list_display = ['user', 'age', 'category', 'highest_qualification', 'state', 'profile_completed']
    list_filter = ['category', 'highest_qualification', 'profile_completed']
    search_fields = ['user__username', 'user__email', 'state']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Personal Details', {
            'fields': ('date_of_birth', 'category')
        }),
        ('Educational Details', {
            'fields': ('highest_qualification',)
        }),
        ('Location & Preferences', {
            'fields': ('state', 'preferred_exam_types')
        }),
        ('Status', {
            'fields': ('profile_completed',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
