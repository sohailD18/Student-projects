from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class UserInteraction(models.Model):
    INTERACTION_TYPES = [
        ('view', 'View'),
        ('purchase', 'Purchase'),
        ('cart', 'Add to Cart'),
        ('wishlist', 'Add to Wishlist'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.interaction_type} - {self.product.name}"

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "User Interaction"
