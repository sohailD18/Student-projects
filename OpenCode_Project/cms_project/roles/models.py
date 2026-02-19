from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType


class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    
    permissions = models.ManyToManyField(Permission, related_name='roles', blank=True)
    groups = models.ManyToManyField(Group, related_name='roles', blank=True)
    
    is_active = models.BooleanField(default=True)
    is_system_role = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def user_count(self):
        return self.role_assignments.count()


class RoleAssignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_assignments')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_assignments')
    
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_roles')
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'role']
        verbose_name_plural = 'Role Assignments'
    
    def __str__(self):
        return f"{self.user.username} - {self.role.name}"


class PagePermission(models.Model):
    PERMISSION_CHOICES = [
        ('VIEW', 'View'),
        ('EDIT', 'Edit'),
        ('DELETE', 'Delete'),
        ('PUBLISH', 'Publish'),
        ('MANAGE', 'Manage'),
    ]

    page = models.ForeignKey('pages.Page', on_delete=models.CASCADE, related_name='permissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='page_permissions', null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='page_permissions', null=True, blank=True)
    
    permission = models.CharField(max_length=20, choices=PERMISSION_CHOICES)
    
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='granted_page_permissions')
    granted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['page', 'user', 'permission']
        verbose_name_plural = 'Page Permissions'
    
    def __str__(self):
        target = self.user.username if self.user else self.role.name
        return f"{target} - {self.permission} on {self.page.title}"


class MediaPermission(models.Model):
    PERMISSION_CHOICES = [
        ('VIEW', 'View'),
        ('UPLOAD', 'Upload'),
        ('EDIT', 'Edit'),
        ('DELETE', 'Delete'),
        ('MANAGE', 'Manage'),
    ]

    folder = models.ForeignKey('media.MediaFolder', on_delete=models.CASCADE, related_name='permissions', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='media_permissions', null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='media_permissions', null=True, blank=True)
    
    permission = models.CharField(max_length=20, choices=PERMISSION_CHOICES)
    
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='granted_media_permissions')
    granted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['folder', 'user', 'permission']
        verbose_name_plural = 'Media Permissions'
    
    def __str__(self):
        target = self.user.username if self.user else self.role.name
        folder = self.folder.name if self.folder else 'All'
        return f"{target} - {self.permission} on {folder}"


class Workflow(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class WorkflowState(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='states')
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)
    
    order = models.PositiveIntegerField(default=0)
    is_initial = models.BooleanField(default=False)
    is_final = models.BooleanField(default=False)
    
    color = models.CharField(max_length=7, default='#6c757d')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['workflow', 'slug']
        verbose_name_plural = 'Workflow States'
    
    def __str__(self):
        return f"{self.workflow.name} - {self.name}"


class WorkflowTransition(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='transitions')
    from_state = models.ForeignKey(WorkflowState, on_delete=models.CASCADE, related_name='outgoing_transitions')
    to_state = models.ForeignKey(WorkflowState, on_delete=models.CASCADE, related_name='incoming_transitions')
    
    name = models.CharField(max_length=255)
    permission_required = models.CharField(max_length=255, blank=True)
    
    action = models.CharField(max_length=255, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['from_state', 'to_state']
        unique_together = ['from_state', 'to_state']
        verbose_name_plural = 'Workflow Transitions'
    
    def __str__(self):
        return f"{self.from_state.name} -> {self.to_state.name}"
