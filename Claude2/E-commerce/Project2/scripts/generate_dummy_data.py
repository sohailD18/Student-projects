"""
Dummy Data Generator for Inventory Management System

This script generates:
1. Sample products across different categories
2. 6 months of historical sales data for each product
3. Realistic sales patterns with trends and seasonality

Usage:
    python manage.py shell < generate_dummy_data.py
    OR
    python scripts/generate_dummy_data.py
"""

import os
import sys
import random
from datetime import datetime, timedelta

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_project.settings')

import django
django.setup()

from inventory.models import Product, SalesData
from django.db.models import Min, Max, F


# Configuration
NUM_PRODUCTS = 20  # Number of products to create
DAYS_OF_HISTORY = 180  # 6 months of data


# Sample product data
PRODUCT_TEMPLATES = [
    # Electronics
    {'name': 'Wireless Mouse', 'category': 'electronics', 'price': 29.99, 'base_demand': 15},
    {'name': 'USB-C Cable', 'category': 'electronics', 'price': 12.99, 'base_demand': 25},
    {'name': 'Laptop Stand', 'category': 'electronics', 'price': 49.99, 'base_demand': 8},
    {'name': 'Bluetooth Headphones', 'category': 'electronics', 'price': 79.99, 'base_demand': 12},
    {'name': 'Webcam HD', 'category': 'electronics', 'price': 59.99, 'base_demand': 10},

    # Clothing
    {'name': 'Cotton T-Shirt', 'category': 'clothing', 'price': 19.99, 'base_demand': 30},
    {'name': 'Jeans Classic', 'category': 'clothing', 'price': 49.99, 'base_demand': 20},
    {'name': 'Winter Jacket', 'category': 'clothing', 'price': 89.99, 'base_demand': 5},
    {'name': 'Running Shoes', 'category': 'clothing', 'price': 79.99, 'base_demand': 15},
    {'name': 'Socks Pack', 'category': 'clothing', 'price': 14.99, 'base_demand': 40},

    # Food & Beverages
    {'name': 'Organic Coffee', 'category': 'food', 'price': 15.99, 'base_demand': 35},
    {'name': 'Green Tea', 'category': 'food', 'price': 9.99, 'base_demand': 25},
    {'name': 'Protein Bar', 'category': 'food', 'price': 24.99, 'base_demand': 50},
    {'name': 'Almonds Pack', 'category': 'food', 'price': 12.99, 'base_demand': 30},
    {'name': 'Olive Oil', 'category': 'food', 'price': 19.99, 'base_demand': 20},

    # Home & Garden
    {'name': 'LED Desk Lamp', 'category': 'home', 'price': 34.99, 'base_demand': 18},
    {'name': 'Plant Pot Set', 'category': 'home', 'price': 24.99, 'base_demand': 12},
    {'name': 'Kitchen Towel Set', 'category': 'home', 'price': 16.99, 'base_demand': 22},
    {'name': 'Storage Box', 'category': 'home', 'price': 19.99, 'base_demand': 15},
    {'name': 'Wall Clock', 'category': 'home', 'price': 29.99, 'base_demand': 8},
]


def generate_sales_quantity(base_demand, day_of_week, day_of_month, month):
    """
    Generate realistic sales quantities with patterns.

    Patterns:
    - Weekend spike (Saturday, Sunday)
    - Mid-month spike (payday effect)
    - Seasonal variations
    - Random fluctuations
    """
    # Base quantity
    quantity = base_demand

    # Weekend boost
    if day_of_week in [5, 6]:  # Saturday, Sunday
        quantity *= 1.3

    # Payday boost (15th and end of month)
    if day_of_month in [1, 15, 25, 30, 31]:
        quantity *= 1.2

    # Seasonal variations
    seasonal_factors = {
        1: 0.9,   # January - post-holiday slowdown
        2: 0.85,  # February
        3: 0.95,  # March
        4: 1.0,   # April
        5: 1.05,  # May
        6: 1.1,   # June
        7: 1.15,  # July
        8: 1.1,   # August
        9: 1.05,  # September
        10: 1.1,  # October
        11: 1.3,  # November - Black Friday
        12: 1.5,  # December - Holiday season
    }
    quantity *= seasonal_factors.get(month, 1.0)

    # Random fluctuation (-30% to +30%)
    fluctuation = random.uniform(0.7, 1.3)
    quantity *= fluctuation

    # Some days have zero sales
    if random.random() < 0.05:  # 5% chance of zero sales
        return 0

    return int(max(0, round(quantity)))


