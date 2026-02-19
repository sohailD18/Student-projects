"""
ProductivityMind - Data Models for Task Management
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import datetime


class Project(models.Model):
    """
    Project model to group related tasks together
    """
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    members = models.ManyToManyField(User, through='ProjectMember', related_name='projects')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def total_tasks(self):
        return self.tasks.count()

    @property
    def completed_tasks(self):
        return self.tasks.filter(status='done').count()

    @property
    def progress_percentage(self):
        total = self.total_tasks
        if total == 0:
            return 0
        return round((self.completed_tasks / total) * 100, 2)


class ProjectMember(models.Model):
    """
    Through model for Project-User relationship with roles
    """
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.role})"


class Task(models.Model):
    """
    Main Task model with all required fields for productivity tracking
    """
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')

    # Project Association
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,
        blank=True
    )

    # Assignment
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )

    # Time Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Estimation
    estimated_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )

    actual_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )

    # Dependencies (Task A cannot start until Task B is done)
    blocked_by = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='blocking'
    )

    # Categorization
    tags = models.ManyToManyField('Tag', blank=True, related_name='tasks')
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
    )

    # AI-Generated Fields
    smart_priority_score = models.IntegerField(
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="AI-calculated priority score (0-100)"
    )

    is_at_risk = models.BooleanField(
        default=False,
        help_text="Flagged by risk prediction algorithm"
    )

    risk_level = models.CharField(
        max_length=20,
        choices=[
            ('none', 'No Risk'),
            ('low', 'Low Risk'),
            ('medium', 'Medium Risk'),
            ('high', 'High Risk'),
            ('critical', 'Critical Risk'),
        ],
        default='none'
    )

    class Meta:
        ordering = ['-smart_priority_score', 'due_date']
        indexes = [
            models.Index(fields=['status', 'due_date']),
            models.Index(fields=['assignee', 'status']),
            models.Index(fields=['-smart_priority_score']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Update completed_at timestamp when status changes to done
        if self.status == 'done' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'done' and self.completed_at:
            self.completed_at = None

        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if self.due_date and self.status != 'done':
            return timezone.now() > self.due_date
        return False

    @property
    def days_until_due(self):
        """Calculate days until due date"""
        if self.due_date:
            delta = self.due_date - timezone.now()
            return delta.days
        return None

    @property
    def blocking_count(self):
        """Number of tasks this task is blocking"""
        return self.blocking.count()

    @property
    def blocked_by_count(self):
        """Number of tasks blocking this task"""
        return self.blocked_by.count()

    @property
    def can_start(self):
        """Check if all dependencies are satisfied"""
        return self.blocked_by.filter(status__in=['todo', 'in_progress']).count() == 0

    @property
    def completion_percentage(self):
        """Calculate completion based on status"""
        status_map = {'todo': 0, 'in_progress': 50, 'done': 100, 'cancelled': 0}
        return status_map.get(self.status, 0)


class Tag(models.Model):
    """Tags for task categorization and filtering"""
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#007bff', help_text="Hex color code")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    """Categories for organizing tasks"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class or emoji")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class WorkLog(models.Model):
    """
    Work log for tracking time spent on tasks
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='work_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='work_logs')
    hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    notes = models.TextField(blank=True)
    logged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-logged_at']
        verbose_name_plural = "Work Logs"

    def __str__(self):
        return f"{self.user.username} - {self.task.title} ({self.hours}h)"


class UserProfile(models.Model):
    """
    Extended user profile for additional user information
    """
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Project Manager'),
        ('team_lead', 'Team Lead'),
        ('member', 'Team Member'),
        ('viewer', 'Viewer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    bio = models.TextField(blank=True)
    avatar_url = models.URLField(blank=True)
    department = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    # Productivity Settings
    working_hours_per_day = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=8.0,
        validators=[MinValueValidator(1), MaxValueValidator(24)]
    )

    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    deadline_reminders = models.BooleanField(default=True)

    class Meta:
        verbose_name = "User Profile"

    def __str__(self):
        return f"{self.user.username}'s Profile ({self.get_role_display()})"

    @property
    def total_tasks_completed(self):
        return self.user.assigned_tasks.filter(status='done').count()

    @property
    def total_hours_logged(self):
        return self.user.work_logs.aggregate(
            total=models.Sum('hours')
        )['total'] or 0

    def has_permission(self, permission):
        """Check if user has specific permission based on role"""
        role_permissions = {
            'admin': ['all'],
            'manager': ['view', 'create', 'edit', 'delete', 'assign', 'report'],
            'team_lead': ['view', 'create', 'edit', 'assign', 'report'],
            'member': ['view', 'create', 'edit_own'],
            'viewer': ['view'],
        }
        user_perms = role_permissions.get(self.role, [])
        return 'all' in user_perms or permission in user_perms


class TaskDependency(models.Model):
    """
    Explicit dependency tracking with additional metadata
    """
    dependent_task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='dependencies_as_dependent'
    )
    blocking_task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='dependencies_as_blocking'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('dependent_task', 'blocking_task')
        verbose_name_plural = "Task Dependencies"

    def __str__(self):
        return f"{self.dependent_task.title} depends on {self.blocking_task.title}"
