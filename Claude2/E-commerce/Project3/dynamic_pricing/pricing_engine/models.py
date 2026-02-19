from django.db import models
from decimal import Decimal


class Product(models.Model):
    """Product model representing items in the inventory."""
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    base_cost = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def margin(self):
        """Calculate profit margin percentage."""
        if self.current_price > 0:
            return ((self.current_price - self.base_cost) / self.current_price) * 100
        return 0

    @property
    def profit(self):
        """Calculate profit per unit."""
        return self.current_price - self.base_cost


class SalesHistory(models.Model):
    """Sales history tracking for products."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales_history')
    quantity_sold = models.IntegerField()
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField()

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Sales Histories'

    def __str__(self):
        return f"{self.product.name} - {self.quantity_sold} units"

    @property
    def revenue(self):
        """Calculate total revenue for this sale."""
        return self.quantity_sold * self.sale_price


class CompetitorPrice(models.Model):
    """Competitor pricing tracking."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='competitor_prices')
    competitor_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']
        verbose_name_plural = 'Competitor Prices'

    def __str__(self):
        return f"{self.competitor_name}: ${self.price}"


class PriceHistory(models.Model):
    """Price change history for products."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Price Histories'

    def __str__(self):
        return f"{self.product.name}: ${self.old_price} -> ${self.new_price}"

    @property
    def price_change(self):
        """Calculate the price change amount."""
        return self.new_price - self.old_price

    @property
    def price_change_percent(self):
        """Calculate the price change percentage."""
        if self.old_price > 0:
            return ((self.new_price - self.old_price) / self.old_price) * 100
        return 0
