from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Create user profiles for existing users'

    def handle(self, *args, **kwargs):
        users_without_profiles = User.objects.filter(profile__isnull=True)

        count = 0
        for user in users_without_profiles:
            # Determine user type based on username or existing data
            user_type = 'job_seeker'  # default
            if user.username == 'admin':
                user_type = 'employer'

            UserProfile.objects.create(
                user=user,
                user_type=user_type
            )
            count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Created profile for {user.username} as {user_type}')
            )

        if count == 0:
            self.stdout.write(self.style.WARNING('All users already have profiles.'))
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\nSuccessfully created {count} user profiles!')
            )
