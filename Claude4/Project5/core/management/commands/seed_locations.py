"""
Django management command to seed the database with sample locations.
"""
from django.core.management.base import BaseCommand
from core.models import Location


class Command(BaseCommand):
    help = 'Seed the database with sample Indian cities and landmarks'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database with sample locations...')

        locations = [
            # Major Cities
            {
                'name': 'New Delhi',
                'address': 'Connaught Place, New Delhi',
                'city': 'New Delhi',
                'state': 'Delhi',
                'country': 'India',
                'latitude': 28.6139,
                'longitude': 77.2090,
                'location_type': 'city',
                'is_popular': True,
            },
            {
                'name': 'Mumbai',
                'address': 'South Mumbai, Maharashtra',
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'country': 'India',
                'latitude': 19.0760,
                'longitude': 72.8777,
                'location_type': 'city',
                'is_popular': True,
            },
            {
                'name': 'Bangalore',
                'address': 'Bangalore Central, Karnataka',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'country': 'India',
                'latitude': 12.9716,
                'longitude': 77.5946,
                'location_type': 'city',
                'is_popular': True,
            },
            {
                'name': 'Chennai',
                'address': 'Chennai Central, Tamil Nadu',
                'city': 'Chennai',
                'state': 'Tamil Nadu',
                'country': 'India',
                'latitude': 13.0827,
                'longitude': 80.2707,
                'location_type': 'city',
                'is_popular': True,
            },
            {
                'name': 'Kolkata',
                'address': 'Kolkata Central, West Bengal',
                'city': 'Kolkata',
                'state': 'West Bengal',
                'country': 'India',
                'latitude': 22.5726,
                'longitude': 88.3639,
                'location_type': 'city',
                'is_popular': True,
            },
            {
                'name': 'Hyderabad',
                'address': 'Hyderabad Central, Telangana',
                'city': 'Hyderabad',
                'state': 'Telangana',
                'country': 'India',
                'latitude': 17.3850,
                'longitude': 78.4867,
                'location_type': 'city',
                'is_popular': True,
            },
            {
                'name': 'Pune',
                'address': 'Pune Central, Maharashtra',
                'city': 'Pune',
                'state': 'Maharashtra',
                'country': 'India',
                'latitude': 18.5204,
                'longitude': 73.8567,
                'location_type': 'city',
                'is_popular': True,
            },
            {
                'name': 'Ahmedabad',
                'address': 'Ahmedabad Central, Gujarat',
                'city': 'Ahmedabad',
                'state': 'Gujarat',
                'country': 'India',
                'latitude': 23.0225,
                'longitude': 72.5714,
                'location_type': 'city',
                'is_popular': True,
            },
            {
                'name': 'Jaipur',
                'address': 'Jaipur Central, Rajasthan',
                'city': 'Jaipur',
                'state': 'Rajasthan',
                'country': 'India',
                'latitude': 26.9124,
                'longitude': 75.7873,
                'location_type': 'city',
                'is_popular': True,
            },
            {
                'name': 'Lucknow',
                'address': 'Lucknow Central, Uttar Pradesh',
                'city': 'Lucknow',
                'state': 'Uttar Pradesh',
                'country': 'India',
                'latitude': 26.8467,
                'longitude': 80.9462,
                'location_type': 'city',
                'is_popular': True,
            },
            # Landmarks
            {
                'name': 'India Gate',
                'address': 'Rajpath, India Gate, New Delhi',
                'city': 'New Delhi',
                'state': 'Delhi',
                'country': 'India',
                'latitude': 28.6130,
                'longitude': 77.2295,
                'location_type': 'landmark',
                'is_popular': True,
            },
            {
                'name': 'Taj Mahal',
                'address': 'Taj Ganj, Agra',
                'city': 'Agra',
                'state': 'Uttar Pradesh',
                'country': 'India',
                'latitude': 27.1751,
                'longitude': 78.0421,
                'location_type': 'landmark',
                'is_popular': True,
            },
            {
                'name': 'Gateway of India',
                'address': 'Apollo Bandar, Mumbai',
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'country': 'India',
                'latitude': 18.9220,
                'longitude': 72.8347,
                'location_type': 'landmark',
                'is_popular': True,
            },
            {
                'name': 'Kashmir Gate',
                'address': 'Kashmir Gate, Delhi',
                'city': 'New Delhi',
                'state': 'Delhi',
                'country': 'India',
                'latitude': 28.6658,
                'longitude': 77.2284,
                'location_type': 'landmark',
                'is_popular': False,
            },
            {
                'name': 'Connaught Place',
                'address': 'Connaught Place, New Delhi',
                'city': 'New Delhi',
                'state': 'Delhi',
                'country': 'India',
                'latitude': 28.6315,
                'longitude': 77.2167,
                'location_type': 'landmark',
                'is_popular': True,
            },
            # Airports
            {
                'name': 'Indira Gandhi International Airport',
                'address': 'Delhi Airport, New Delhi',
                'city': 'New Delhi',
                'state': 'Delhi',
                'country': 'India',
                'latitude': 28.5562,
                'longitude': 77.1000,
                'location_type': 'airport',
                'is_popular': True,
            },
            {
                'name': 'Chhatrapati Shivaji International Airport',
                'address': 'Mumbai Airport, Mumbai',
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'country': 'India',
                'latitude': 19.0896,
                'longitude': 72.8656,
                'location_type': 'airport',
                'is_popular': True,
            },
            {
                'name': 'Kempegowda International Airport',
                'address': 'Bangalore Airport, Bangalore',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'country': 'India',
                'latitude': 13.1986,
                'longitude': 77.7066,
                'location_type': 'airport',
                'is_popular': True,
            },
        ]

        created_count = 0
        for loc_data in locations:
            # Check if location already exists
            if not Location.objects.filter(name=loc_data['name'], city=loc_data['city']).exists():
                Location.objects.create(**loc_data)
                created_count += 1
                self.stdout.write(f'  Created: {loc_data["name"]}, {loc_data["city"]}')
            else:
                self.stdout.write(f'  Already exists: {loc_data["name"]}, {loc_data["city"]}')

        self.stdout.write(self.style.SUCCESS(f'✓ Successfully seeded {created_count} locations!'))
