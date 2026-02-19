"""
Django Admin Configuration for FinRisk AI
"""
from django.contrib import admin
from .models import UserProfile, Transaction, RiskProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'age', 'annual_income', 'employment_status', 'income_stability', 'created_at']
    list_filter = ['employment_status', 'income_stability', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'user_profile', 'category', 'transaction_type', 'amount', 'created_at']
    list_filter = ['transaction_type', 'category', 'date', 'created_at']
    search_fields = ['user_profile__name', 'description']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'


@admin.register(RiskProfile)
class RiskProfileAdmin(admin.ModelAdmin):
    list_display = ['user_profile', 'classification', 'risk_score', 'savings_rate', 'spending_pattern', 'created_at']
    list_filter = ['classification', 'spending_pattern', 'created_at']
    search_fields = ['user_profile__name']
    readonly_fields = ['created_at', 'updated_at']
