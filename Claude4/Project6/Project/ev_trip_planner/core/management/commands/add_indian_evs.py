from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Vehicle


class Command(BaseCommand):
    help = 'Add sample Indian EV vehicles for demo purposes'

    def handle(self, *args, **options):
        # Get or create a demo user
        user, created = User.objects.get_or_create(
            username='demo',
            defaults={
                'email': 'demo@example.com',
                'first_name': 'Demo',
                'last_name': 'User'
            }
        )
        if created:
            user.set_password('demo123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created demo user (username: demo, password: demo123)'))
        else:
            self.stdout.write(self.style.WARNING('Demo user already exists'))

        # Sample Indian EVs
        sample_evs = [
            {
                'make': 'Tata',
                'model': 'Nexon EV',
                'year': 2024,
                'ev_type': 'BEV',
                'battery_capacity': 40.5,
                'range_km': 312,
                'charging_speed': 50,
            },
            {
                'make': 'Tata',
                'model': 'Tiago EV',
                'year': 2024,
                'ev_type': 'BEV',
                'battery_capacity': 24.0,
                'range_km': 315,
                'charging_speed': 25,
            },
            {
                'make': 'Tata',
                'model': 'Punch EV',
                'year': 2024,
                'ev_type': 'BEV',
                'battery_capacity': 35.0,
                'range_km': 421,
                'charging_speed': 50,
            },
            {
                'make': 'Mahindra',
                'model': 'XUV400',
                'year': 2024,
                'ev_type': 'BEV',
                'battery_capacity': 39.5,
                'range_km': 456,
                'charging_speed': 50,
            },
            {
                'make': 'Hyundai',
                'model': 'Kona Electric',
                'year': 2023,
                'ev_type': 'BEV',
                'battery_capacity': 39.2,
                'range_km': 452,
                'charging_speed': 100,
            },
            {
                'make': 'MG',
                'model': 'ZS EV',
                'year': 2024,
                'ev_type': 'BEV',
                'battery_capacity': 50.3,
                'range_km': 461,
                'charging_speed': 80,
            },
        ]

        created_count = 0
        for ev_data in sample_evs:
            vehicle, created = Vehicle.objects.get_or_create(
                user=user,
                make=ev_data['make'],
                model=ev_data['model'],
                defaults=ev_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Added: {vehicle.year} {vehicle.make} {vehicle.model} ({vehicle.range_km} km)')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Already exists: {vehicle.year} {vehicle.make} {vehicle.model}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully added {created_count} sample Indian EVs to demo account!')
        )
        self.stdout.write(
            self.style.WARNING('\nLogin with: username: demo, password: demo123')
        )
