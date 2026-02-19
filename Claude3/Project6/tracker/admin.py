"""
Admin configuration for Carbon Credit Tracking System.
"""
from django.contrib import admin
from .models import Industry, EmissionRecord, CarbonPrice, PredictionLog


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ['name', 'industry_type', 'emission_limit', 'total_emissions', 'carbon_surplus', 'efficiency_score']
    list_filter = ['industry_type']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'industry_type', 'description')
        }),
        ('Emission Settings', {
            'fields': ('emission_limit',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EmissionRecord)
class EmissionRecordAdmin(admin.ModelAdmin):
    list_display = ['industry', 'year', 'month', 'emission_amount', 'created_at']
    list_filter = ['year', 'month', 'industry']
    search_fields = ['industry__name']
    date_hierarchy = 'created_at'

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['created_at']
        return []


@admin.register(CarbonPrice)
class CarbonPriceAdmin(admin.ModelAdmin):
    list_display = ['date', 'price_per_ton', 'created_at']
    list_filter = ['date']
    date_hierarchy = 'date'
    readonly_fields = ['created_at']


@admin.register(PredictionLog)
class PredictionLogAdmin(admin.ModelAdmin):
    list_display = ['industry', 'prediction_year', 'prediction_month', 'predicted_emission',
                   'trading_suggestion', 'confidence_score', 'prediction_date']
    list_filter = ['trading_suggestion', 'prediction_year', 'prediction_month']
    search_fields = ['industry__name']
    readonly_fields = ['prediction_date']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['prediction_date']
        return []
