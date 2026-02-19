"""
Models for CRM Contacts app
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Company(models.Model):
    INDUSTRY_CHOICES = [
        ('TECHNOLOGY', 'Technology'),
        ('FINANCE', 'Finance'),
        ('HEALTHCARE', 'Healthcare'),
        ('EDUCATION', 'Education'),
        ('RETAIL', 'Retail'),
        ('MANUFACTURING', 'Manufacturing'),
        ('SERVICES', 'Services'),
        ('OTHER', 'Other'),
    ]
    
    SIZE_CHOICES = [
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('500+', '500+ employees'),
    ]
    
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='companies/', blank=True, null=True)
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES, blank=True)
    company_size = models.CharField(max_length=20, choices=SIZE_CHOICES, blank=True)
    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def total_contacts(self):
        return self.contacts.count()
    
    @property
    def total_deals(self):
        return self.deals.count()


class Contact(models.Model):
    STATUS_CHOICES = [
        ('LEAD', 'Lead'),
        ('PROSPECT', 'Prospect'),
        ('CUSTOMER', 'Customer'),
        ('INACTIVE', 'Inactive'),
    ]
    
    SALUTATION_CHOICES = [
        ('MR', 'Mr.'),
        ('MS', 'Ms.'),
        ('MRS', 'Mrs.'),
        ('DR', 'Dr.'),
        ('PROF', 'Prof.'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts', null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='contacts', null=True, blank=True)
    
    salutation = models.CharField(max_length=10, choices=SALUTATION_CHOICES, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    mobile = models.CharField(max_length=20, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='LEAD')
    source = models.CharField(max_length=100, blank=True)
    
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    linkedin = models.URLField(blank=True)
    twitter = models.CharField(max_length=100, blank=True)
    
    notes = models.TextField(blank=True)
    tags = models.CharField(max_length=500, blank=True)
    
    last_contacted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def total_deals(self):
        return self.deals.count()


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#007bff')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
