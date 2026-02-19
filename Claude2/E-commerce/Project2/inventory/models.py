"""
Database Models for Inventory Management System

This module defines the core data models:
1. Product: Represents items in inventory
2. SalesData: Historical sales records for forecasting
"""

from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Product(models.Model):
    """
    Product Model

    Represents a product in the inventory with stock tracking.

    Fields:
        name: Product name
        category: Product category for grouping
        current_stock: Current quantity in stock
        price: Unit price
        safety_stock: Minimum stock level to maintain
        created_at: Timestamp when product was created
        updated_at: Timestamp of last update
    """

    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing'),
        ('food', 'Food & Beverages'),
        ('home', 'Home & Garden'),
        ('sports', 'Sports & Outdoors'),
        ('toys', 'Toys & Games'),
        ('books', 'Books & Media'),
        ('other', 'Other'),
    ]

    name = models.CharField(
        max_length=200,
        help_text="Product name"
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='other',
        help_text="Product category"
    )

    current_stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Current quantity in stock"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Unit price"
    )

    safety_stock = models.IntegerField(
        default=10,
        validators=[MinValueValidator(0)],
        help_text="Minimum stock level to maintain (buffer)"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when product was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp of last update"
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return f"{self.name} ({self.category}) - Stock: {self.current_stock}"

    @property
    def inventory_value(self):
        """Calculate total value of current stock"""
        return self.current_stock * self.price

    def get_stock_status(self, predicted_demand=0):
        """
        Determine stock status based on current stock and predicted demand.

        Args:
            predicted_demand: Forecasted demand for next period

        Returns:
            str: 'low', 'good', or 'overstock'
        """
        if self.current_stock == 0:
            return 'out_of_stock'
        elif self.current_stock < self.safety_stock:
            return 'critical'
        elif predicted_demand > 0:
            if self.current_stock < predicted_demand + self.safety_stock:
                return 'low'
            elif self.current_stock > predicted_demand * 2:
                return 'overstock'
            else:
                return 'good'
        else:
            return 'good'


class SalesData(models.Model):
    """
    SalesData Model

    Represents historical sales data for demand forecasting.
    Records daily sales quantities for each product.

    Fields:
        product: Foreign key to Product
        date: Date of sales
        quantity_sold: Number of units sold
        revenue: Calculated revenue (quantity * price)
        created_at: Timestamp when record was created
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='sales_data',
        help_text="Product sold"
    )

    date = models.DateField(
        help_text="Date of sales"
    )

    quantity_sold = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Number of units sold"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when record was created"
    )

    class Meta:
        ordering = ['-date', 'product']
        verbose_name = 'Sales Data'
        verbose_name_plural = 'Sales Data'
        # Ensure one record per product per date
        unique_together = ['product', 'date']
        indexes = [
            models.Index(fields=['product', 'date']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.date}: {self.quantity_sold} units"

    @property
    def revenue(self):
        """Calculate revenue from sales"""
        return self.quantity_sold * self.product.price

    def save(self, *args, **kwargs):
        """
        Override save to ensure data integrity.
        Validates that quantity_sold is not negative.
        """
        if self.quantity_sold < 0:
            raise ValueError("Quantity sold cannot be negative")
        super().save(*args, **kwargs)
