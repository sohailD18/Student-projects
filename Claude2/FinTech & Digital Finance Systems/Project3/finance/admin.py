"""
Django Admin configuration for Finance models.
"""
from django.contrib import admin
from .models import Transaction, Budget, FinancialInsight


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin interface for Transaction model."""
    list_display = ['date', 'description', 'amount', 'transaction_type', 'category', 'created_at']
    list_filter = ['transaction_type', 'category', 'date']
    search_fields = ['description', 'category']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Transaction Details', {
            'fields': ('amount', 'date', 'transaction_type', 'category', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    """Admin interface for Budget model."""
    list_display = ['category', 'month', 'year', 'limit_amount', 'spent_amount', 'remaining_amount', 'status']
    list_filter = ['category', 'month', 'year']
    search_fields = ['category']
    readonly_fields = ['created_at', 'updated_at', 'spent_amount', 'remaining_amount', 'utilization_percentage', 'status']

    fieldsets = (
        ('Budget Details', {
            'fields': ('category', 'limit_amount', 'month', 'year')
        }),
        ('Budget Status (Read-only)', {
            'fields': ('spent_amount', 'remaining_amount', 'utilization_percentage', 'status'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def spent_amount(self, obj):
        return f"${obj.spent_amount:.2f}"
    spent_amount.short_description = 'Spent'

    def remaining_amount(self, obj):
        return f"${obj.remaining_amount:.2f}"
    remaining_amount.short_description = 'Remaining'

    def utilization_percentage(self, obj):
        return f"{obj.utilization_percentage:.1f}%"
    utilization_percentage.short_description = 'Utilization'

    def status(self, obj):
        color_map = {
            'Over Budget': 'red',
            'Near Limit': 'orange',
            'Moderate': 'yellow',
            'On Track': 'green'
        }
        color = color_map.get(obj.status, 'black')
        return f'<span style="color: {color}; font-weight: bold;">{obj.status}</span>'
    status.allow_tags = True
    status.short_description = 'Status'


@admin.register(FinancialInsight)
class FinancialInsightAdmin(admin.ModelAdmin):
    """Admin interface for FinancialInsight model."""
    list_display = ['title', 'insight_type', 'is_read', 'created_at']
    list_filter = ['insight_type', 'is_read', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Insight Details', {
            'fields': ('insight_type', 'title', 'description', 'is_read')
        }),
        ('Related Data', {
            'fields': ('data',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
