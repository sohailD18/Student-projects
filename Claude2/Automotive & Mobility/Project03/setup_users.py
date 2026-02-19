#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup script to create/update users and add dummy data
"""
import os
import sys

# Add the project to the path
sys.path.insert(0, 'c:\\Users\\Dell\\OneDrive\\Desktop\\Claude2\\E-commerce\\Project3')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'driver_behavior_project.settings')

import django
django.setup()

from django.contrib.auth.models import User
from driver_app.models import DriverData
from datetime import date, timedelta
import random

print("=" * 60)
print("Driver Behavior Analysis - User & Data Setup")
print("=" * 60)

# Create/update admin user
print("\n[1/4] Setting up admin account...")
try:
    admin = User.objects.get(username='admin')
    admin.set_password('admin1234')
    admin.save()
    print("[OK] Admin password updated: admin / admin1234")
except User.DoesNotExist:
    admin = User.objects.create_superuser('admin', 'admin@driveranalysis.com', 'admin1234')
    print("[OK] Admin created: admin / admin1234")

# Create demo users
print("\n[2/4] Creating demo users...")
demo_users = [
    {
        'username': 'john',
        'email': 'john@example.com',
        'password': 'user123',
        'first_name': 'John',
        'last_name': 'Smith',
    },
    {
        'username': 'sarah',
        'email': 'sarah@example.com',
        'password': 'user123',
        'first_name': 'Sarah',
        'last_name': 'Johnson',
    },
    {
        'username': 'mike',
        'email': 'mike@example.com',
        'password': 'user123',
        'first_name': 'Mike',
        'last_name': 'Williams',
    },
    {
        'username': 'emma',
        'email': 'emma@example.com',
        'password': 'user123',
        'first_name': 'Emma',
        'last_name': 'Davis',
    },
    {
        'username': 'david',
        'email': 'david@example.com',
        'password': 'user123',
        'first_name': 'David',
        'last_name': 'Brown',
    },
]

for user_data in demo_users:
    try:
        user = User.objects.get(username=user_data['username'])
        print(f"  [OK] User '{user_data['username']}' already exists")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
        )
        print(f"  [OK] Created user: {user_data['username']} / {user_data['password']}")

# Clear existing data (optional - uncomment if needed)
# print("\n[3/4] Clearing existing driver data...")
# DriverData.objects.all().delete()
# print("  [OK] All existing data cleared")

# Create dummy driver data
print("\n[3/4] Creating dummy driver data...")

# Helper function to create trip
def create_trip(driver_name, trip_date, avg_speed, max_speed, cornering,
                braking, acceleration):
    """Create a trip with AI analysis"""
    trip = DriverData.objects.create(
        driver_name=driver_name,
        trip_date=trip_date,
        average_speed=avg_speed,
        max_speed=max_speed,
        cornering_speed=cornering,
        harsh_braking_events=braking,
        rapid_acceleration_events=acceleration,
    )

    # Analyze using AI
    from driver_app.ai_utils import analyze_driver_behavior
    result = analyze_driver_behavior({
        'average_speed': avg_speed,
        'max_speed': max_speed,
        'harsh_braking_events': braking,
        'rapid_acceleration_events': acceleration,
        'cornering_speed': cornering,
    })

    trip.risk_score = result['risk_score']
    trip.behavior_class = result['behavior_class']
    trip.recommendations = result['recommendations']
    trip.save()

    return trip

# Generate data for each user
drivers = ['john', 'sarah', 'mike', 'emma', 'david']
base_date = date.today()

driver_profiles = {
    'john': {'safe': 8, 'moderate': 3, 'risky': 1},  # Mostly safe
    'sarah': {'safe': 5, 'moderate': 5, 'risky': 2},  # Mixed
    'mike': {'safe': 3, 'moderate': 6, 'risky': 3},  # Moderate
    'emma': {'safe': 10, 'moderate': 2, 'risky': 0},  # Very safe
    'david': {'safe': 2, 'moderate': 4, 'risky': 6},  # Risky
}

for driver_name in drivers:
    profile = driver_profiles[driver_name]
    total_trips = profile['safe'] + profile['moderate'] + profile['risky']

    print(f"\n  Creating {total_trips} trips for {driver_name}:")

    for i in range(total_trips):
        trip_date = base_date - timedelta(days=random.randint(0, 30))

        # Determine behavior type for this trip
        if i < profile['safe']:
            # Safe trip
            avg_speed = random.randint(40, 55)
            max_speed = random.randint(55, 70)
            cornering = random.randint(20, 35)
            braking = random.randint(0, 1)
            acceleration = random.randint(0, 1)
            behavior = 'Safe'
        elif i < profile['safe'] + profile['moderate']:
            # Moderate trip
            avg_speed = random.randint(55, 75)
            max_speed = random.randint(75, 100)
            cornering = random.randint(35, 55)
            braking = random.randint(2, 4)
            acceleration = random.randint(2, 4)
            behavior = 'Moderate'
        else:
            # Risky trip
            avg_speed = random.randint(80, 110)
            max_speed = random.randint(110, 160)
            cornering = random.randint(55, 80)
            braking = random.randint(5, 8)
            acceleration = random.randint(5, 8)
            behavior = 'Risky'

        trip = create_trip(driver_name, trip_date, avg_speed, max_speed,
                          cornering, braking, acceleration)
        print(f"    [OK] Trip {i+1}: {behavior} (Risk: {trip.risk_score})")

# Print summary
print("\n[4/4] Setup Summary")
print("=" * 60)
print(f"Total Users: {User.objects.count()}")
print(f"Total Driver Data Records: {DriverData.objects.count()}")

# Show breakdown by behavior
safe_count = DriverData.objects.filter(behavior_class='Safe').count()
moderate_count = DriverData.objects.filter(behavior_class='Moderate').count()
risky_count = DriverData.objects.filter(behavior_class='Risky').count()

print(f"\nBehavior Breakdown:")
print(f"  Safe: {safe_count} trips")
print(f"  Moderate: {moderate_count} trips")
print(f"  Risky: {risky_count} trips")

print("\n" + "=" * 60)
print("[OK] Setup Complete!")
print("\nDemo Credentials:")
print("  Admin: admin / admin1234")
print("  Users: john, sarah, mike, emma, david / user123")
print("=" * 60)
