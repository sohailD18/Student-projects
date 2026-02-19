from django.core.management.base import BaseCommand
from jobs.models import Job
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Transfer jobs from admin/demo users to employer accounts based on company name'

    def handle(self, *args, **options):
        # Mapping of company names to employer usernames
        companies_to_users = {
            'InnovateTech': 'innovatetech',
            'GrowthHub': 'growthhub',
            'Creative Studio': 'creativestudio',
            'DataDriven Analytics': 'datadriven',
            'TechCorp Inc.': 'techcorp',
        }

        self.stdout.write('=== Transferring Jobs to Employer Accounts ===\n')

        transferred = 0
        not_found = []

        for job in Job.objects.all():
            if job.company in companies_to_users:
                username = companies_to_users[job.company]
                try:
                    new_owner = User.objects.get(username=username)
                    old_owner = job.created_by
                    job.created_by = new_owner
                    job.save()
                    transferred += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'+ Transferred: {job.title} ({job.company})\n'
                            f'  From: {old_owner.username}\n'
                            f'  To: {new_owner.username}\n'
                        )
                    )
                except User.DoesNotExist:
                    not_found.append(f'{job.company} -> {username}')
                    self.stdout.write(
                        self.style.WARNING(f'User {username} not found for {job.company}')
                    )

        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal jobs transferred: {transferred}\n')
        )

        if not_found:
            self.stdout.write(
                self.style.WARNING(f'\nUsers not found: {len(not_found)}\n')
            )
            for item in not_found:
                self.stdout.write(f'  - {item}')
