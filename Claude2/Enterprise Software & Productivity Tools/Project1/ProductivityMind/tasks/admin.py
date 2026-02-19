"""
ProductivityMind - Django Admin Configuration
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import (
    Task, Project, ProjectMember, Tag, Category,
    WorkLog, UserProfile, TaskDependency
)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'total_tasks', 'completed_tasks', 'progress_percentage', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'role', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['user__username', 'project__name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_preview', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']

    def color_preview(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 5px 10px; border-radius: 3px; color: white;">{}</span>',
            obj.color, obj.color
        )
    color_preview.short_description = 'Color'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'status', 'priority', 'smart_priority_score',
        'assignee', 'due_date', 'is_at_risk', 'project'
    ]
    list_filter = ['status', 'priority', 'is_at_risk', 'risk_level', 'project', 'category']
    search_fields = ['title', 'description', 'assignee__username']
    readonly_fields = [
        'created_at', 'updated_at', 'completed_at',
        'smart_priority_score', 'is_at_risk', 'risk_level'
    ]
    filter_horizontal = ['blocked_by', 'tags']
    date_hierarchy = 'due_date'

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'status', 'priority')
        }),
        ('Assignment & Project', {
            'fields': ('project', 'assignee', 'category')
        }),
        ('Time Tracking', {
            'fields': ('due_date', 'estimated_hours', 'actual_hours')
        }),
        ('Dependencies & Tags', {
            'fields': ('blocked_by', 'tags')
        }),
        ('AI Analytics', {
            'fields': ('smart_priority_score', 'is_at_risk', 'risk_level'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'assignee', 'project', 'category'
        ).prefetch_related('tags')


@admin.register(WorkLog)
class WorkLogAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'hours', 'logged_at']
    list_filter = ['logged_at', 'user']
    search_fields = ['task__title', 'user__username', 'notes']
    readonly_fields = ['logged_at']


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ['bio', 'avatar_url', 'department', 'position', 'phone', 'working_hours_per_day']


class ExtendedUserAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = UserAdmin.list_display + ('get_department', 'get_position')

    def get_department(self, obj):
        return obj.profile.department if hasattr(obj, 'profile') else ''
    get_department.short_description = 'Department'

    def get_position(self, obj):
        return obj.profile.position if hasattr(obj, 'profile') else ''
    get_position.short_description = 'Position'


# Unregister the default User admin and register the extended one
admin.site.unregister(User)
admin.site.register(User, ExtendedUserAdmin)


@admin.register(TaskDependency)
class TaskDependencyAdmin(admin.ModelAdmin):
    list_display = ['dependent_task', 'blocking_task', 'created_at']
    search_fields = ['dependent_task__title', 'blocking_task__title', 'notes']
    readonly_fields = ['created_at']
