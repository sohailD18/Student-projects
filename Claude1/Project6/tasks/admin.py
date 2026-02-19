from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'assigned_to', 'status', 'estimated_duration', 'created_at')
    list_filter = ('status', 'created_at', 'estimated_duration')
    search_fields = ('title', 'description', 'required_skills')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
