from django.contrib import admin
from .models import (
    Product, UserPreference, ChatSession, ChatMessage, InteractionHistory,
    UserProfile, Wishlist, PurchaseHistory, RecommendationHistory, UserInsight
)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'rating', 'created_at']
    list_filter = ['category', 'rating', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['-rating', '-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'created_at', 'updated_at']
    search_fields = ['user_id']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user_id', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['session_id', 'user_id']
    readonly_fields = ['session_id', 'created_at']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'role', 'timestamp']
    list_filter = ['role', 'timestamp']
    search_fields = ['content']
    readonly_fields = ['timestamp']


@admin.register(InteractionHistory)
class InteractionHistoryAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'interaction_type', 'timestamp']
    list_filter = ['interaction_type', 'timestamp']
    search_fields = ['user_id', 'query_text']
    readonly_fields = ['timestamp']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'default_budget_min', 'default_budget_max', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'phone']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__username', 'product__name']
    readonly_fields = ['added_at']


@admin.register(PurchaseHistory)
class PurchaseHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'price_at_purchase', 'quantity', 'purchase_date', 'rating']
    list_filter = ['purchase_date', 'rating']
    search_fields = ['user__username', 'product__name']
    readonly_fields = ['purchase_date']


@admin.register(RecommendationHistory)
class RecommendationHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'shown_at']
    list_filter = ['shown_at']
    search_fields = ['user__username']
    readonly_fields = ['shown_at']


@admin.register(UserInsight)
class UserInsightAdmin(admin.ModelAdmin):
    list_display = ['user', 'insight_type', 'title', 'is_read', 'created_at']
    list_filter = ['insight_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'description']
    readonly_fields = ['created_at']
