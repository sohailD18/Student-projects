"""
Create Admin User Script

Creates a superuser with predefined credentials:
Username: admin
Password: 1234

Usage:
    python scripts/create_admin.py
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


def create_admin_user():
    """Create admin user with specific credentials"""

    username = 'admin'
    password = '1234'
    email = 'admin@inventory.com'

    # Check if admin already exists
    if User.objects.filter(username=username).exists():
        print(f"[WARNING] Admin user '{username}' already exists!")
        user = User.objects.get(username=username)
        # Reset password
        user.set_password(password)
        user.email = email
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print(f"[SUCCESS] Admin user '{username}' password reset to '{password}'")
        return

    # Create new admin user
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.is_superuser = True
        user.is_staff = True
        user.save()

        print("[SUCCESS] Admin user created successfully!")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Email: {email}")
        print("\nYou can now login at: http://127.0.0.1:8000/admin/")

    except Exception as e:
        print(f"[ERROR] Error creating admin user: {e}")


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("CREATE ADMIN USER")
    print("=" * 60 + "\n")

    create_admin_user()

    print("\n" + "=" * 60)
    print("Admin user setup complete!")
    print("=" * 60 + "\n")
