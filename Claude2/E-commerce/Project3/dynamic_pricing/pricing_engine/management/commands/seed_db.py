from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import random
from pricing_engine.models import Product, SalesHistory, CompetitorPrice, PriceHistory


class Command(BaseCommand):
    help = 'Seeds the database with sample products, sales history, and competitor prices'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        # Clear existing data
        self.stdout.write('Clearing existing data...')
        SalesHistory.objects.all().delete()
        CompetitorPrice.objects.all().delete()
        PriceHistory.objects.all().delete()
        Product.objects.all().delete()

        # Sample product data
        products_data = [
            {
                'name': 'Wireless Bluetooth Headphones',
                'category': 'Electronics',
                'base_cost': Decimal('45.00'),
                'current_price': Decimal('79.99'),
                'stock_quantity': 150,
                'description': 'Premium wireless headphones with noise cancellation and 30-hour battery life.'
            },
            {
                'name': 'Smart Watch Series X',
                'category': 'Electronics',
                'base_cost': Decimal('120.00'),
                'current_price': Decimal('249.99'),
                'stock_quantity': 75,
                'description': 'Advanced smartwatch with health monitoring, GPS, and 5-day battery life.'
            },
            {
                'name': 'Organic Green Tea (100 bags)',
                'category': 'Food & Beverages',
                'base_cost': Decimal('8.50'),
                'current_price': Decimal('14.99'),
                'stock_quantity': 200,
                'description': 'Premium organic green tea sourced from Japan.'
            },
            {
                'name': 'Yoga Mat Premium',
                'category': 'Sports & Fitness',
                'base_cost': Decimal('18.00'),
                'current_price': Decimal('35.99'),
                'stock_quantity': 8,
                'description': 'Extra thick yoga mat with non-slip surface and carrying strap.'
            },
            {
                'name': 'Mechanical Keyboard RGB',
                'category': 'Electronics',
                'base_cost': Decimal('65.00'),
                'current_price': Decimal('129.99'),
                'stock_quantity': 45,
                'description': 'Gaming mechanical keyboard with RGB backlighting and programmable keys.'
            },
            {
                'name': 'Stainless Steel Water Bottle',
                'category': 'Sports & Fitness',
                'base_cost': Decimal('12.00'),
                'current_price': Decimal('24.99'),
                'stock_quantity': 300,
                'description': 'Insulated water bottle that keeps drinks cold for 24 hours.'
            },
            {
                'name': 'Wireless Mouse Ergonomic',
                'category': 'Electronics',
                'base_cost': Decimal('15.00'),
                'current_price': Decimal('39.99'),
                'stock_quantity': 120,
                'description': 'Ergonomic wireless mouse with precision tracking and customizable buttons.'
            },
            {
                'name': 'Coffee Maker Deluxe',
                'category': 'Home & Kitchen',
                'base_cost': Decimal('55.00'),
                'current_price': Decimal('99.99'),
                'stock_quantity': 5,
                'description': 'Programmable coffee maker with built-in grinder and thermal carafe.'
            },
            {
                'name': 'Running Shoes Pro',
                'category': 'Sports & Fitness',
                'base_cost': Decimal('45.00'),
                'current_price': Decimal('89.99'),
                'stock_quantity': 90,
                'description': 'Lightweight running shoes with advanced cushioning technology.'
            },
            {
                'name': 'LED Desk Lamp',
                'category': 'Home & Kitchen',
                'base_cost': Decimal('22.00'),
                'current_price': Decimal('44.99'),
                'stock_quantity': 180,
                'description': 'Adjustable LED desk lamp with multiple brightness levels and USB charging port.'
            },
            {
                'name': 'Portable Power Bank 20000mAh',
                'category': 'Electronics',
                'base_cost': Decimal('25.00'),
                'current_price': Decimal('49.99'),
                'stock_quantity': 250,
                'description': 'High-capacity power bank with fast charging and dual USB ports.'
            },
            {
                'name': 'Backpack Waterproof',
                'category': 'Travel',
                'base_cost': Decimal('30.00'),
                'current_price': Decimal('59.99'),
                'stock_quantity': 85,
                'description': 'Durable waterproof backpack with laptop compartment and anti-theft design.'
            },
            {
                'name': 'Bluetooth Speaker Portable',
                'category': 'Electronics',
                'base_cost': Decimal('28.00'),
                'current_price': Decimal('54.99'),
                'stock_quantity': 140,
                'description': 'Portable Bluetooth speaker with 360-degree sound and 12-hour battery.'
            },
            {
                'name': 'Skincare Set Premium',
                'category': 'Beauty',
                'base_cost': Decimal('35.00'),
                'current_price': Decimal('69.99'),
                'stock_quantity': 65,
                'description': 'Complete skincare set with cleanser, toner, serum, and moisturizer.'
            },
            {
                'name': 'Cookware Set Non-Stick',
                'category': 'Home & Kitchen',
                'base_cost': Decimal('75.00'),
                'current_price': Decimal('149.99'),
                'stock_quantity': 40,
                'description': '12-piece non-stick cookware set with ergonomic handles and heat-resistant grips.'
            }
        ]

        # Create products
        products = []
        for product_data in products_data:
            product = Product.objects.create(**product_data)
            products.append(product)
            self.stdout.write(f'Created product: {product.name}')

        # Generate sales history for each product
        self.stdout.write('Generating sales history...')
        for product in products:
            # Generate random sales over the last 90 days
            base_demand = random.randint(5, 20)  # Base daily sales

            for days_ago in range(90, 0, -1):
                sale_date = timezone.now() - timedelta(days=days_ago)

                # Randomize quantity sold (some days more, some less)
                daily_variance = random.uniform(0.5, 1.5)
                quantity = int(base_demand * daily_variance)

                # Ensure we don't sell more than we had in stock (simplified)
                if quantity > 0:
                    # Price might have varied slightly historically
                    price_variance = random.uniform(0.95, 1.05)
                    sale_price = Decimal(str(float(product.current_price) * price_variance)).quantize(Decimal('0.01'))

                    SalesHistory.objects.create(
                        product=product,
                        quantity_sold=quantity,
                        sale_price=sale_price,
                        date=sale_date
                    )

        self.stdout.write(self.style.SUCCESS('Sales history generated successfully'))

        # Generate competitor prices
        self.stdout.write('Generating competitor prices...')
        competitors = ['Amazon', 'Walmart', 'BestBuy', 'Target', 'Newegg']

        for product in products:
            # Generate 5-10 competitor price entries per product
            num_entries = random.randint(5, 10)

            for _ in range(num_entries):
                days_ago = random.randint(1, 30)
                recorded_at = timezone.now() - timedelta(days=days_ago)

                # Competitor price within +/- 20% of our price
                price_variance = random.uniform(0.80, 1.20)
                competitor_price = Decimal(str(float(product.current_price) * price_variance)).quantize(Decimal('0.01'))

                CompetitorPrice.objects.create(
                    product=product,
                    competitor_name=random.choice(competitors),
                    price=competitor_price,
                    recorded_at=recorded_at
                )

        self.stdout.write(self.style.SUCCESS('Competitor prices generated successfully'))

        # Generate some price history
        self.stdout.write('Generating price history...')
        for product in products:
            # Generate 2-5 price changes per product
            num_changes = random.randint(2, 5)

            for i in range(num_changes):
                days_ago = random.randint(i * 10, (i + 1) * 10)
                timestamp = timezone.now() - timedelta(days=days_ago)

                # Create a price change (either increase or decrease)
                change_direction = random.choice([-1, 1])
                change_percent = random.uniform(0.05, 0.15)  # 5-15% change

                new_price = Decimal(str(float(product.current_price) * (1 + change_direction * change_percent))).quantize(Decimal('0.01'))

                # Ensure price doesn't go below cost
                if new_price < product.base_cost * Decimal('1.1'):
                    new_price = product.base_cost * Decimal('1.1')

                # Calculate old price for this change
                if change_direction == 1:
                    old_price = Decimal(str(float(new_price) / (1 + change_percent))).quantize(Decimal('0.01'))
                else:
                    old_price = Decimal(str(float(new_price) / (1 - change_percent))).quantize(Decimal('0.01'))

                reason = random.choice([
                    'Market demand adjustment',
                    'Competitor price match',
                    'Inventory optimization',
                    'Seasonal pricing',
                    'Promotional pricing'
                ])

                PriceHistory.objects.create(
                    product=product,
                    old_price=old_price,
                    new_price=new_price,
                    reason=reason,
                    timestamp=timestamp
                )

        self.stdout.write(self.style.SUCCESS('Price history generated successfully'))

        self.stdout.write(self.style.SUCCESS(f'\nDatabase seeding complete!'))
        self.stdout.write(self.style.SUCCESS(f'Created {len(products)} products'))
        self.stdout.write(self.style.SUCCESS(f'Generated {SalesHistory.objects.count()} sales records'))
        self.stdout.write(self.style.SUCCESS(f'Generated {CompetitorPrice.objects.count()} competitor price entries'))
        self.stdout.write(self.style.SUCCESS(f'Generated {PriceHistory.objects.count()} price change records'))
