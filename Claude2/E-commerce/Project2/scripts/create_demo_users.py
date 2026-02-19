"""
Create Demo Users Script

Creates sample regular users for testing the authentication system.

Users created:
- Username: manager, Password: manager123
- Username: staff1, Password: staff123
- Username: staff2, Password: staff123

Usage:
    python scripts/create_demo_users.py
"""

import os
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_project.settings')

import django
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()


def create_demo_users():
    """Create demo regular users"""

    demo_users = [
        {
            'username': 'manager',
            'password': 'manager123',
            'email': 'manager@inventory.com',
            'first_name': 'John',
            'last_name': 'Manager'
        },
        {
            'username': 'staff1',
            'password': 'staff123',
            'email': 'staff1@inventory.com',
            'first_name': 'Alice',
            'last_name': 'Smith'
        },
        {
            'username': 'staff2',
            'password': 'staff123',
            'email': 'staff2@inventory.com',
            'first_name': 'Bob',
            'last_name': 'Johnson'
        }
    ]

    created_count = 0
    updated_count = 0

    for user_data in demo_users:
        username = user_data['username']
        password = user_data['password']

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            user.set_password(password)
            user.email = user_data['email']
            user.first_name = user_data['first_name']
            user.last_name = user_data['last_name']
            user.save()
            print(f"[UPDATE] User '{username}' password reset")
            updated_count += 1
        else:
            # Create new user
            user = User.objects.create_user(
                username=username,
                email=user_data['email'],
                password=password,
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )
            print(f"[CREATED] User '{username}' created successfully")
            created_count += 1

    print(f"\n[SUMMARY]")
    print(f"   Created: {created_count} users")
    print(f"   Updated: {updated_count} users")
    print(f"   Total: {created_count + updated_count} users")


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("CREATE DEMO USERS")
    print("=" * 60 + "\n")

    create_demo_users()

    print("\n" + "=" * 60)
    print("Demo users created successfully!")
    print("=" * 60)
    print("\n[Credentials]")
    print("   1. manager / manager123")
    print("   2. staff1 / staff123")
    print("   3. staff2 / staff123")
    print("\nLogin at: http://127.0.0.1:8000/login/\n")
