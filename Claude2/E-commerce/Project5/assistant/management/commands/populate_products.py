from django.core.management.base import BaseCommand
from assistant.models import Product


class Command(BaseCommand):
    help = 'Populate the database with sample electronic products'

    def handle(self, *args, **kwargs):
        # Clear existing products
        Product.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing products'))

        # Sample products data
        products_data = [
            # Laptops
            {
                'name': 'MacBook Pro 16"',
                'description': 'Apple M3 Max chip, 36GB Memory, 1TB SSD. The most powerful MacBook ever for demanding workflows.',
                'price': 2499.00,
                'category': 'Laptop',
                'image_url': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400',
                'specs': {
                    'processor': 'Apple M3 Max',
                    'ram': '36GB',
                    'storage': '1TB SSD',
                    'display': '16.2" Liquid Retina XDR',
                    'battery': 'Up to 22 hours',
                    'weight': '2.1 kg'
                },
                'rating': 4.9
            },
            {
                'name': 'Dell XPS 15',
                'description': '13th Gen Intel Core i7, 32GB RAM, 1TB SSD. Stunning 4K+ OLED display with exceptional color accuracy.',
                'price': 1899.00,
                'category': 'Laptop',
                'image_url': 'https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=400',
                'specs': {
                    'processor': 'Intel Core i7-13700H',
                    'ram': '32GB DDR5',
                    'storage': '1TB NVMe SSD',
                    'display': '15.6" OLED 3.5K',
                    'battery': 'Up to 12 hours',
                    'weight': '1.86 kg'
                },
                'rating': 4.7
            },
            {
                'name': 'HP Spectre x360',
                'description': 'Intel Core i7, 16GB RAM, 512GB SSD. 2-in-1 convertible laptop with stunning gem-cut design.',
                'price': 1399.00,
                'category': 'Laptop',
                'image_url': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400',
                'specs': {
                    'processor': 'Intel Core i7-1355U',
                    'ram': '16GB DDR5',
                    'storage': '512GB SSD',
                    'display': '13.5" WUXGA+ Touch',
                    'battery': 'Up to 14 hours',
                    'weight': '1.36 kg'
                },
                'rating': 4.5
            },
            {
                'name': 'Lenovo ThinkPad X1 Carbon',
                'description': 'Intel Core i7, 32GB RAM, 1TB SSD. Business ultrabook with legendary ThinkPad durability.',
                'price': 1699.00,
                'category': 'Laptop',
                'image_url': 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=400',
                'specs': {
                    'processor': 'Intel Core i7-1365U',
                    'ram': '32GB LPDDR5',
                    'storage': '1TB SSD',
                    'display': '14" WUXGA',
                    'battery': 'Up to 18 hours',
                    'weight': '1.12 kg'
                },
                'rating': 4.6
            },
            {
                'name': 'ASUS ROG Zephyrus G14',
                'description': 'AMD Ryzen 9, 32GB RAM, 1TB SSD, RTX 4060. Powerful gaming laptop in a compact form factor.',
                'price': 1599.00,
                'category': 'Laptop',
                'image_url': 'https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400',
                'specs': {
                    'processor': 'AMD Ryzen 9 7940HS',
                    'ram': '32GB DDR5',
                    'storage': '1TB SSD',
                    'display': '14" 165Hz QHD+',
                    'gpu': 'NVIDIA RTX 4060',
                    'battery': 'Up to 10 hours',
                    'weight': '1.72 kg'
                },
                'rating': 4.8
            },
            # Phones
            {
                'name': 'iPhone 15 Pro Max',
                'description': 'A17 Pro chip, 256GB, 6.7" display. The ultimate iPhone with titanium design and advanced camera system.',
                'price': 1199.00,
                'category': 'Phone',
                'image_url': 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400',
                'specs': {
                    'processor': 'A17 Pro',
                    'storage': '256GB',
                    'display': '6.7" Super Retina XDR',
                    'camera': '48MP Main + 12MP Ultra Wide',
                    'battery': 'Up to 29 hours video',
                    'weight': '221 g'
                },
                'rating': 4.9
            },
            {
                'name': 'Samsung Galaxy S24 Ultra',
                'description': 'Snapdragon 8 Gen 3, 256GB, 6.8" display. Premium Android flagship with S Pen included.',
                'price': 1299.00,
                'category': 'Phone',
                'image_url': 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=400',
                'specs': {
                    'processor': 'Snapdragon 8 Gen 3',
                    'ram': '12GB',
                    'storage': '256GB',
                    'display': '6.8" QHD+ Dynamic AMOLED',
                    'camera': '200MP Main + 12MP Ultra Wide',
                    'battery': '5000mAh',
                    'weight': '232 g'
                },
                'rating': 4.8
            },
            {
                'name': 'Google Pixel 8 Pro',
                'description': 'Google Tensor G3, 128GB, 6.7" display. Pure Android with exceptional AI photography features.',
                'price': 999.00,
                'category': 'Phone',
                'image_url': 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=400',
                'specs': {
                    'processor': 'Google Tensor G3',
                    'ram': '12GB',
                    'storage': '128GB',
                    'display': '6.7" LTPO OLED',
                    'camera': '50MP Main + 48MP Ultra Wide',
                    'battery': '5050mAh',
                    'weight': '213 g'
                },
                'rating': 4.6
            },
            {
                'name': 'OnePlus 12',
                'description': 'Snapdragon 8 Gen 3, 256GB, 6.82" display. Flagship killer with fast charging and Hasselblad cameras.',
                'price': 799.00,
                'category': 'Phone',
                'image_url': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400',
                'specs': {
                    'processor': 'Snapdragon 8 Gen 3',
                    'ram': '16GB',
                    'storage': '256GB',
                    'display': '6.82" LTPO AMOLED',
                    'camera': '50MP Main + 48MP Ultra Wide',
                    'battery': '5400mAh',
                    'weight': '220 g'
                },
                'rating': 4.5
            },
            {
                'name': 'Xiaomi 14 Pro',
                'description': 'Snapdragon 8 Gen 3, 256GB, 6.73" display. Leica-tuned cameras with HyperOS.',
                'price': 899.00,
                'category': 'Phone',
                'image_url': 'https://images.unsplash.com/photo-1574944985070-8f3ebc6b79d2?w=400',
                'specs': {
                    'processor': 'Snapdragon 8 Gen 3',
                    'ram': '16GB',
                    'storage': '256GB',
                    'display': '6.73" LTPO AMOLED',
                    'camera': '50MP Leica Triple Camera',
                    'battery': '4880mAh',
                    'weight': '223 g'
                },
                'rating': 4.4
            },
            # Headphones
            {
                'name': 'Sony WH-1000XM5',
                'description': 'Industry-leading noise cancellation with exceptional sound quality and 30-hour battery life.',
                'price': 399.00,
                'category': 'Headphones',
                'image_url': 'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=400',
                'specs': {
                    'type': 'Over-Ear, Wireless',
                    'noise_cancellation': 'Active',
                    'battery': 'Up to 30 hours',
                    'charging': 'USB-C, 3 min = 3 hours',
                    'weight': '250 g',
                    'codecs': 'LDAC, AAC, SBC'
                },
                'rating': 4.8
            },
            {
                'name': 'Bose QuietComfort Ultra',
                'description': 'Spatial audio and legendary quiet with CustomTune technology that personalizes sound.',
                'price': 429.00,
                'category': 'Headphones',
                'image_url': 'https://images.unsplash.com/photo-1613040809024-b4ef7ba99bc3?w=400',
                'specs': {
                    'type': 'Over-Ear, Wireless',
                    'noise_cancellation': 'Active',
                    'battery': 'Up to 24 hours',
                    'charging': 'USB-C',
                    'weight': '240 g',
                    'features': 'Spatial Audio, Immersive Audio'
                },
                'rating': 4.7
            },
            {
                'name': 'Apple AirPods Max',
                'description': 'High-fidelity audio with Active Noise Cancellation and Transparency mode. Premium build quality.',
                'price': 549.00,
                'category': 'Headphones',
                'image_url': 'https://images.unsplash.com/photo-1625245488600-f03fef636a3c?w=400',
                'specs': {
                    'type': 'Over-Ear, Wireless',
                    'noise_cancellation': 'Active',
                    'battery': 'Up to 20 hours',
                    'chip': 'Apple H1',
                    'weight': '384.8 g',
                    'features': 'Transparency mode, Spatial Audio'
                },
                'rating': 4.6
            },
            {
                'name': 'Sennheiser MOMENTUM 4',
                'description': '60-hour battery life with superior sound and advanced codec support.',
                'price': 349.00,
                'category': 'Headphones',
                'image_url': 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=400',
                'specs': {
                    'type': 'Over-Ear, Wireless',
                    'noise_cancellation': 'Hybrid ANC',
                    'battery': 'Up to 60 hours',
                    'charging': 'USB-C',
                    'weight': '293 g',
                    'codecs': 'aptX Adaptive, aptX HD, AAC, SBC'
                },
                'rating': 4.5
            },
            {
                'name': 'AirPods Pro 2nd Gen',
                'description': 'Magical audio experience with Active Noise Cancellation and Adaptive Audio.',
                'price': 249.00,
                'category': 'Headphones',
                'image_url': 'https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=400',
                'specs': {
                    'type': 'In-Ear, Wireless',
                    'noise_cancellation': 'Active',
                    'battery': 'Up to 6 hours (30 with case)',
                    'chip': 'Apple H2',
                    'weight': '5.3 g per earbud',
                    'features': 'Adaptive Audio, Conversation Awareness'
                },
                'rating': 4.9
            },
            {
                'name': 'JBL Tour One M2',
                'description': 'True adaptive noise cancelling with Hi-Res audio certification.',
                'price': 299.00,
                'category': 'Headphones',
                'image_url': 'https://images.unsplash.com/photo-1598532163257-ae3c6b2524b6?w=400',
                'specs': {
                    'type': 'Over-Ear, Wireless',
                    'noise_cancellation': 'Adaptive ANC',
                    'battery': 'Up to 50 hours',
                    'charging': 'USB-C',
                    'weight': '252 g',
                    'certification': 'Hi-Res Audio'
                },
                'rating': 4.4
            },
            # Budget options
            {
                'name': 'Acer Aspire 5',
                'description': 'Intel Core i5, 8GB RAM, 256GB SSD. Affordable laptop for everyday tasks.',
                'price': 549.00,
                'category': 'Laptop',
                'image_url': 'https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=400',
                'specs': {
                    'processor': 'Intel Core i5-1335U',
                    'ram': '8GB DDR4',
                    'storage': '256GB SSD',
                    'display': '15.6" Full HD',
                    'battery': 'Up to 10 hours',
                    'weight': '1.8 kg'
                },
                'rating': 4.2
            },
            {
                'name': 'Samsung Galaxy A54',
                'description': 'Exynos 1380, 128GB, 6.4" display. Mid-range phone with premium features.',
                'price': 449.00,
                'category': 'Phone',
                'image_url': 'https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=400',
                'specs': {
                    'processor': 'Exynos 1380',
                    'ram': '8GB',
                    'storage': '128GB',
                    'display': '6.4" Super AMOLED',
                    'camera': '50MP Triple Camera',
                    'battery': '5000mAh',
                    'weight': '202 g'
                },
                'rating': 4.3
            },
            {
                'name': 'Anker Soundcore Life Q30',
                'description': 'Hi-Res sound with LDAC and multi-mode noise cancellation.',
                'price': 79.00,
                'category': 'Headphones',
                'image_url': 'https://images.unsplash.com/photo-1558756520-22cfe5d382ca?w=400',
                'specs': {
                    'type': 'Over-Ear, Wireless',
                    'noise_cancellation': 'Hybrid ANC',
                    'battery': 'Up to 60 hours',
                    'charging': 'USB-C',
                    'weight': '259 g',
                    'codecs': 'LDAC, AAC, SBC'
                },
                'rating': 4.5
            },
            {
                'name': 'MacBook Air M2',
                'description': 'Apple M2 chip, 8GB RAM, 256GB SSD. Supercharged portable with fanless design.',
                'price': 999.00,
                'category': 'Laptop',
                'image_url': 'https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=400',
                'specs': {
                    'processor': 'Apple M2',
                    'ram': '8GB',
                    'storage': '256GB SSD',
                    'display': '13.6" Liquid Retina',
                    'battery': 'Up to 18 hours',
                    'weight': '1.24 kg'
                },
                'rating': 4.7
            },
        ]

        # Create products
        products = []
        for product_data in products_data:
            product = Product.objects.create(**product_data)
            products.append(product)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(products)} products')
        )
