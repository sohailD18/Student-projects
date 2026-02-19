"""
Test Data Creation Script for InfraGuard
Run with: python manage.py shell < create_test_data.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'infra_guard.settings')
django.setup()

from django.contrib.auth.models import User
from reports.models import UserProfile, Incident, Claim
from django.utils import timezone
from datetime import timedelta
import random


def create_test_data():
    """Create sample test data for demonstration"""

    print("Creating test data for InfraGuard...")

    # Create test users
    users_data = [
        {
            'username': 'john_citizen',
            'email': 'john@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'testpass123',
            'role': 'citizen',
            'phone': '555-0101'
        },
        {
            'username': 'jane_citizen',
            'email': 'jane@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'password': 'testpass123',
            'role': 'citizen',
            'phone': '555-0102'
        },
        {
            'username': 'admin_authority',
            'email': 'admin@infraguard.org',
            'first_name': 'Admin',
            'last_name': 'User',
            'password': 'testpass123',
            'role': 'authority',
            'phone': '555-9999'
        }
    ]

    created_users = {}
    for user_data in users_data:
        username = user_data['username']
        role = user_data['role']

        # Check if user exists
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            print(f"  User '{username}' already exists, skipping...")
        else:
            user = User.objects.create_user(
                username=username,
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                password=user_data['password']
            )
            UserProfile.objects.create(
                user=user,
                role=role,
                phone=user_data.get('phone', '')
            )
            print(f"  Created user: {username} ({role})")

        created_users[username] = User.objects.get(username=username)

    # Get users
    john = created_users['john_citizen']
    jane = created_users['jane_citizen']
    admin = created_users['admin_authority']

    # Create sample incidents
    incidents_data = [
        {
            'location': '123 Main Street, Downtown',
            'description': 'Large pothole causing damage to vehicles. Very dangerous at night.',
            'incident_type': 'pothole',
            'severity': 75,
            'status': 'pending',
            'reported_by': john,
            'has_image': True
        },
        {
            'location': '456 Oak Avenue, Near Park',
            'description': 'Drainage completely blocked, water flooding the street during rain.',
            'incident_type': 'drainage',
            'severity': 60,
            'status': 'verified',
            'verified_at': timezone.now() - timedelta(days=2),
            'reported_by': john,
            'has_image': True
        },
        {
            'location': '789 Pine Road, Residential Area',
            'description': 'Street light has been out for a week. Very dark and unsafe for pedestrians.',
            'incident_type': 'streetlight',
            'severity': 50,
            'status': 'resolved',
            'verified_at': timezone.now() - timedelta(days=10),
            'resolved_at': timezone.now() - timedelta(days=5),
            'reported_by': jane,
            'has_image': False
        },
        {
            'location': '321 Elm Street, Near School',
            'description': 'Footpath badly damaged with raised concrete. Trip hazard for children.',
            'incident_type': 'footpath',
            'severity': 85,
            'status': 'verified',
            'verified_at': timezone.now() - timedelta(days=1),
            'reported_by': jane,
            'has_image': True
        },
        {
            'location': '555 Maple Drive, Commercial District',
            'description': 'Multiple potholes on this stretch of road. Emergency repair needed.',
            'incident_type': 'pothole',
            'severity': 90,
            'status': 'pending',
            'reported_by': john,
            'has_image': False
        },
        {
            'location': '123 Main Street, Downtown',
            'description': 'Another pothole reported near the first one. This area needs attention.',
            'incident_type': 'pothole',
            'severity': 55,
            'status': 'rejected',
            'reported_by': jane,
            'has_image': False
        },
        {
            'location': '999 Cedar Lane, Industrial Area',
            'description': 'Water logging from clogged drain. Mosquito breeding concern.',
            'incident_type': 'drainage',
            'severity': 70,
            'status': 'verified',
            'verified_at': timezone.now() - timedelta(days=3),
            'reported_by': john,
            'has_image': True
        }
    ]

    for i, inc_data in enumerate(incidents_data):
        # Check if similar incident exists
        if Incident.objects.filter(location=inc_data['location'], description=inc_data['description']).exists():
            print(f"  Incident at '{inc_data['location']}' already exists, skipping...")
            continue

        incident = Incident.objects.create(
            location=inc_data['location'],
            description=inc_data['description'],
            incident_type=inc_data['incident_type'],
            severity_score=inc_data['severity'],
            status=inc_data['status'],
            reported_by=inc_data['reported_by'],
            verified_at=inc_data.get('verified_at'),
            resolved_at=inc_data.get('resolved_at'),
            authority_notes='Verified by authority' if inc_data['status'] in ['verified', 'resolved'] else None,
            latitude=40.7128 + (i * 0.01),
            longitude=-74.0060 + (i * 0.01)
        )
        print(f"  Created incident #{incident.id}: {incident.incident_type} at {incident.location}")

        # Create some claims for verified incidents
        if incident.status == 'verified' and incident.id in [2, 4, 7]:
            claim_data = {
                'incident': incident,
                'victim_name': incident.reported_by.first_name + ' ' + incident.reported_by.last_name,
                'claim_amount': 500.00 if incident.severity_score > 60 else 250.00,
                'status': random.choice(['filed', 'under_review', 'approved']),
                'evidence_description': 'Vehicle damage repair costs and medical expenses due to this infrastructure issue.'
            }

            if Claim.objects.filter(incident=incident).exists():
                print(f"    Claim already exists for incident #{incident.id}, skipping...")
            else:
                claim = Claim.objects.create(**claim_data)
                if claim.status == 'approved':
                    claim.reviewed_by = admin
                    claim.reviewed_at = timezone.now() - timedelta(days=1)
                    claim.approved_amount = claim.claim_amount * 0.8
                    claim.save()
                print(f"    Created claim for incident #{incident.id}: {claim.status} - ${claim.claim_amount}")

    print("\n✅ Test data creation completed!")
    print("\nLogin credentials:")
    print("  Citizen: john_citizen / testpass123")
    print("  Citizen: jane_citizen / testpass123")
    print("  Authority: admin_authority / testpass123")


if __name__ == '__main__':
    create_test_data()
