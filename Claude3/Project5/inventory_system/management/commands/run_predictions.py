from django.core.management.base import BaseCommand
from inventory_system.services.predictor import DemandPredictor


class Command(BaseCommand):
    help = 'Run AI predictions for all products and save to database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--safety-margin',
            type=float,
            default=0.20,
            help='Safety margin percentage (default: 0.20 = 20%%)'
        )

    def handle(self, *args, **options):
        safety_margin = options['safety_margin']

        self.stdout.write('Initializing AI Demand Prediction Engine...')
        predictor = DemandPredictor(safety_margin=safety_margin)

        self.stdout.write('Analyzing historical sales data...')
        predictions = predictor.predict_all_products()

        self.stdout.write(f'Generating predictions for {len(predictions)} products...')

        # Save predictions to database
        created_count = predictor.save_predictions()

        self.stdout.write(self.style.SUCCESS(f'\n[*] Successfully created {created_count} predictions!'))

        # Show summary
        low_stock = sum(1 for p in predictions if p['status'] == 'low_stock')
        optimal = sum(1 for p in predictions if p['status'] == 'optimal')
        overstock = sum(1 for p in predictions if p['status'] == 'overstock')

        self.stdout.write('\nPrediction Summary:')
        self.stdout.write(f'  Low Stock: {low_stock}')
        self.stdout.write(f'  Optimal: {optimal}')
        self.stdout.write(f'  Overstock: {overstock}')
