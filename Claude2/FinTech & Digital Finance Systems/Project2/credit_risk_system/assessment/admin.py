"""
Admin configuration for Credit Risk Assessment System
"""
from django.contrib import admin
from .models import Applicant, FinancialData


@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    """
    Admin interface for Applicant model
    """
    list_display = [
        'name', 'email', 'annual_income', 'employment_status',
        'risk_category', 'eligibility_status', 'created_at'
    ]
    list_filter = [
        'employment_status', 'risk_category', 'eligibility_status', 'created_at'
    ]
    search_fields = ['name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'risk_probability',
                      'risk_category', 'eligibility_status']

    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Financial Information', {
            'fields': ('annual_income', 'employment_status',
                      'years_employed', 'debt_to_income_ratio')
        }),
        ('Assessment Results', {
            'fields': ('risk_probability', 'risk_category', 'eligibility_status'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FinancialData)
class FinancialDataAdmin(admin.ModelAdmin):
    """
    Admin interface for FinancialData model
    """
    list_display = [
        'applicant', 'credit_score', 'num_open_loans',
        'late_payments', 'bankruptcies', 'home_ownership_status'
    ]
    list_filter = [
        'home_ownership_status', 'bankruptcies', 'created_at'
    ]
    search_fields = ['applicant__name', 'applicant__email']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Credit Information', {
            'fields': ('applicant', 'credit_score', 'num_open_loans',
                      'num_credit_lines', 'late_payments', 'bankruptcies')
        }),
        ('Additional Details', {
            'fields': ('home_ownership_status', 'total_credit_limit',
                      'credit_utilization')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
