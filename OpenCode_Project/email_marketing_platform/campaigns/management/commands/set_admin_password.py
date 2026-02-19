from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Set the admin user password to admin123'

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username='admin')
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Successfully set admin password to admin123'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Admin user does not exist. Please create a superuser first.'))
