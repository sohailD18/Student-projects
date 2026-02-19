"""
Admin configuration for Multi-Vendor Marketplace
"""

from django.contrib import admin
from .models import (
    Vendor, Category, Product, Order, OrderItem, Commission,
    Payout, Cart, CartItem, Review, Wishlist
)

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['store_name', 'user', 'is_approved', 'is_active', 'total_sales', 'created_at']
    list_filter = ['is_approved', 'is_active']
    search_fields = ['store_name', 'user__username']
    prepopulated_fields = {'store_slug': ('store_name',)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active']
    list_filter = ['is_active', 'parent']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'vendor', 'category', 'price', 'stock_quantity', 'status', 'view_count']
    list_filter = ['status', 'category', 'vendor']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'sku']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'status', 'total', 'created_at']
    list_filter = ['status', 'order_type']
    search_fields = ['order_number', 'customer__username']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'vendor', 'quantity', 'subtotal', 'status']
    list_filter = ['status', 'vendor']


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ['order', 'vendor', 'amount', 'rate', 'status', 'created_at']
    list_filter = ['status', 'vendor']


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'amount', 'method', 'status', 'requested_at', 'processed_at']
    list_filter = ['status', 'method']


admin.register(Category)
admin.register(Review)
admin.register(Cart)
admin.register(CartItem)
admin.register(Wishlist)
