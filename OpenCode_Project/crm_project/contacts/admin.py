"""
Admin configuration for CRM Contacts app
"""

from django.contrib import admin
from .models import Company, Contact, Tag


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'industry', 'city', 'country', 'total_contacts', 'total_deals', 'created_at']
    list_filter = ['industry', 'company_size']
    search_fields = ['name', 'email', 'city']
    prepopulated_fields = {'name': ('name',)}


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'company', 'job_title', 'status', 'phone', 'created_at']
    list_filter = ['status', 'department', 'company']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    raw_id_fields = ['company']


admin.register(Tag)
