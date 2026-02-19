from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random
import math
from inventory_system.models import Product, SalesRecord


class Command(BaseCommand):
    help = 'Seed the database with dummy products and sales data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--months',
            type=int,
            default=12,
            help='Number of months of historical data to generate (default: 12)'
        )

    def handle(self, *args, **options):
        months = options['months']

        # Sample product data
        products_data = [
            {"name": "Wireless Mouse", "category": "electronics", "stock": 150, "price": 29.99, "monthly_sales": (45, 65)},
            {"name": "Bluetooth Headphones", "category": "electronics", "stock": 80, "price": 79.99, "monthly_sales": (25, 40)},
            {"name": "USB-C Hub", "category": "electronics", "stock": 200, "price": 49.99, "monthly_sales": (60, 90)},
            {"name": "Laptop Sleeve", "category": "electronics", "stock": 120, "price": 24.99, "monthly_sales": (35, 55)},
            {"name": "Mechanical Keyboard", "category": "electronics", "stock": 45, "price": 129.99, "monthly_sales": (15, 30)},
            {"name": "Men's T-Shirt", "category": "clothing", "stock": 300, "price": 19.99, "monthly_sales": (80, 120)},
            {"name": "Women's Jeans", "category": "clothing", "stock": 180, "price": 59.99, "monthly_sales": (40, 70)},
            {"name": "Running Shoes", "category": "sports", "stock": 95, "price": 89.99, "monthly_sales": (30, 50)},
            {"name": "Yoga Mat", "category": "sports", "stock": 150, "price": 34.99, "monthly_sales": (50, 80)},
            {"name": "Coffee Maker", "category": "home", "stock": 65, "price": 79.99, "monthly_sales": (20, 35)},
            {"name": "Desk Lamp", "category": "home", "stock": 110, "price": 39.99, "monthly_sales": (30, 50)},
            {"name": "Novel - Best Seller", "category": "books", "stock": 250, "price": 14.99, "monthly_sales": (70, 100)},
            {"name": "Board Game", "category": "toys", "stock": 85, "price": 44.99, "monthly_sales": (25, 45)},
            {"name": "Smart Watch", "category": "electronics", "stock": 55, "price": 199.99, "monthly_sales": (12, 25)},
            {"name": "Water Bottle", "category": "sports", "stock": 220, "price": 16.99, "monthly_sales": (60, 95)},
        ]

        self.stdout.write(f"Creating products and generating {months} months of sales data...")

        for prod_data in products_data:
            # Create or get product
            product, created = Product.objects.get_or_create(
                name=prod_data["name"],
                defaults={
                    "category": prod_data["category"],
                    "current_stock": prod_data["stock"],
                    "unit_price": prod_data["price"]
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created product: {product.name}"))

            # Generate historical sales data
            existing_records = SalesRecord.objects.filter(product=product).count()
            if existing_records == 0:
                min_sales, max_sales = prod_data["monthly_sales"]

                for month_offset in range(months, 0, -1):
                    # Calculate date for this month
                    target_date = timezone.now().date() - timedelta(days=month_offset * 30)

                    # Generate sales for each day in the month with some variation
                    days_in_month = 30
                    monthly_total = 0

                    for day in range(days_in_month):
                        sale_date = target_date + timedelta(days=day)

                        # Skip weekends for some products
                        if product.category in ['electronics', 'home'] and sale_date.weekday() >= 5:
                            if random.random() < 0.7:  # 70% chance of no sales on weekends
                                continue

                        # Random quantity with daily variation
                        daily_avg = random.randint(min_sales // 25, max_sales // 20)

                        # Add some seasonality
                        seasonality = 1.0 + 0.3 * math.sin(month_offset * 0.5)

                        # Add trend
                        trend = 1.0 + (months - month_offset) * 0.02

                        quantity = int(daily_avg * seasonality * trend * random.uniform(0.5, 1.5))
                        quantity = max(0, min(quantity, 20))  # Clamp between 0 and 20

                        if quantity > 0:
                            SalesRecord.objects.create(
                                product=product,
                                quantity_sold=quantity,
                                sale_date=sale_date
                            )
                            monthly_total += quantity

                self.stdout.write(
                    self.style.SUCCESS(f"  Generated sales data for {product.name}")
                )

        self.stdout.write(self.style.SUCCESS("\nData seeding completed successfully!"))
        self.stdout.write(f"Total products: {Product.objects.count()}")
        self.stdout.write(f"Total sales records: {SalesRecord.objects.count()}")
