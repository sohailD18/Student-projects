from django.contrib import admin
from .models import Transaction, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type']
    list_filter = ['type']
    search_fields = ['name']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'amount', 'date', 'description', 'created_at']
    list_filter = ['category', 'date', 'created_at']
    search_fields = ['user__username', 'description']
    date_hierarchy = 'date'
    readonly_fields = ['created_at']