def create_products():
    """Create sample products"""
    print("Creating products...")

    # Clear existing products and sales data
    Product.objects.all().delete()

    products = []
    for i, template in enumerate(PRODUCT_TEMPLATES[:NUM_PRODUCTS], 1):
        # Generate stock level (some low, some good, some high)
        stock_level = random.choice([
            random.randint(0, 5),      # Low stock
            random.randint(20, 50),    # Good stock
            random.randint(100, 200),  # Over-stock
        ])

        # Safety stock based on demand
        safety_stock = max(5, int(template['base_demand'] * 0.5))

        product = Product.objects.create(
            name=template['name'],
            category=template['category'],
            current_stock=stock_level,
            price=template['price'],
            safety_stock=safety_stock
        )
        products.append(product)
        print(f"  Created: {product.name} ({product.category}) - Stock: {product.current_stock}")

    print(f"Created {len(products)} products\n")
    return products


def create_sales_data(products):
    """Create historical sales data"""
    print("Generating sales data...")

    # Calculate date range
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=DAYS_OF_HISTORY)

    total_sales_records = 0

    for product in products:
        # Find base demand from template
        base_demand = 15  # Default
        for template in PRODUCT_TEMPLATES:
            if template['name'] == product.name:
                base_demand = template['base_demand']
                break

        current_date = start_date
        sales_records = []

        while current_date <= end_date:
            # Generate sales quantity
            quantity = generate_sales_quantity(
                base_demand,
                current_date.weekday(),
                current_date.day,
                current_date.month
            )

            if quantity > 0:
                sales_records.append(SalesData(
                    product=product,
                    date=current_date,
                    quantity_sold=quantity
                ))

            current_date += timedelta(days=1)

        # Bulk create for efficiency
        SalesData.objects.bulk_create(sales_records)
        total_sales_records += len(sales_records)

        print(f"  Generated {len(sales_records)} sales records for {product.name}")

    print(f"Total sales records created: {total_sales_records}\n")


def generate_summary():
    """Generate summary statistics"""
    print("=" * 60)
    print("DATA GENERATION SUMMARY")
    print("=" * 60)

    # Product statistics
    total_products = Product.objects.count()
    print(f"\nTotal Products: {total_products}")

    by_category = {}
    for product in Product.objects.all():
        category = product.get_category_display()
        by_category[category] = by_category.get(category, 0) + 1

    print("\nProducts by Category:")
    for category, count in sorted(by_category.items()):
        print(f"  {category}: {count}")

    # Sales statistics
    total_sales = SalesData.objects.count()
    print(f"\nTotal Sales Records: {total_sales}")

    date_range = SalesData.objects.aggregate(
        earliest=Min('date'),
        latest=Max('date')
    )
    print(f"Date Range: {date_range['earliest']} to {date_range['latest']}")

    # Stock status
    print("\nStock Status:")
    low_stock = Product.objects.filter(current_stock__lte=F('safety_stock')).count()
    print(f"  Low Stock: {low_stock}")
    print(f"  Good Stock: {total_products - low_stock}")

    print("\n" + "=" * 60)
    print("Dummy data generation complete!")
    print("=" * 60)


def main():
    """Main execution function"""
    print("\n" + "=" * 60)
    print("DUMMY DATA GENERATOR")
    print("Inventory Management System")
    print("=" * 60 + "\n")

    # Set random seed for reproducibility
    random.seed(42)

    # Generate products
    products = create_products()

    # Generate sales data
    create_sales_data(products)

    # Generate summary
    generate_summary()

    print("\nYou can now access the dashboard at:")
    print("http://127.0.0.1:8000/")
    print("\nOr view products in Django Admin:")
    print("http://127.0.0.1:8000/admin/\n")


if __name__ == '__main__':
    main()
