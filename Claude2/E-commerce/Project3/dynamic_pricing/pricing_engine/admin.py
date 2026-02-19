from django.contrib import admin
from .models import Product, SalesHistory, CompetitorPrice, PriceHistory


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'current_price', 'base_cost', 'stock_quantity', 'margin']
    list_filter = ['category']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SalesHistory)
class SalesHistoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity_sold', 'sale_price', 'revenue', 'date']
    list_filter = ['product', 'date']
    date_hierarchy = 'date'


@admin.register(CompetitorPrice)
class CompetitorPriceAdmin(admin.ModelAdmin):
    list_display = ['product', 'competitor_name', 'price', 'recorded_at']
    list_filter = ['product', 'competitor_name']
    date_hierarchy = 'recorded_at'


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'old_price', 'new_price', 'price_change_percent', 'reason', 'timestamp']
    list_filter = ['product', 'reason']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']
