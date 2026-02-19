from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile


class Command(BaseCommand):
    help = 'Creates an admin user with username: admin, password: 1234'

    def handle(self, *args, **options):
        username = 'admin'
        password = '1234'

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            # Update password
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(
                self.style.WARNING(f'Admin user "{username}" already exists. Password updated.')
            )
        else:
            # Create new admin user
            user = User.objects.create_user(
                username=username,
                password=password,
                is_staff=True,
                is_superuser=True
            )
            # Create profile
            UserProfile.objects.get_or_create(user=user)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created admin user "{username}"')
            )

        self.stdout.write(
            self.style.SUCCESS(f'\nAdmin credentials:\n  Username: {username}\n  Password: {password}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'\nLogin at: http://127.0.0.1:8000/users/login/\nDjango Admin: http://127.0.0.1:8000/admin/')
        )
