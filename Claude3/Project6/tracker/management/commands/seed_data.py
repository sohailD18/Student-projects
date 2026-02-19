"""
Management command to seed the database with sample data.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random
from tracker.models import Industry, EmissionRecord, CarbonPrice


class Command(BaseCommand):
    help = 'Seeds the database with sample carbon credit data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        # Clear existing data
        self.stdout.write('Clearing existing data...')
        CarbonPrice.objects.all().delete()
        EmissionRecord.objects.all().delete()
        Industry.objects.all().delete()

        # Create industries
        industries_data = [
            {
                'name': 'GreenTech Manufacturing',
                'industry_type': 'manufacturing',
                'emission_limit': 5000,
                'description': 'Leading sustainable manufacturing company focused on eco-friendly production methods.'
            },
            {
                'name': 'SolarPower Energy Corp',
                'industry_type': 'energy',
                'emission_limit': 8000,
                'description': 'Renewable energy company specializing in solar power generation.'
            },
            {
                'name': 'EcoChem Industries',
                'industry_type': 'chemical',
                'emission_limit': 6500,
                'description': 'Chemical company committed to reducing environmental impact.'
            },
            {
                'name': 'StrongBuild Cement',
                'industry_type': 'cement',
                'emission_limit': 10000,
                'description': 'Construction materials manufacturer implementing green technologies.'
            },
            {
                'name': 'AutoGreen Motors',
                'industry_type': 'automotive',
                'emission_limit': 7000,
                'description': 'Electric vehicle manufacturer with sustainable production practices.'
            }
        ]

        industries = []
        for data in industries_data:
            industry = Industry.objects.create(**data)
            industries.append(industry)
            self.stdout.write(f'Created industry: {industry.name}')

        # Generate historical emission data (2 years back)
        self.stdout.write('\nGenerating emission records...')
        current_year = timezone.now().year
        current_month = timezone.now().month

        for industry in industries:
            # Base emission varies by industry type
            base_emission = {
                'manufacturing': 350,
                'energy': 500,
                'chemical': 420,
                'cement': 650,
                'automotive': 450
            }.get(industry.industry_type, 400)

            # Generate 24 months of data
            for year_offset in range(2):
                for month in range(1, 13):
                    # Calculate actual date
                    actual_year = current_year - 1 + year_offset
                    actual_month = month

                    # Skip if date is in the future
                    if year_offset == 1 and month >= current_month:
                        continue

                    # Add seasonality and random variation
                    seasonal_factor = 1.0 + 0.2 * random.sin(month * 3.14159 / 6)  # Seasonal pattern
                    random_factor = random.uniform(0.85, 1.15)  # Random variation
                    trend_factor = 1.0 - (0.02 * (24 - ((year_offset * 12) + month)) / 24)  # Slight improving trend

                    emission = base_emission * seasonal_factor * random_factor * trend_factor

                    EmissionRecord.objects.create(
                        industry=industry,
                        year=actual_year,
                        month=actual_month,
                        emission_amount=round(emission, 2)
                    )

            self.stdout.write(f'  Generated emission records for {industry.name}')

        # Generate carbon price data (1 year back)
        self.stdout.write('\nGenerating carbon price data...')
        base_price = 45.00  # Starting price

        for days_ago in range(365, 0, -1):
            date = datetime.now().date() - timedelta(days=days_ago)

            # Price fluctuates with trend and randomness
            trend = 0.02 * (1 - days_ago / 365)  # Slight upward trend
            daily_change = random.uniform(-0.5, 0.6)  # Daily fluctuation
            price = base_price + trend * 10 + daily_change

            CarbonPrice.objects.create(
                date=date,
                price_per_ton=round(max(20, price), 2)  # Minimum price of $20
            )

        self.stdout.write(self.style.SUCCESS('\n✓ Database seeding completed successfully!'))
        self.stdout.write(f'  - Created {len(industries)} industries')
        self.stdout.write(f'  - Created {EmissionRecord.objects.count()} emission records')
        self.stdout.write(f'  - Created {CarbonPrice.objects.count()} carbon price entries')
