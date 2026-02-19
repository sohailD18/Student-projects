"""
Django Admin Configuration for Inventory Management System
"""

from django.contrib import admin
from .models import Product, SalesData


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin interface for Product model
    """
    list_display = ['name', 'category', 'current_stock', 'safety_stock', 'price', 'inventory_value', 'updated_at']
    list_filter = ['category', 'created_at', 'updated_at']
    search_fields = ['name', 'category']
    list_editable = ['current_stock', 'safety_stock', 'price']
    readonly_fields = ['created_at', 'updated_at', 'inventory_value']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category')
        }),
        ('Stock Information', {
            'fields': ('current_stock', 'safety_stock')
        }),
        ('Pricing', {
            'fields': ('price',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'inventory_value'),
            'classes': ('collapse',)
        }),
    )

    def inventory_value(self, obj):
        return f"${obj.inventory_value:.2f}"
    inventory_value.short_description = 'Total Value'


@admin.register(SalesData)
class SalesDataAdmin(admin.ModelAdmin):
    """
    Admin interface for SalesData model
    """
    list_display = ['product', 'date', 'quantity_sold', 'revenue_display', 'created_at']
    list_filter = ['date', 'product__category']
    search_fields = ['product__name']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'revenue_display']

    fieldsets = (
        ('Sales Information', {
            'fields': ('product', 'date', 'quantity_sold')
        }),
        ('Calculated Fields', {
            'fields': ('revenue_display',),
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def revenue_display(self, obj):
        return f"${obj.revenue:.2f}"
    revenue_display.short_description = 'Revenue'

    def get_queryset(self, request):
        """Optimize queries with prefetch_related"""
        qs = super().get_queryset(request)
        return qs.select_related('product')
