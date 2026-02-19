"""
Models for CRM Deals app
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


class Pipeline(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class PipelineStage(models.Model):
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='stages')
    name = models.CharField(max_length=100)
    stage_key = models.CharField(max_length=50)
    order = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=7, default='#007bff')
    win_probability = models.PositiveIntegerField(default=0)
    is_won = models.BooleanField(default=False)
    is_lost = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.pipeline.name} - {self.name}"


class Deal(models.Model):
    SOURCE_CHOICES = [
        ('WEBSITE', 'Website'),
        ('REFERRAL', 'Referral'),
        ('COLD_CALL', 'Cold Call'),
        ('EMAIL', 'Email'),
        ('SOCIAL_MEDIA', 'Social Media'),
        ('TRADE_SHOW', 'Trade Show'),
        ('OTHER', 'Other'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deals', null=True, blank=True)
    contact = models.ForeignKey('contacts.Contact', on_delete=models.CASCADE, related_name='deals', null=True, blank=True)
    company = models.ForeignKey('contacts.Company', on_delete=models.CASCADE, related_name='deals', null=True, blank=True)
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    pipeline = models.ForeignKey(Pipeline, on_delete=models.SET_NULL, null=True, blank=True)
    stage = models.ForeignKey(PipelineStage, on_delete=models.SET_NULL, null=True, related_name='deals')
    
    value = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=3, default='USD')
    
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    
    expected_close_date = models.DateField(null=True, blank=True)
    actual_close_date = models.DateField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def days_until_close(self):
        if self.expected_close_date:
            delta = self.expected_close_date - timezone.now().date()
            return delta.days
        return None
    
    @property
    def is_overdue(self):
        if self.expected_close_date and self.is_active:
            return self.expected_close_date < timezone.now().date()
        return False


class DealActivity(models.Model):
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name='deal_activities')
    activity_type = models.CharField(max_length=50)
    description = models.TextField()
    activity_date = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.deal.title} - {self.activity_type}"
