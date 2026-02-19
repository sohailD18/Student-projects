from django.db import models
from django.contrib.auth.models import User
import uuid


class Product(models.Model):
    """Model representing electronic products in the store."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)  # Laptop, Phone, Headphones, etc.
    image_url = models.URLField(max_length=500, blank=True)
    specs = models.JSONField(default=dict)  # Store specifications as JSON
    rating = models.FloatField(default=0.0)  # Rating out of 5.0
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-rating', '-created_at']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['price']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return f"{self.name} - ${self.price}"


class UserPreference(models.Model):
    """Model to store user preferences for personalized recommendations."""
    user_id = models.CharField(max_length=255, unique=True)
    preferred_categories = models.JSONField(default=list)  # List of category names
    budget_range = models.JSONField(default=dict)  # {'min': 0, 'max': 10000}
    style_tags = models.JSONField(default=list)  # List of style preferences
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user_id}"


class ChatSession(models.Model):
    """Model to track individual chat sessions."""
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Session {self.session_id}"


class ChatMessage(models.Model):
    """Model to store individual chat messages in a session."""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class InteractionHistory(models.Model):
    """Model to track user interactions and clicked products."""
    INTERACTION_TYPES = [
        ('view', 'View'),
        ('click', 'Click'),
        ('compare', 'Compare'),
        ('purchase', 'Purchase'),
    ]

    user_id = models.CharField(max_length=255)
    query_text = models.TextField(blank=True)
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES, default='view')
    clicked_products = models.ManyToManyField(Product, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='interactions'
    )

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user_id} - {self.interaction_type} at {self.timestamp}"


# ============================================
# USER AUTHENTICATION & PROFILE MODELS
# ============================================

class UserProfile(models.Model):
    """Extended user profile with shopping preferences."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shopping_profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.URLField(max_length=500, blank=True, null=True)
    default_budget_min = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    default_budget_max = models.DecimalField(max_digits=10, decimal_places=2, default=5000)
    preferred_brands = models.JSONField(default=list)
    shopping_interests = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


class Wishlist(models.Model):
    """User wishlist for products they want to buy later."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class PurchaseHistory(models.Model):
    """Track user purchases for better recommendations."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='purchased_by')
    purchase_date = models.DateTimeField(auto_now_add=True)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    rating = models.FloatField(null=True, blank=True)  # User's rating after purchase
    review = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-purchase_date']

    def __str__(self):
        return f"{self.user.username} - {self.product.name if self.product else 'Deleted Product'}"


class RecommendationHistory(models.Model):
    """Track recommendations shown to users for analytics."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations', null=True, blank=True)
    products = models.ManyToManyField(Product, related_name='recommended_in')
    context = models.JSONField(default=dict)  # Store recommendation context
    shown_at = models.DateTimeField(auto_now_add=True)
    clicked = models.ManyToManyField(Product, related_name='clicked_recommendations', blank=True)

    class Meta:
        ordering = ['-shown_at']

    def __str__(self):
        return f"Recommendations for {self.user.username if self.user else 'Anonymous'} at {self.shown_at}"


class UserInsight(models.Model):
    """Store AI-generated insights about user shopping behavior."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='insights')
    insight_type = models.CharField(max_length=50)  # 'budget_trend', 'category_preference', 'price_sensitivity'
    title = models.CharField(max_length=200)
    description = models.TextField()
    data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"
