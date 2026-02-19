from django.contrib import admin
from .models import Product, SalesRecord, InventoryPrediction


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'current_stock', 'unit_price', 'stock_value', 'updated_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'category']
    readonly_fields = ['created_at', 'updated_at', 'stock_value']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category')
        }),
        ('Inventory Details', {
            'fields': ('current_stock', 'unit_price')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SalesRecord)
class SalesRecordAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity_sold', 'sale_date', 'revenue']
    list_filter = ['sale_date', 'product__category']
    search_fields = ['product__name']
    date_hierarchy = 'sale_date'
    readonly_fields = ['revenue']


@admin.register(InventoryPrediction)
class InventoryPredictionAdmin(admin.ModelAdmin):
    list_display = ['product', 'predicted_demand', 'recommended_stock', 'status', 'date_of_prediction', 'confidence_score']
    list_filter = ['status', 'date_of_prediction']
    search_fields = ['product__name']
    readonly_fields = ['date_of_prediction', 'confidence_score']

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ['product', 'predicted_demand', 'recommended_stock', 'status']
        return self.readonly_fields
