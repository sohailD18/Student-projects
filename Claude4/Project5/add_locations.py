"""
Script to add sample locations in Karnataka, India to the database.
Run with: python manage.py shell < add_locations.py
Or: python add_locations.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trip_planner_ai.settings')
django.setup()

from core.models import Location

# Sample locations in Karnataka, India
karnataka_locations = [
    # Major Cities
    {
        'name': 'Bangalore',
        'city': 'Bengaluru',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 12.9716,
        'longitude': 77.5946,
        'location_type': 'city',
        'is_popular': True,
        'address': 'Bangalore, Karnataka, India'
    },
    {
        'name': 'Mysore Palace',
        'city': 'Mysuru',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 12.3054,
        'longitude': 76.6551,
        'location_type': 'landmark',
        'is_popular': True,
        'address': 'Mysore Palace, Mysuru, Karnataka, India'
    },
    {
        'name': 'Hampi',
        'city': 'Hampi',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 15.3350,
        'longitude': 76.4620,
        'location_type': 'landmark',
        'is_popular': True,
        'address': 'Hampi, Karnataka, India'
    },
    {
        'name': 'Cubbon Park',
        'city': 'Bengaluru',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 12.9769,
        'longitude': 77.6046,
        'location_type': 'landmark',
        'is_popular': False,
        'address': 'Cubbon Park, Bangalore, Karnataka, India'
    },
    {
        'name': 'Lalbagh Botanical Garden',
        'city': 'Bengaluru',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 12.9480,
        'longitude': 77.5832,
        'location_type': 'landmark',
        'is_popular': False,
        'address': 'Lalbagh Botanical Garden, Bangalore, Karnataka, India'
    },
    {
        'name': 'Bangalore Palace',
        'city': 'Bengaluru',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 12.9986,
        'longitude': 77.5920,
        'location_type': 'landmark',
        'is_popular': False,
        'address': 'Bangalore Palace, Bangalore, Karnataka, India'
    },
    {
        'name': 'Tipu Sultan Summer Palace',
        'city': 'Bengaluru',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 12.9576,
        'longitude': 77.5718,
        'location_type': 'landmark',
        'is_popular': False,
        'address': 'Tipu Sultan Summer Palace, Bangalore, Karnataka, India'
    },
    {
        'name': 'ISKCON Temple Bangalore',
        'city': 'Bengaluru',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 13.0097,
        'longitude': 77.5511,
        'location_type': 'landmark',
        'is_popular': False,
        'address': 'ISKCON Temple, Bangalore, Karnataka, India'
    },
    {
        'name': 'Bannerghatta National Park',
        'city': 'Bengaluru',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 12.7000,
        'longitude': 77.5750,
        'location_type': 'landmark',
        'is_popular': False,
        'address': 'Bannerghatta National Park, Bangalore, Karnataka, India'
    },
    {
        'name': 'Wonderla Amusement Park',
        'city': 'Bengaluru',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 12.8282,
        'longitude': 77.3946,
        'location_type': 'landmark',
        'is_popular': False,
        'address': 'Wonderla, Bangalore, Karnataka, India'
    },
    {
        'name': 'MG Brigade Road',
        'city': 'Bengaluru',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 12.9756,
        'longitude': 77.6066,
        'location_type': 'address',
        'is_popular': False,
        'address': 'MG Brigade Road, Bangalore, Karnataka, India'
    },
    {
        'name': 'Commercial Street',
        'city': 'Bengaluru',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 12.9814,
        'longitude': 77.6039,
        'location_type': 'address',
        'is_popular': False,
        'address': 'Commercial Street, Bangalore, Karnataka, India'
    },
    {
        'name': 'Brindavan Gardens',
        'city': 'Mysuru',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 12.4249,
        'longitude': 76.5682,
        'location_type': 'landmark',
        'is_popular': True,
        'address': 'Brindavan Gardens, Mysuru, Karnataka, India'
    },
    {
        'name': 'Chamundi Hills',
        'city': 'Mysuru',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 12.2448,
        'longitude': 76.6561,
        'location_type': 'landmark',
        'is_popular': False,
        'address': 'Chamundi Hills, Mysuru, Karnataka, India'
    },
    {
        'name': 'Belur Temple',
        'city': 'Belur',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 13.1687,
        'longitude': 75.8687,
        'location_type': 'landmark',
        'is_popular': True,
        'address': 'Belur Temple, Belur, Karnataka, India'
    },
    {
        'name': 'Halebidu Temple',
        'city': 'Halebidu',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 13.2139,
        'longitude': 75.9539,
        'location_type': 'landmark',
        'is_popular': True,
        'address': 'Halebidu Temple, Hassan, Karnataka, India'
    },
    {
        'name': 'Gokarna Beach',
        'city': 'Gokarna',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 14.5439,
        'longitude': 74.3189,
        'location_type': 'landmark',
        'is_popular': True,
        'address': 'Gokarna Beach, Karnataka, India'
    },
    {
        'name': 'Jog Falls',
        'city': 'Sagara',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 14.2296,
        'longitude': 74.8127,
        'location_type': 'landmark',
        'is_popular': True,
        'address': 'Jog Falls, Shimoga, Karnataka, India'
    },
    {
        'name': 'Coorg',
        'city': 'Madikeri',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 12.4258,
        'longitude': 75.7394,
        'location_type': 'city',
        'is_popular': True,
        'address': 'Coorg, Madikeri, Karnataka, India'
    },
    {
        'name': 'Chikmagalur',
        'city': 'Chikmagalur',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 13.3182,
        'longitude': 75.7719,
        'location_type': 'city',
        'is_popular': True,
        'address': 'Chikmagalur, Karnataka, India'
    },
    {
        'name': 'Hubli',
        'city': 'Hubli',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 15.3647,
        'longitude': 75.1240,
        'location_type': 'city',
        'is_popular': False,
        'address': 'Hubli, Karnataka, India'
    },
    {
        'name': 'Dharwad',
        'city': 'Dharwad',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 15.4579,
        'longitude': 75.0076,
        'location_type': 'city',
        'is_popular': False,
        'address': 'Dharwad, Karnataka, India'
    },
    {
        'name': 'Mangalore',
        'city': 'Mangaluru',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 12.9141,
        'longitude': 74.8560,
        'location_type': 'city',
        'is_popular': True,
        'address': 'Mangalore, Karnataka, India'
    },
    {
        'name': 'Udupi',
        'city': 'Udupi',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 13.3409,
        'longitude': 74.7421,
        'location_type': 'city',
        'is_popular': False,
        'address': 'Udupi, Karnataka, India'
    },
    {
        'name': 'Bangalore Airport',
        'city': 'Devanahalli',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 13.1986,
        'longitude': 77.7066,
        'location_type': 'airport',
        'is_popular': False,
        'address': 'Kempegowda International Airport, Bangalore, Karnataka, India'
    },
    {
        'name': 'Mysore Airport',
        'city': 'Mysuru',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 12.2338,
        'longitude': 76.6961,
        'location_type': 'airport',
        'is_popular': False,
        'address': 'Mysore Airport, Mysuru, Karnataka, India'
    },
    {
        'name': 'Bangalore City Railway Station',
        'city': 'Bengaluru',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 12.9777,
        'longitude': 77.5718,
        'location_type': 'station',
        'is_popular': False,
        'address': 'Bangalore City Junction, Bangalore, Karnataka, India'
    },
    {
        'name': 'Mysore Railway Station',
        'city': 'Mysuru',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 12.3128,
        'longitude': 76.6473,
        'location_type': 'station',
        'is_popular': False,
        'address': 'Mysore Junction, Mysuru, Karnataka, India'
    },
    {
        'name': 'Vidhana Soudha',
        'city': 'Bengaluru',
        'state': 'Karnataka',
        'country': 'India',
        'latitude': 12.9797,
        'longitude': 77.5907,
        'location_type': 'landmark',
        'is_popular': False,
        'address': 'Vidhana Soudha, Bangalore, Karnataka, India'
    },
]

# Add locations to database
print(f"Adding {len(karnataka_locations)} locations to database...")
print(f"Existing locations: {Location.objects.count()}")

added_count = 0
updated_count = 0

for location_data in karnataka_locations:
    # Check if location already exists
    name = location_data['name']
    city = location_data['city']

    existing = Location.objects.filter(name=name, city=city).first()

    if existing:
        # Update existing location
        for key, value in location_data.items():
            setattr(existing, key, value)
        existing.save()
        updated_count += 1
        print(f"[+] Updated: {name}, {city}")
    else:
        # Create new location
        Location.objects.create(**location_data)
        added_count += 1
        print(f"[+] Added: {name}, {city}")

print(f"\n=== Summary ===")
print(f"Total locations in database: {Location.objects.count()}")
print(f"New locations added: {added_count}")
print(f"Locations updated: {updated_count}")
print("\nPopular destinations:")
for loc in Location.objects.filter(is_popular=True).order_by('name'):
    print(f"  * {loc.name}, {loc.city}")
