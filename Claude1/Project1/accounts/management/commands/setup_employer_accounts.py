from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from jobs.models import Job


class Command(BaseCommand):
    help = 'Create employer accounts for existing companies'

    def handle(self, *args, **options):
        # Company data with their usernames and passwords
        companies = [
            {
                'company_name': 'InnovateTech',
                'username': 'innovatetech',
                'password': 'Innovate123',
                'email': 'contact@innovatetech.com',
            },
            {
                'company_name': 'GrowthHub',
                'username': 'growthhub',
                'password': 'Growth123',
                'email': 'contact@growthhub.com',
            },
            {
                'company_name': 'Creative Studio',
                'username': 'creativestudio',
                'password': 'Creative123',
                'email': 'contact@creativestudio.com',
            },
            {
                'company_name': 'DataDriven Analytics',
                'username': 'datadriven',
                'password': 'Data123',
                'email': 'contact@datadriven.com',
            },
            {
                'company_name': 'TechCorp Inc.',
                'username': 'techcorp',
                'password': 'TechCorp123',
                'email': 'contact@techcorp.com',
            },
        ]

        for company_data in companies:
            company_name = company_data['company_name']
            username = company_data['username']
            password = company_data['password']
            email = company_data['email']

            # Check if user already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'User {username} already exists. Skipping...')
                )
                continue

            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=company_name.split()[0],  # First word of company name
                last_name=company_name.split()[-1] if len(company_name.split()) > 1 else '',  # Last word
            )

            # Create user profile with user_type='employer'
            profile = UserProfile.objects.create(
                user=user,
                user_type='employer',
                company=company_name,
            )

            # Update existing jobs to be associated with this employer
            jobs_updated = Job.objects.filter(
                company=company_name,
                created_by__is_staff=True  # Jobs created by admin
            ).update(created_by=user)

            self.stdout.write(
                self.style.SUCCESS(
                    f'+ Created employer account for {company_name}\n'
                    f'  Username: {username}\n'
                    f'  Password: {password}\n'
                    f'  Email: {email}\n'
                    f'  Jobs transferred: {jobs_updated}\n'
                )
            )

        self.stdout.write(
            self.style.SUCCESS('\n=== Employer accounts created successfully! ===\n')
        )
