from django.core.management.base import BaseCommand
from jobs.models import JobCategory


class Command(BaseCommand):
    help = 'Create initial job categories'

    def handle(self, *args, **kwargs):
        categories = [
            {'name': 'Software Development', 'description': 'Programming and software engineering roles'},
            {'name': 'Data Science', 'description': 'Data analysis, machine learning, and AI roles'},
            {'name': 'Design', 'description': 'UI/UX, graphic design, and creative roles'},
            {'name': 'Marketing', 'description': 'Digital marketing, content, and branding roles'},
            {'name': 'Sales', 'description': 'Sales and business development roles'},
            {'name': 'Finance', 'description': 'Accounting, finance, and investment roles'},
            {'name': 'Human Resources', 'description': 'HR, recruitment, and people management'},
            {'name': 'Engineering', 'description': 'Civil, mechanical, and electrical engineering'},
            {'name': 'Customer Service', 'description': 'Support and customer success roles'},
            {'name': 'Management', 'description': 'Project and product management roles'},
        ]

        created_count = 0
        for cat_data in categories:
            category, created = JobCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Category already exists: {category.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created {created_count} new categories!')
        )
