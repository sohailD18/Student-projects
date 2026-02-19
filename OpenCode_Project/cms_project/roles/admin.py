from django.contrib import admin
from .models import Role, RoleAssignment, PagePermission, MediaPermission, Workflow, WorkflowState, WorkflowTransition


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'is_system_role', 'created_at']
    list_filter = ['is_active', 'is_system_role', 'created_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['permissions', 'groups']


@admin.register(RoleAssignment)
class RoleAssignmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'assigned_by', 'assigned_at']
    list_filter = ['role', 'assigned_at']
    search_fields = ['user__username', 'role__name']


@admin.register(PagePermission)
class PagePermissionAdmin(admin.ModelAdmin):
    list_display = ['page', 'get_target', 'permission', 'granted_by', 'granted_at']
    list_filter = ['permission', 'granted_at']
    search_fields = ['page__title']

    def get_target(self, obj):
        return obj.user.username if obj.user else obj.role.name
    get_target.short_description = 'Target'


@admin.register(MediaPermission)
class MediaPermissionAdmin(admin.ModelAdmin):
    list_display = ['folder', 'get_target', 'permission', 'granted_by', 'granted_at']
    list_filter = ['permission', 'folder', 'granted_at']

    def get_target(self, obj):
        return obj.user.username if obj.user else obj.role.name
    get_target.short_description = 'Target'


class WorkflowStateInline(admin.StackedInline):
    model = WorkflowState
    extra = 0


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'content_type', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [WorkflowStateInline]


@admin.register(WorkflowState)
class WorkflowStateAdmin(admin.ModelAdmin):
    list_display = ['name', 'workflow', 'slug', 'order', 'is_initial', 'is_final']
    list_filter = ['workflow', 'is_initial', 'is_final']
    search_fields = ['name', 'slug', 'description']


@admin.register(WorkflowTransition)
class WorkflowTransitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'from_state', 'to_state', 'workflow', 'is_active']
    list_filter = ['workflow', 'is_active']
    search_fields = ['name', 'action']
