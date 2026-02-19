from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Task(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    required_skills = models.CharField(
        max_length=200,
        help_text='Enter required skills, separated by commas'
    )
    estimated_duration = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text='Estimated duration in hours'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tasks'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_skills_list(self):
        """Return skills as a list"""
        return [skill.strip() for skill in self.required_skills.split(',')]

    def matches_user_skills(self, user_skills):
        """Check if task skills match user skills"""
        if not user_skills:
            return False
        user_skills_list = [skill.strip().lower() for skill in user_skills.split(',')]
        task_skills_list = [skill.strip().lower() for skill in self.required_skills.split(',')]
        return any(skill in user_skills_list for skill in task_skills_list)
