from django.core.management.base import BaseCommand
from agriSense.models import Crop, Season, SoilData, YieldRecord


class Command(BaseCommand):
    help = 'Seed the database with dummy data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        # Create Seasons first (needed for crop relationships)
        seasons_data = [
            {'name': 'Spring', 'months': 'March, April, May'},
            {'name': 'Summer', 'months': 'June, July, August'},
            {'name': 'Autumn', 'months': 'September, October, November'},
            {'name': 'Winter', 'months': 'December, January, February'},
            {'name': 'Monsoon', 'months': 'June, July, August, September'},
            {'name': 'Kharif', 'months': 'July, October'},
            {'name': 'Rabi', 'months': 'October, March'},
        ]

        seasons = {}
        seasons_created = 0
        for season_data in seasons_data:
            season, created = Season.objects.get_or_create(
                name=season_data['name'],
                defaults={'months': season_data['months']}
            )
            seasons[season.name] = season
            if created:
                seasons_created += 1
                self.stdout.write(f'  Created season: {season.name}')

        # Create Crops with suitability information
        crops_data = [
            {
                'name': 'Wheat',
                'type': 'cereals',
                'duration': 120,
                'soil_types': ['loamy', 'clay', 'silty'],
                'seasons': ['Winter', 'Rabi']
            },
            {
                'name': 'Rice',
                'type': 'cereals',
                'duration': 150,
                'soil_types': ['clay', 'loamy'],
                'seasons': ['Summer', 'Monsoon', 'Kharif']
            },
            {
                'name': 'Maize',
                'type': 'cereals',
                'duration': 110,
                'soil_types': ['loamy', 'silty'],
                'seasons': ['Spring', 'Summer', 'Kharif']
            },
            {
                'name': 'Tomato',
                'type': 'vegetables',
                'duration': 90,
                'soil_types': ['loamy', 'sandy'],
                'seasons': ['Spring', 'Autumn']
            },
            {
                'name': 'Potato',
                'type': 'vegetables',
                'duration': 100,
                'soil_types': ['sandy', 'loamy'],
                'seasons': ['Spring', 'Autumn', 'Winter']
            },
            {
                'name': 'Onion',
                'type': 'vegetables',
                'duration': 120,
                'soil_types': ['loamy', 'clay'],
                'seasons': ['Winter', 'Rabi']
            },
            {
                'name': 'Apple',
                'type': 'fruits',
                'duration': 200,
                'soil_types': ['loamy', 'silty'],
                'seasons': ['Spring', 'Autumn']
            },
            {
                'name': 'Mango',
                'type': 'fruits',
                'duration': 180,
                'soil_types': ['sandy', 'loamy'],
                'seasons': ['Summer', 'Spring']
            },
            {
                'name': 'Banana',
                'type': 'fruits',
                'duration': 365,
                'soil_types': ['loamy', 'clay'],
                'seasons': ['Summer', 'Monsoon']
            },
            {
                'name': 'Beans',
                'type': 'legumes',
                'duration': 75,
                'soil_types': ['loamy', 'sandy'],
                'seasons': ['Spring', 'Autumn']
            },
            {
                'name': 'Lentils',
                'type': 'legumes',
                'duration': 90,
                'soil_types': ['loamy', 'silty'],
                'seasons': ['Winter', 'Rabi']
            },
            {
                'name': 'Soybean',
                'type': 'legumes',
                'duration': 100,
                'soil_types': ['loamy', 'clay'],
                'seasons': ['Summer', 'Kharif']
            },
            {
                'name': 'Cotton',
                'type': 'cash_crops',
                'duration': 180,
                'soil_types': ['loamy', 'clay'],
                'seasons': ['Summer', 'Kharif']
            },
            {
                'name': 'Sugarcane',
                'type': 'cash_crops',
                'duration': 365,
                'soil_types': ['loamy', 'clay', 'silty'],
                'seasons': ['Summer', 'Monsoon', 'Spring']
            },
            {
                'name': 'Coffee',
                'type': 'cash_crops',
                'duration': 240,
                'soil_types': ['loamy', 'silty'],
                'seasons': ['Spring', 'Autumn']
            },
        ]

        crops = {}
        crops_created = 0
        for crop_data in crops_data:
            soil_types = crop_data.pop('soil_types')
            season_names = crop_data.pop('seasons')

            crop, created = Crop.objects.get_or_create(
                name=crop_data['name'],
                defaults=crop_data
            )

            # Update suitable soil types
            if created or not crop.suitable_soil_types:
                crop.suitable_soil_types = soil_types
                crop.save()

            # Add suitable seasons
            for season_name in season_names:
                if season_name in seasons:
                    crop.suitable_seasons.add(seasons[season_name])

            crops[crop.name] = crop
            if created:
                crops_created += 1
                self.stdout.write(f'  Created crop: {crop.name}')

        # Create Soil Data samples
        soil_data_samples = [
            {'ph': 6.5, 'moisture': 45.0, 'type': 'loamy'},
            {'ph': 7.2, 'moisture': 55.0, 'type': 'clay'},
            {'ph': 5.8, 'moisture': 35.0, 'type': 'sandy'},
            {'ph': 6.8, 'moisture': 60.0, 'type': 'silty'},
            {'ph': 4.5, 'moisture': 70.0, 'type': 'peaty'},
        ]

        soil_created = 0
        for soil_data in soil_data_samples:
            soil, created = SoilData.objects.get_or_create(
                ph=soil_data['ph'],
                moisture=soil_data['moisture'],
                type=soil_data['type'],
            )
            if created:
                soil_created += 1
                self.stdout.write(f'  Created soil data: {soil.type} (pH: {soil.ph})')

        # Create Yield Records
        yield_data = [
            {'crop': crops.get('Wheat'), 'year': 2021, 'quantity': 4.5},
            {'crop': crops.get('Wheat'), 'year': 2022, 'quantity': 4.8},
            {'crop': crops.get('Wheat'), 'year': 2023, 'quantity': 5.2},
            {'crop': crops.get('Rice'), 'year': 2021, 'quantity': 6.0},
            {'crop': crops.get('Rice'), 'year': 2022, 'quantity': 6.3},
            {'crop': crops.get('Rice'), 'year': 2023, 'quantity': 5.9},
            {'crop': crops.get('Maize'), 'year': 2021, 'quantity': 3.8},
            {'crop': crops.get('Maize'), 'year': 2022, 'quantity': 4.1},
            {'crop': crops.get('Maize'), 'year': 2023, 'quantity': 4.5},
        ]

        yields_created = 0
        for yield_record in yield_data:
            if yield_record['crop']:
                record, created = YieldRecord.objects.get_or_create(
                    crop=yield_record['crop'],
                    year=yield_record['year'],
                    defaults={'quantity': yield_record['quantity']}
                )
                if created:
                    yields_created += 1
                    self.stdout.write(
                        f'  Created yield record: {record.crop.name} - {record.year}: {record.quantity} tons/ha'
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully seeded database:\n'
                f'  - {crops_created} crops created\n'
                f'  - {seasons_created} seasons created\n'
                f'  - {soil_created} soil data entries created\n'
                f'  - {yields_created} yield records created'
            )
        )
