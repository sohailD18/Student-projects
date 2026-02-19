"""
Django admin configuration for the fraud detection system.
"""
from django.contrib import admin
from .models import Transaction, ModelMetrics, FraudAlert, AuditLog


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id', 'amount', 'merchant', 'timestamp',
        'is_fraud', 'risk_score', 'is_flagged'
    ]
    list_filter = ['is_fraud', 'is_flagged', 'transaction_type', 'merchant_category', 'country']
    search_fields = ['transaction_id', 'merchant', 'account_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-timestamp']

    fieldsets = (
        ('Transaction Details', {
            'fields': ('transaction_id', 'transaction_type', 'amount', 'currency')
        }),
        ('Location & Merchant', {
            'fields': ('location', 'country', 'city', 'ip_address', 'merchant', 'merchant_category')
        }),
        ('Account Information', {
            'fields': ('account_id', 'card_number_last4')
        }),
        ('Timestamp', {
            'fields': ('timestamp',)
        }),
        ('AI Detection Results', {
            'fields': ('is_fraud', 'risk_score', 'fraud_reason', 'is_flagged', 'is_reviewed')
        }),
        ('Additional Metadata', {
            'fields': ('device_id', 'browser', 'os', 'features')
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_risk_level(self, obj):
        return obj.get_risk_level()
    get_risk_level.short_description = 'Risk Level'


@admin.register(ModelMetrics)
class ModelMetricsAdmin(admin.ModelAdmin):
    list_display = [
        'model_name', 'model_version', 'accuracy', 'precision', 'recall', 'f1_score', 'trained_at'
    ]
    readonly_fields = ['trained_at']
    ordering = ['-trained_at']


@admin.register(FraudAlert)
class FraudAlertAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'alert_type', 'status', 'risk_score', 'created_at']
    list_filter = ['status', 'alert_type']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'entity_type', 'entity_id', 'timestamp']
    list_filter = ['action', 'entity_type']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
