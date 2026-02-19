from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_credits')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

    def get_credits(self, obj):
        return obj.profile.time_credits_balance if hasattr(obj, 'profile') else 0
    get_credits.short_description = 'Credits'


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'skills', 'availability', 'time_credits_balance')
    list_filter = ('availability',)
    search_fields = ('user__username', 'skills', 'bio')
    readonly_fields = ('time_credits_balance',)
