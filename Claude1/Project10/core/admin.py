from django.contrib import admin
from .models import Skill, Session, Review


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'category', 'hourly_rate_points', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'teacher__username', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['skill', 'student', 'teacher', 'scheduled_time', 'status', 'created_at']
    list_filter = ['status', 'scheduled_time', 'created_at']
    search_fields = ['student__username', 'teacher__username', 'skill__title']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'scheduled_time'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['session', 'rating', 'reviewer', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['session__skill__title', 'reviewer__username', 'comment']
    readonly_fields = ['created_at', 'updated_at']
