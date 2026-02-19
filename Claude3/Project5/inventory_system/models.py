from django.db import models
from django.utils import timezone


class Product(models.Model):
    """Model representing a product in inventory."""
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

    name = models.CharField(max_length=200, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    current_stock = models.IntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.name

    @property
    def stock_value(self):
        """Calculate total stock value."""
        return self.current_stock * float(self.unit_price)


class SalesRecord(models.Model):
    """Model representing sales data for products."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales_records')
    quantity_sold = models.IntegerField()
    sale_date = models.DateField(default=timezone.now)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['-sale_date']
        verbose_name_plural = 'Sales Records'

    def __str__(self):
        return f"{self.product.name} - {self.quantity_sold} units on {self.sale_date}"

    def save(self, *args, **kwargs):
        """Calculate revenue automatically when saving."""
        if self.revenue is None:
            self.revenue = self.quantity_sold * self.product.unit_price
        super().save(*args, **kwargs)


class InventoryPrediction(models.Model):
    """Model representing AI predictions for inventory levels."""
    STATUS_CHOICES = [
        ('low_stock', 'Low Stock'),
        ('optimal', 'Optimal'),
        ('overstock', 'Overstock'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='predictions')
    predicted_demand = models.IntegerField()
    recommended_stock = models.IntegerField()
    date_of_prediction = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='optimal')
    confidence_score = models.FloatField(null=True, blank=True)
    prediction_period = models.CharField(max_length=50, default='Next 30 days')

    class Meta:
        ordering = ['-date_of_prediction']
        verbose_name_plural = 'Inventory Predictions'

    def __str__(self):
        return f"{self.product.name} - {self.status} ({self.date_of_prediction.date()})"

    def calculate_status(self):
        """Determine stock status based on current vs recommended."""
        current = self.product.current_stock
        recommended = self.recommended_stock

        if current < recommended:
            return 'low_stock'
        elif current > recommended * 1.5:
            return 'overstock'
        else:
            return 'optimal'

    def save(self, *args, **kwargs):
        """Calculate status automatically when saving."""
        self.status = self.calculate_status()
        super().save(*args, **kwargs)
