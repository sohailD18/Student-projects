"""
Management command to load demo data for the AI E-Commerce shop.

Creates:
- Demo categories
- Demo products with descriptions
- Demo users (if they don't exist)
- Sample user interactions (views, purchases, cart, wishlist)

Usage:
    python manage.py load_demo_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from shop.models import Category, Product, UserInteraction
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Loads demo data for the AI E-Commerce shop'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Loading demo data...'))

        # Create demo users
        self.create_users()

        # Create categories and products
        self.create_categories_and_products()

        # Create user interactions
        self.create_interactions()

        self.stdout.write(self.style.SUCCESS('Demo data loaded successfully!'))
        self.stdout.write(self.style.WARNING('\nDemo Users:'))
        self.stdout.write('  Username: demo1, Password: demo123')
        self.stdout.write('  Username: demo2, Password: demo123')
        self.stdout.write('  Username: demo3, Password: demo123')

    def create_users(self):
        """Create demo users"""
        users_data = [
            ('demo1', 'Demo User One'),
            ('demo2', 'Demo User Two'),
            ('demo3', 'Demo User Three'),
        ]

        for username, full_name in users_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'first_name': full_name.split()[0],
                    'last_name': full_name.split()[1] if len(full_name.split()) > 1 else '',
                    'is_active': True,
                }
            )
            if created:
                user.set_password('demo123')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))
            else:
                self.stdout.write(self.style.WARNING(f'User already exists: {username}'))

        return User.objects.filter(username__in=[u[0] for u in users_data])

    def create_categories_and_products(self):
        """Create categories and products"""
        # Categories and their products
        categories_data = {
            'Electronics': [
                {
                    'name': 'Wireless Bluetooth Headphones',
                    'price': 79.99,
                    'description': 'Premium noise-cancelling wireless headphones with 30-hour battery life, superior sound quality, and comfortable over-ear design. Perfect for music lovers and professionals.'
                },
                {
                    'name': 'Smartphone 128GB',
                    'price': 699.99,
                    'description': 'Latest flagship smartphone with stunning 6.5-inch display, powerful processor, triple camera system, and all-day battery life. Capture every moment in brilliance.'
                },
                {
                    'name': 'Laptop 15.6" Intel i7',
                    'price': 1299.99,
                    'description': 'High-performance laptop for work and gaming. Features Intel i7 processor, 16GB RAM, 512GB SSD, and dedicated graphics. Sleek aluminum design.'
                },
                {
                    'name': '4K Ultra HD Smart TV 55"',
                    'price': 599.99,
                    'description': 'Stunning 4K resolution with HDR support, smart TV capabilities, voice control, and immersive sound. Transform your living room into a home theater.'
                },
                {
                    'name': 'Wireless Gaming Mouse',
                    'price': 49.99,
                    'description': 'Precision gaming mouse with customizable RGB lighting, 16000 DPI sensor, programmable buttons, and ergonomic design for competitive gaming.'
                },
            ],
            'Clothing': [
                {
                    'name': 'Classic Cotton T-Shirt',
                    'price': 24.99,
                    'description': 'Comfortable 100% cotton t-shirt in multiple colors. Perfect for everyday wear with a classic fit that never goes out of style.'
                },
                {
                    'name': 'Slim Fit Jeans',
                    'price': 59.99,
                    'description': 'Modern slim-fit jeans made from premium denim. Features stretch fabric for comfort and classic five-pocket styling. Available in various washes.'
                },
                {
                    'name': 'Winter Wool Coat',
                    'price': 149.99,
                    'description': 'Elegant wool blend coat for cold weather. Features a tailored fit, notched lapels, and premium lining. Stay warm in style this winter.'
                },
                {
                    'name': 'Running Sneakers',
                    'price': 89.99,
                    'description': 'Lightweight running shoes with responsive cushioning, breathable mesh upper, and durable outsole. Perfect for daily runs and athletic activities.'
                },
                {
                    'name': 'Casual Hoodie',
                    'price': 44.99,
                    'description': 'Soft fleece hoodie with kangaroo pocket and adjustable hood. Perfect for lounging or casual outings. Available in classic colors.'
                },
            ],
            'Home & Garden': [
                {
                    'name': 'Stainless Steel Cookware Set',
                    'price': 199.99,
                    'description': 'Professional 12-piece cookware set with stainless steel construction, stay-cool handles, and tempered glass lids. Essential for every kitchen.'
                },
                {
                    'name': 'Memory Foam Pillow Set',
                    'price': 59.99,
                    'description': 'Set of two premium memory foam pillows with cooling gel layer. Provides optimal neck support and pressure relief for restful sleep.'
                },
                {
                    'name': 'Indoor Plant Collection',
                    'price': 39.99,
                    'description': 'Set of three easy-care indoor plants with decorative pots. Purifies air and adds natural beauty to any room. Perfect for beginners.'
                },
                {
                    'name': 'LED Desk Lamp',
                    'price': 34.99,
                    'description': 'Modern LED desk lamp with adjustable brightness and color temperature. Features USB charging port and flexible gooseneck design.'
                },
                {
                    'name': 'Vacuum Cleaner',
                    'price': 179.99,
                    'description': 'Powerful cordless vacuum cleaner with lightweight design, long battery life, and versatile attachments for whole-home cleaning.'
                },
            ],
            'Sports & Outdoors': [
                {
                    'name': 'Yoga Mat Premium',
                    'price': 39.99,
                    'description': 'Extra-thick non-slip yoga mat with carrying strap. Provides superior cushioning and stability for yoga, pilates, and floor exercises.'
                },
                {
                    'name': 'Dumbbell Set 20kg',
                    'price': 79.99,
                    'description': 'Adjustable dumbbell set with weight plates and compact storage rack. Perfect for home strength training and fitness routines.'
                },
                {
                    'name': 'Camping Tent 4-Person',
                    'price': 149.99,
                    'description': 'Spacious waterproof camping tent with easy setup, integrated ground sheet, and excellent ventilation. Great for family camping trips.'
                },
                {
                    'name': 'Mountain Bike',
                    'price': 449.99,
                    'description': 'Trail-ready mountain bike with suspension fork, 21-speed gears, and durable frame. Perfect for off-road adventures and city commuting.'
                },
                {
                    'name': 'Fitness Tracker Watch',
                    'price': 99.99,
                    'description': 'Advanced fitness tracker with heart rate monitoring, GPS, sleep tracking, and smartphone notifications. Your complete health companion.'
                },
            ],
            'Books & Media': [
                {
                    'name': 'Bestselling Fiction Novel',
                    'price': 14.99,
                    'description': 'Captivating thriller that will keep you on the edge of your seat. New York Times bestseller with millions of copies sold worldwide.'
                },
                {
                    'name': 'Self-Help Guide',
                    'price': 19.99,
                    'description': 'Transformative self-help book with practical strategies for personal growth and success. Based on proven psychological research.'
                },
                {
                    'name': 'Cooking Recipes Hardcover',
                    'price': 29.99,
                    'description': 'Beautiful cookbook with 200+ easy-to-follow recipes from around the world. Stunning photography and chef-tested dishes.'
                },
                {
                    'name': 'Blu-ray Movie Collection',
                    'price': 24.99,
                    'description': 'Award-winning drama film on Blu-ray with bonus features and director commentary. A must-have for any movie collection.'
                },
                {
                    'name': 'Educational Documentary Series',
                    'price': 34.99,
                    'description': 'Complete documentary series exploring nature and science. Stunning visuals and expert narration. Perfect for learning and entertainment.'
                },
            ],
        }

        for category_name, products_data in categories_data.items():
            # Create or get category
            category, created = Category.objects.get_or_create(name=category_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category_name}'))

            # Create products
            for product_data in products_data:
                product, created = Product.objects.get_or_create(
                    name=product_data['name'],
                    defaults={
                        'category': category,
                        'price': product_data['price'],
                        'description': product_data['description'],
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'  Created product: {product.name}'))

    def create_interactions(self):
        """Create sample user interactions"""
        users = User.objects.filter(username__startswith='demo')
        products = Product.objects.all()

        if not users.exists() or not products.exists():
            self.stdout.write(self.style.WARNING('No users or products found, skipping interactions'))
            return

        # Clear existing interactions for demo users
        UserInteraction.objects.filter(user__in=users).delete()

        interaction_types = ['view', 'cart', 'wishlist', 'purchase']
        now = timezone.now()

        interaction_count = 0
        for user in users:
            # Each user interacts with random products
            num_products = random.randint(10, 20)
            user_products = random.sample(list(products), min(num_products, len(products)))

            for product in user_products:
                # Create 1-3 interactions per product
                num_interactions = random.randint(1, 3)
                days_ago = random.randint(0, 30)

                for _ in range(num_interactions):
                    interaction_type = random.choice(interaction_types)

                    # More likely to view than purchase
                    if interaction_type == 'purchase' and random.random() > 0.3:
                        interaction_type = 'view'

                    timestamp = now - timedelta(
                        days=days_ago,
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59)
                    )

                    UserInteraction.objects.create(
                        user=user,
                        product=product,
                        interaction_type=interaction_type,
                        timestamp=timestamp
                    )
                    interaction_count += 1

        self.stdout.write(self.style.SUCCESS(f'Created {interaction_count} user interactions'))
