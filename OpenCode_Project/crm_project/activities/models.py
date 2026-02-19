"""
Models for CRM Activities app
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Activity(models.Model):
    TYPE_CHOICES = [
        ('CALL', 'Call'),
        ('EMAIL', 'Email'),
        ('MEETING', 'Meeting'),
        ('NOTE', 'Note'),
        ('TASK', 'Task'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    
    activity_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    contact = models.ForeignKey('contacts.Contact', on_delete=models.CASCADE, null=True, blank=True, related_name='activities')
    company = models.ForeignKey('contacts.Company', on_delete=models.CASCADE, null=True, blank=True, related_name='activities')
    deal = models.ForeignKey('deals.Deal', on_delete=models.CASCADE, null=True, blank=True, related_name='activity_deals')
    
    subject = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    activity_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField(null=True, blank=True)
    duration = models.PositiveIntegerField(default=0, help_text="Duration in minutes")
    
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    is_reminder = models.BooleanField(default=False)
    reminder_date = models.DateTimeField(null=True, blank=True)
    
    outcome = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-activity_date', '-created_at']
    
    def __str__(self):
        return f"{self.activity_type}: {self.subject}"
    
    @property
    def is_overdue(self):
        if self.due_date and self.status == 'PENDING':
            return self.due_date < timezone.now().date()
        return False
