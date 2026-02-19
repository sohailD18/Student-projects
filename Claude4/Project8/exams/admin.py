"""
Admin configuration for Exams App
"""
from django.contrib import admin
from .models import Exam, ExamCategory


@admin.register(ExamCategory)
class ExamCategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for ExamCategory model
    """
    list_display = ['name', 'code', 'exam_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at', 'exam_count']

    fieldsets = (
        ('Category Information', {
            'fields': ('name', 'code', 'description', 'icon_class', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'exam_count'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    """
    Admin interface for Exam model
    """
    list_display = [
        'title',
        'category',
        'exam_type',
        'application_start_date',
        'application_end_date',
        'exam_date',
        'age_limits',
        'is_upcoming',
        'created_at'
    ]
    list_filter = ['category', 'exam_type', 'application_start_date', 'exam_date']
    search_fields = ['title', 'description', 'eligibility_criteria']
    date_hierarchy = 'exam_date'
    ordering = ['-exam_date']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'category', 'official_link', 'description')
        }),
        ('Eligibility Criteria', {
            'fields': ('eligibility_criteria', 'age_limit_min', 'age_limit_max', 'educational_qualification')
        }),
        ('Syllabus & Details', {
            'fields': ('syllabus_text',)
        }),
        ('Important Dates', {
            'fields': ('application_start_date', 'application_end_date', 'exam_date')
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def age_limits(self, obj):
        """Display age limits in list view"""
        return f"{obj.age_limit_min} - {obj.age_limit_max} years"
    age_limits.short_description = 'Age Limit'

    def is_upcoming(self, obj):
        """Show if exam is upcoming"""
        return obj.is_upcoming()
    is_upcoming.boolean = True
    is_upcoming.short_description = 'Upcoming'


# Unregister default User model to customize (optional)
# from django.contrib.auth.models import User
# from django.contrib.auth.admin import UserAdmin
# admin.site.unregister(User)
