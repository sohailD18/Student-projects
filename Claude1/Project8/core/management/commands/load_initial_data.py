from django.core.management.base import BaseCommand
from core.models import IncidentCategory


class Command(BaseCommand):
    help = 'Load initial incident categories'

    def handle(self, *args, **kwargs):
        categories = [
            {
                'name': 'Theft',
                'description': 'Reports of stolen items, pickpocketing, burglary, or robbery',
                'icon': 'bi-bag',
                'color': '#6f42c1'
            },
            {
                'name': 'Assault',
                'description': 'Physical attacks, fights, or violent behavior',
                'icon': 'bi-exclamation-triangle-fill',
                'color': '#dc3545'
            },
            {
                'name': 'Vandalism',
                'description': 'Property damage, graffiti, or destruction of public/private property',
                'icon': 'bi-pencil-square',
                'color': '#fd7e14'
            },
            {
                'name': 'Suspicious Activity',
                'description': 'Unusual or suspicious behavior that may warrant attention',
                'icon': 'bi-eye-fill',
                'color': '#ffc107'
            },
            {
                'name': 'Traffic Hazard',
                'description': 'Road accidents, broken traffic lights, potholes, or unsafe driving conditions',
                'icon': 'bi-car-front-fill',
                'color': '#0dcaf0'
            },
            {
                'name': 'Fire',
                'description': 'Fire incidents, smoke reports, or fire hazards',
                'icon': 'bi-fire',
                'color': '#dc3545'
            },
            {
                'name': 'Medical Emergency',
                'description': 'Health emergencies, injuries, or need for medical assistance',
                'icon': 'bi-heart-pulse-fill',
                'color': '#d63384'
            },
            {
                'name': 'Natural Disaster',
                'description': 'Floods, storms, earthquakes, or other natural disasters',
                'icon': 'bi-cloud-lightning-rain-fill',
                'color': '#6c757d'
            },
            {
                'name': 'Missing Person',
                'description': 'Reports of missing individuals or Amber alerts',
                'icon': 'bi-person-exclamation',
                'color': '#0d6efd'
            },
            {
                'name': 'Animal Issue',
                'description': 'Stray animals, aggressive animals, or animal attacks',
                'icon': 'bi-emoji-frown-fill',
                'color': '#20c997'
            },
            {
                'name': 'Public Disturbance',
                'description': 'Noise complaints, public intoxication, or disruptive behavior',
                'icon': 'bi-volume-up-fill',
                'color': '#6f42c1'
            },
            {
                'name': 'Utility Issue',
                'description': 'Power outages, water main breaks, gas leaks, or other utility problems',
                'icon': 'bi-lightning-charge-fill',
                'color': '#ffc107'
            },
        ]

        created_count = 0
        updated_count = 0

        for category_data in categories:
            category, created = IncidentCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={
                    'description': category_data['description'],
                    'icon': category_data['icon'],
                    'color': category_data['color']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.name}')
                )
            else:
                # Update existing category
                category.description = category_data['description']
                category.icon = category_data['icon']
                category.color = category_data['color']
                category.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated category: {category.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSummary: {created_count} categories created, {updated_count} categories updated.'
            )
        )
