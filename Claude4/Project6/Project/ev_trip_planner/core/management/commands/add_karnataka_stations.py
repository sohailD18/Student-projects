from django.core.management.base import BaseCommand
from core.models import ChargingStation


class Command(BaseCommand):
    help = 'Add sample charging stations in Karnataka, India'

    def handle(self, *args, **options):
        stations = [
            {
                'name': 'Tata Power Charging Station',
                'location': 'Bangalore',
                'latitude': 12.9716,
                'longitude': 77.5946,
                'address': 'MG Road, Bangalore, Karnataka 560001',
                'connector_type': 'CCS2',
                'power_kw': 50,
                'price_per_kwh': 15.00,
                'fast_charging': True,
                'total_ports': 4,
                'available_ports': 2,
                'amenities': 'WiFi, Restroom, Coffee Shop, Parking',
                'description': 'Fast charging station located in the heart of Bangalore city center.'
            },
            {
                'name': 'Ather Grid Hosur Road',
                'location': 'Bangalore',
                'latitude': 12.9141,
                'longitude': 77.6101,
                'address': 'Hosur Road, Bangalore, Karnataka 560068',
                'connector_type': 'Type2',
                'power_kw': 7.5,
                'price_per_kwh': 12.00,
                'fast_charging': False,
                'total_ports': 6,
                'available_ports': 4,
                'amenities': 'WiFi, Covered Parking, Restroom',
                'description': 'Ather Grid charging point with multiple Type 2 connectors.'
            },
            {
                'name': 'MG Motor EV Station',
                'location': 'Bangalore',
                'latitude': 12.9352,
                'longitude': 77.6245,
                'address': 'Koramangala, Bangalore, Karnataka 560034',
                'connector_type': 'CCS2',
                'power_kw': 60,
                'price_per_kwh': 18.00,
                'fast_charging': True,
                'total_ports': 3,
                'available_ports': 3,
                'amenities': 'WiFi, Restroom, Shopping Mall',
                'description': 'DC fast charging at Koramangala shopping complex.'
            },
            {
                'name': 'Station Mysore Road',
                'location': 'Mysore',
                'latitude': 12.3119,
                'longitude': 76.6524,
                'address': 'Mysore-Bangalore Highway, Mysore, Karnataka 570013',
                'connector_type': 'Bharat_DC',
                'power_kw': 30,
                'price_per_kwh': 12.50,
                'fast_charging': True,
                'total_ports': 2,
                'available_ports': 1,
                'amenities': 'Restroom, Food Court, Parking',
                'description': 'Bharat DC standard charger on Bangalore-Mysore highway.'
            },
            {
                'name': 'Tata Motors Hub',
                'location': 'Hubli',
                'latitude': 15.3647,
                'longitude': 75.1240,
                'address': 'Gokul Road, Hubli, Karnataka 580020',
                'connector_type': 'CCS2',
                'power_kw': 50,
                'price_per_kwh': 15.00,
                'fast_charging': True,
                'total_ports': 3,
                'available_ports': 2,
                'amenities': 'WiFi, Restroom, 24/7 Service',
                'description': 'Tata motors authorized charging station in North Karnataka.'
            },
            {
                'name': 'Hyundai Charging Plaza',
                'location': 'Mangalore',
                'latitude': 12.9141,
                'longitude': 74.8560,
                'address': 'Lalbagh, Mangalore, Karnataka 575002',
                'connector_type': 'CCS2',
                'power_kw': 60,
                'price_per_kwh': 16.00,
                'fast_charging': True,
                'total_ports': 2,
                'available_ports': 2,
                'amenities': 'WiFi, Covered Parking, Restroom',
                'description': 'Hyundai Kona & ZS EV fast charging station in coastal Karnataka.'
            },
            {
                'name': 'Public Charging Station',
                'location': 'Belgaum',
                'latitude': 15.8481,
                'longitude': 74.5129,
                'address': 'Khanapur Road, Belgaum, Karnataka 590001',
                'connector_type': 'CHAdeMO',
                'power_kw': 50,
                'price_per_kwh': 14.00,
                'fast_charging': True,
                'total_ports': 2,
                'available_ports': 1,
                'amenities': 'Restroom, Parking',
                'description': 'Public fast charging station for all EV types.'
            },
            {
                'name': 'Electric Avenue',
                'location': 'Bangalore',
                'latitude': 13.0218,
                'longitude': 77.6410,
                'address': 'Yelahanka, Bangalore, Karnataka 560063',
                'connector_type': 'CCS2',
                'power_kw': 100,
                'price_per_kwh': 20.00,
                'fast_charging': True,
                'total_ports': 5,
                'available_ports': 3,
                'amenities': 'WiFi, Restroom, Restaurant, 24/7 Available',
                'description': 'Ultra-fast 100kW charging station near Bangalore airport.'
            },
            {
                'name': 'Solar Powered Station',
                'location': 'Mysore',
                'latitude': 12.3127,
                'longitude': 76.6475,
                'address': 'Saraswathipuram, Mysore, Karnataka 570009',
                'connector_type': 'Type2',
                'power_kw': 11,
                'price_per_kwh': 10.00,
                'fast_charging': False,
                'total_ports': 4,
                'available_ports': 3,
                'amenities': 'Solar Powered, Eco-friendly, Parking',
                'description': 'Environmentally friendly solar-powered charging station.'
            },
            {
                'name': 'Highway Charging Plaza',
                'location': 'Tumkur',
                'latitude': 13.3392,
                'longitude': 77.1130,
                'address': 'Bangalore-Pune Highway, Tumkur, Karnataka 572101',
                'connector_type': 'Bharat_DC',
                'power_kw': 50,
                'price_per_kwh': 15.00,
                'fast_charging': True,
                'total_ports': 3,
                'available_ports': 2,
                'amenities': 'Restroom, Food Court, Parking, 24/7 Available',
                'description': 'Convenient highway stop for long distance travelers.'
            },
        ]

        created_count = 0
        for station_data in stations:
            station, created = ChargingStation.objects.get_or_create(
                name=station_data['name'],
                defaults=station_data
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {station.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Already exists: {station.name}'))

        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully added {created_count} charging stations in Karnataka!')
        )
