from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from vendor.models import (
    Vendor, Category, Product, Order, OrderItem, Commission,
    Payout, Cart, CartItem, Review, Wishlist
)


class Command(BaseCommand):
    help = 'Load demo data for Multi-Vendor Marketplace'

    def handle(self, *args, **options):
        self.stdout.write('Loading demo data...')
        
        # Clear existing data
        Review.objects.all().delete()
        Wishlist.objects.all().delete()
        Payout.objects.all().delete()
        Commission.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        CartItem.objects.all().delete()
        Cart.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Vendor.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        
        # Create Users
        self.stdout.write('Creating users...')
        users = self.create_users()
        
        # Create Vendors
        self.stdout.write('Creating vendors...')
        vendors = self.create_vendors(users)
        
        # Create Categories
        self.stdout.write('Creating categories...')
        categories = self.create_categories()
        
        # Create Products
        self.stdout.write('Creating products...')
        products = self.create_products(vendors, categories)
        
        # Create Orders
        self.stdout.write('Creating orders...')
        orders = self.create_orders(users, products, vendors)
        
        # Create Reviews
        self.stdout.write('Creating reviews...')
        self.create_reviews(users, products)
        
        # Create Payouts
        self.stdout.write('Creating payouts...')
        self.create_payouts(vendors)
        
        self.stdout.write(self.style.SUCCESS('Demo data loaded successfully!'))
        self.stdout.write('\nLogin Credentials:')
        for i, user in enumerate(users[:4]):
            self.stdout.write(f'  {i+1}. Username: {user.username} | Password: demo123')
    
    def create_users(self):
        users = []
        
        # Customers
        customer_data = [
            ('john_doe', 'john@example.com', 'John', 'Doe'),
            ('jane_smith', 'jane@example.com', 'Jane', 'Smith'),
            ('mike_jones', 'mike@example.com', 'Mike', 'Jones'),
            ('sarah_williams', 'sarah@example.com', 'Sarah', 'Williams'),
            ('david_brown', 'david@example.com', 'David', 'Brown'),
            ('emily_davis', 'emily@example.com', 'Emily', 'Davis'),
            ('robert_miller', 'robert@example.com', 'Robert', 'Miller'),
            ('lisa_wilson', 'lisa@example.com', 'Lisa', 'Wilson'),
            ('kevin_moore', 'kevin@example.com', 'Kevin', 'Moore'),
            ('anna_taylor', 'anna@example.com', 'Anna', 'Taylor'),
        ]
        
        for username, email, first_name, last_name in customer_data:
            user = User.objects.create_user(
                username=username,
                email=email,
                password='demo123',
                first_name=first_name,
                last_name=last_name
            )
            users.append(user)
        
        return users
    
    def create_vendors(self, users):
        vendors = []
        
        vendor_data = [
            {
                'user': users[0],
                'store_name': 'TechWorld Electronics',
                'store_slug': 'techworld',
                'description': 'Premium electronics and gadgets at competitive prices.',
                'bank_name': 'Chase Bank',
                'commission_rate': Decimal('10.00'),
            },
            {
                'user': users[1],
                'store_name': 'Fashion Haven',
                'store_slug': 'fashion-haven',
                'description': 'Trendy fashion and accessories for everyone.',
                'bank_name': 'Bank of America',
                'commission_rate': Decimal('12.00'),
            },
            {
                'user': users[2],
                'store_name': 'Home Decor Plus',
                'store_slug': 'home-decor-plus',
                'description': 'Beautiful home decor and furniture.',
                'bank_name': 'Wells Fargo',
                'commission_rate': Decimal('8.00'),
            },
            {
                'user': users[3],
                'store_name': 'Sports Gear Hub',
                'store_slug': 'sports-gear',
                'description': 'Premium sports equipment and activewear.',
                'bank_name': 'TD Bank',
                'commission_rate': Decimal('10.00'),
            },
        ]
        
        for i, data in enumerate(vendor_data):
            vendor = Vendor.objects.create(
                user=data['user'],
                store_name=data['store_name'],
                store_slug=data['store_slug'],
                description=data['description'],
                contact_email=data['user'].email,
                contact_phone=f'+1-555-010{i + 1}',
                address=f'{i + 1} Business Ave\nNew York, NY 10001\nUSA',
                bank_name=data['bank_name'],
                bank_account_number=f'****{i + 1234}',
                bank_routing_number='021000021',
                paypal_email=data['user'].email,
                commission_rate=data['commission_rate'],
                is_approved=True,
                is_active=True,
                total_sales=Decimal(f'{(i + 1) * 10000}.00'),
                total_earnings=Decimal(f'{(i + 1) * 9000}.00'),
                pending_balance=Decimal(f'{(i + 1) * 1000}.00'),
            )
            vendors.append(vendor)
        
        return vendors
    
    def create_categories(self):
        categories = []
        
        category_data = [
            {'name': 'Electronics', 'slug': 'electronics', 'description': 'Computers, phones, and electronic devices.'},
            {'name': 'Clothing', 'slug': 'clothing', 'description': 'Fashion and apparel for all ages.'},
            {'name': 'Home & Garden', 'slug': 'home-garden', 'description': 'Furniture, decor, and home essentials.'},
            {'name': 'Sports & Outdoors', 'slug': 'sports-outdoors', 'description': 'Athletic gear and outdoor equipment.'},
            {'name': 'Books & Media', 'slug': 'books-media', 'description': 'Books, movies, and music.'},
            {'name': 'Toys & Games', 'slug': 'toys-games', 'description': 'Toys, games, and hobbies.'},
            {'name': 'Health & Beauty', 'slug': 'health-beauty', 'description': 'Personal care and beauty products.'},
            {'name': 'Automotive', 'slug': 'automotive', 'description': 'Car parts and accessories.'},
        ]
        
        for data in category_data:
            category = Category.objects.create(**data)
            categories.append(category)
        
        return categories
    
    def create_products(self, vendors, categories):
        products = []
        
        product_data = [
            # Electronics
            {
                'vendor': vendors[0],
                'category': categories[0],
                'name': 'Wireless Bluetooth Headphones',
                'slug': 'wireless-bluetooth-headphones',
                'description': 'Premium sound quality with 30-hour battery life. Features active noise cancellation and comfortable ear cups.',
                'price': Decimal('149.99'),
                'sale_price': Decimal('119.99'),
                'stock_quantity': 150,
                'sku': 'TECH-001',
                'status': 'ACTIVE',
                'rating': Decimal('4.5'),
                'review_count': 128,
                'view_count': 1543,
            },
            {
                'vendor': vendors[0],
                'category': categories[0],
                'name': 'Smart Watch Series 5',
                'slug': 'smart-watch-series-5',
                'description': 'Track fitness, receive notifications, and stay connected with this feature-packed smartwatch.',
                'price': Decimal('299.99'),
                'stock_quantity': 75,
                'sku': 'TECH-002',
                'status': 'ACTIVE',
                'rating': Decimal('4.7'),
                'review_count': 256,
                'view_count': 3201,
            },
            {
                'vendor': vendors[0],
                'category': categories[0],
                'name': '4K Ultra HD Smart TV 55 inch',
                'slug': '4k-uhd-smart-tv-55',
                'description': 'Stunning 4K resolution with HDR support. Smart TV with streaming apps built-in.',
                'price': Decimal('699.99'),
                'sale_price': Decimal('599.99'),
                'stock_quantity': 30,
                'sku': 'TECH-003',
                'status': 'ACTIVE',
                'rating': Decimal('4.8'),
                'review_count': 89,
                'view_count': 2456,
            },
            # Clothing
            {
                'vendor': vendors[1],
                'category': categories[1],
                'name': 'Classic Denim Jeans',
                'slug': 'classic-denim-jeans',
                'description': 'Premium quality denim jeans with comfortable stretch. Available in multiple washes and sizes.',
                'price': Decimal('89.99'),
                'stock_quantity': 200,
                'sku': 'FASH-001',
                'status': 'ACTIVE',
                'rating': Decimal('4.3'),
                'review_count': 342,
                'view_count': 4521,
            },
            {
                'vendor': vendors[1],
                'category': categories[1],
                'name': 'Summer Floral Dress',
                'slug': 'summer-floral-dress',
                'description': 'Beautiful floral pattern dress perfect for summer occasions. Lightweight and breathable fabric.',
                'price': Decimal('69.99'),
                'sale_price': Decimal('49.99'),
                'stock_quantity': 120,
                'sku': 'FASH-002',
                'status': 'ACTIVE',
                'rating': Decimal('4.6'),
                'review_count': 198,
                'view_count': 2876,
            },
            # Home & Garden
            {
                'vendor': vendors[2],
                'category': categories[2],
                'name': 'Modern Floor Lamp',
                'slug': 'modern-floor-lamp',
                'description': 'Elegant floor lamp with adjustable brightness. Perfect for living room or bedroom.',
                'price': Decimal('129.99'),
                'stock_quantity': 85,
                'sku': 'HOME-001',
                'status': 'ACTIVE',
                'rating': Decimal('4.4'),
                'review_count': 156,
                'view_count': 1987,
            },
            {
                'vendor': vendors[2],
                'category': categories[2],
                'name': 'Velvet Sofa Set',
                'slug': 'velvet-sofa-set',
                'description': 'Luxurious 3-piece velvet sofa set. Comfortable and stylish addition to any living room.',
                'price': Decimal('1299.99'),
                'sale_price': Decimal('1099.99'),
                'stock_quantity': 15,
                'sku': 'HOME-002',
                'status': 'ACTIVE',
                'rating': Decimal('4.9'),
                'review_count': 67,
                'view_count': 1876,
            },
            # Sports
            {
                'vendor': vendors[3],
                'category': categories[3],
                'name': 'Professional Running Shoes',
                'slug': 'pro-running-shoes',
                'description': 'High-performance running shoes with advanced cushioning technology.',
                'price': Decimal('149.99'),
                'stock_quantity': 180,
                'sku': 'SPORT-001',
                'status': 'ACTIVE',
                'rating': Decimal('4.6'),
                'review_count': 523,
                'view_count': 6234,
            },
            {
                'vendor': vendors[3],
                'category': categories[3],
                'name': 'Yoga Mat Premium',
                'slug': 'yoga-mat-premium',
                'description': 'Extra thick, non-slip yoga mat for comfortable practice sessions.',
                'price': Decimal('49.99'),
                'stock_quantity': 250,
                'sku': 'SPORT-002',
                'status': 'ACTIVE',
                'rating': Decimal('4.7'),
                'review_count': 389,
                'view_count': 4123,
            },
            # More Electronics
            {
                'vendor': vendors[0],
                'category': categories[0],
                'name': 'Laptop Computer 15.6 inch',
                'slug': 'laptop-computer-15-6',
                'description': 'Powerful laptop for work and entertainment. 16GB RAM, 512GB SSD.',
                'price': Decimal('999.99'),
                'stock_quantity': 45,
                'sku': 'TECH-004',
                'status': 'ACTIVE',
                'rating': Decimal('4.4'),
                'review_count': 234,
                'view_count': 3521,
            },
            {
                'vendor': vendors[0],
                'category': categories[0],
                'name': 'Wireless Gaming Mouse',
                'slug': 'wireless-gaming-mouse',
                'description': 'High-precision gaming mouse with RGB lighting and 7 programmable buttons.',
                'price': Decimal('79.99'),
                'stock_quantity': 200,
                'sku': 'TECH-005',
                'status': 'ACTIVE',
                'rating': Decimal('4.5'),
                'review_count': 412,
                'view_count': 5187,
            },
            # More Clothing
            {
                'vendor': vendors[1],
                'category': categories[1],
                'name': 'Casual Polo Shirt',
                'slug': 'casual-polo-shirt',
                'description': 'Classic polo shirt in various colors. Soft cotton blend for all-day comfort.',
                'price': Decimal('49.99'),
                'stock_quantity': 300,
                'sku': 'FASH-003',
                'status': 'ACTIVE',
                'rating': Decimal('4.2'),
                'review_count': 278,
                'view_count': 3892,
            },
        ]
        
        for data in product_data:
            product = Product.objects.create(**data)
            products.append(product)
        
        return products
    
    def create_orders(self, users, products, vendors):
        orders = []
        
        order_data = [
            {
                'customer': users[4],
                'items': [
                    {'product': products[0], 'quantity': 1},
                    {'product': products[1], 'quantity': 1},
                ],
                'status': 'DELIVERED',
                'order_type': 'ONLINE',
            },
            {
                'customer': users[5],
                'items': [
                    {'product': products[2], 'quantity': 1},
                ],
                'status': 'DELIVERED',
                'order_type': 'ONLINE',
            },
            {
                'customer': users[6],
                'items': [
                    {'product': products[3], 'quantity': 2},
                    {'product': products[4], 'quantity': 1},
                ],
                'status': 'PROCESSING',
                'order_type': 'ONLINE',
            },
            {
                'customer': users[7],
                'items': [
                    {'product': products[5], 'quantity': 1},
                    {'product': products[6], 'quantity': 1},
                ],
                'status': 'CONFIRMED',
                'order_type': 'COD',
            },
            {
                'customer': users[8],
                'items': [
                    {'product': products[7], 'quantity': 2},
                ],
                'status': 'SHIPPED',
                'order_type': 'ONLINE',
            },
            {
                'customer': users[9],
                'items': [
                    {'product': products[0], 'quantity': 1},
                    {'product': products[8], 'quantity': 1},
                    {'product': products[9], 'quantity': 2},
                ],
                'status': 'PENDING',
                'order_type': 'ONLINE',
            },
        ]
        
        for i, data in enumerate(order_data):
            # Calculate totals
            subtotal = Decimal('0.00')
            for item_data in data['items']:
                subtotal += item_data['product'].current_price * item_data['quantity']
            
            shipping_cost = Decimal('10.00') if subtotal < 100 else Decimal('0')
            tax = subtotal * Decimal('0.08')
            total = subtotal + shipping_cost + tax
            
            # Create order
            order = Order.objects.create(
                customer=data['customer'],
                status=data['status'],
                order_type=data['order_type'],
                shipping_address=f'{i + 100} Main Street\nNew York, NY 10001',
                billing_address=f'{i + 100} Main Street\nNew York, NY 10001',
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                tax=tax,
                total=total,
                created_at=timezone.now() - timedelta(days=i),
            )
            orders.append(order)
            
            # Create order items
            for item_data in data['items']:
                OrderItem.objects.create(
                    order=order,
                    product=item_data['product'],
                    vendor=item_data['product'].vendor,
                    quantity=item_data['quantity'],
                    price=item_data['product'].current_price,
                    subtotal=item_data['product'].current_price * item_data['quantity'],
                    status=data['status'],
                )
                
                # Create commission
                Commission.objects.create(
                    order=order,
                    vendor=item_data['product'].vendor,
                    order_item=OrderItem.objects.filter(order=order).last(),
                    amount=item_data['product'].current_price * item_data['quantity'] * (item_data['product'].vendor.commission_rate / 100),
                    rate=item_data['product'].vendor.commission_rate,
                    status='COMPLETED' if data['status'] == 'DELIVERED' else 'PENDING',
                    completed_at=timezone.now() if data['status'] == 'DELIVERED' else None,
                )
        
        return orders
    
    def create_reviews(self, users, products):
        review_texts = [
            "Great product! Exactly as described.",
            "Excellent quality and fast shipping.",
            "Highly recommend this seller.",
            "Good value for money.",
            "Product exceeded my expectations.",
            "Very satisfied with my purchase.",
            "Will definitely buy from this vendor again.",
            "Top-notch quality!",
            "Arrived quickly and in perfect condition.",
            "Five stars all the way!",
        ]
        
        for product in products[:8]:
            for i in range(5):
                Review.objects.create(
                    product=product,
                    user=users[i % len(users)],
                    title=f"Great Product #{i + 1}",
                    content=review_texts[i % len(review_texts)],
                    rating=4 + (i % 2),
                    is_approved=True,
                    created_at=timezone.now() - timedelta(days=i),
                )
    
    def create_payouts(self, vendors):
        for i, vendor in enumerate(vendors):
            payout_amount = vendor.pending_balance / 2
            
            Payout.objects.create(
                vendor=vendor,
                amount=payout_amount,
                method='bank_transfer',
                transaction_id=f'TXN-{timezone.now().strftime("%Y%m%d")}-{i + 1000}',
                status='COMPLETED',
                notes='Monthly payout for completed orders',
                requested_at=timezone.now() - timedelta(days=30),
                processed_at=timezone.now() - timedelta(days=25),
            )
