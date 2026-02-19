"""
Models for Multi-Vendor Marketplace
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor')
    store_name = models.CharField(max_length=100)
    store_slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()
    logo = models.ImageField(upload_to='vendor/logos/', blank=True, null=True)
    banner = models.ImageField(upload_to='vendor/banners/', blank=True, null=True)
    
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    bank_routing_number = models.CharField(max_length=50, blank=True)
    paypal_email = models.EmailField(blank=True)
    
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('10.00'))
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    pending_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Vendors"
    
    def __str__(self):
        return self.store_name
    
    @property
    def total_products(self):
        return self.products.count()
    
    @property
    def total_orders(self):
        return OrderItem.objects.filter(product__vendor=self).distinct('order').count()


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name


class Product(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'), ('ACTIVE', 'Active'), ('INACTIVE', 'Inactive'),
    ]
    
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    images = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.00'))
    review_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def current_price(self):
        return self.sale_price if self.sale_price and self.sale_price < self.price else self.price
    
    @property
    def is_in_stock(self):
        return self.stock_quantity > 0


class Review(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    order = models.ForeignKey('Order', on_delete=models.CASCADE, null=True, blank=True)
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=100)
    content = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['product', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'), ('CONFIRMED', 'Confirmed'),
        ('PROCESSING', 'Processing'), ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'), ('CANCELLED', 'Cancelled'),
    ]
    
    ORDER_TYPE_CHOICES = [
        ('ONLINE', 'Online'), ('COD', 'Cash on Delivery'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='ONLINE')
    
    shipping_address = models.TextField()
    billing_address = models.TextField(blank=True)
    
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=12, decimal_places=2)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.order_number
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD{timezone.now().strftime('%Y%m%d%H%M%S')}{self.id or ''}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)


class Commission(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('REFUNDED', 'Refunded'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='commissions')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='commissions')
    order_item = models.OneToOneField(OrderItem, on_delete=models.CASCADE, related_name='commission')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        return f"Commission #{self.id} - {self.vendor.store_name}"
    
    def save(self, *args, **kwargs):
        if not self.rate:
            self.rate = self.vendor.commission_rate
        if not self.amount:
            self.amount = self.order_item.subtotal * (self.rate / 100)
        super().save(*args, **kwargs)


class Payout(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'), ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'), ('FAILED', 'Failed'),
    ]
    
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='payouts')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        return f"Payout #{self.id} - {self.vendor.store_name}"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Cart of {self.user.username}"
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['cart', 'product']
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    @property
    def subtotal(self):
        return self.product.current_price * self.quantity


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'product']
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
