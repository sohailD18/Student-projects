from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create a demo user for testing the application'

    def handle(self, *args, **options):
        username = 'demo'
        password = 'demo123'
        email = 'demo@example.com'

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'Demo user "{username}" already exists.')
            )
            self.stdout.write(f'Username: {username}')
            self.stdout.write(f'Password: {password}')
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created demo user!')
                )
            self.stdout.write(f'Username: {username}')
            self.stdout.write(f'Password: {password}')
