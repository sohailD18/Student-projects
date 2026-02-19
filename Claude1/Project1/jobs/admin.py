from django.contrib import admin
from .models import JobCategory, Job, JobApplication, SavedJob


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']
    list_per_page = 20


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'location', 'job_type', 'experience_level', 'status', 'application_count', 'views_count', 'created_at']
    list_filter = ['status', 'job_type', 'experience_level', 'category', 'created_at']
    search_fields = ['title', 'company', 'location', 'description']
    readonly_fields = ['created_at', 'updated_at', 'views_count', 'application_count']
    date_hierarchy = 'created_at'
    list_per_page = 20
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'company', 'location', 'category', 'status')
        }),
        ('Job Details', {
            'fields': ('job_type', 'experience_level', 'description', 'requirements')
        }),
        ('Salary Information', {
            'fields': ('salary_min', 'salary_max', 'is_salary_visible')
        }),
        ('Additional Information', {
            'fields': ('application_deadline', 'created_by', 'views_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def application_count(self, obj):
        return obj.application_count
    application_count.short_description = 'Applications'


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant_name', 'job', 'email', 'phone', 'status', 'applied_at']
    list_filter = ['status', 'applied_at', 'job__category']
    search_fields = ['applicant_name', 'email', 'phone', 'cover_letter']
    readonly_fields = ['applied_at', 'updated_at']
    date_hierarchy = 'applied_at'
    list_per_page = 20
    fieldsets = (
        ('Application Information', {
            'fields': ('job', 'applicant_name', 'email', 'phone', 'status')
        }),
        ('Application Details', {
            'fields': ('cover_letter', 'resume', 'expected_salary')
        }),
        ('Additional Links', {
            'fields': ('linkedin_profile', 'portfolio_url')
        }),
        ('Internal Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('applied_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ['job', 'applicant_name', 'email']
        return self.readonly_fields


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ['user', 'job', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'job__title']
    readonly_fields = ['created_at']
    list_per_page = 20
