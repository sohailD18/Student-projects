"""
Django management command to train the fraud detection model.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
import os

from transactions.models import Transaction, ModelMetrics, AuditLog
from transactions.ml_engine import get_model, save_trained_model_metrics
from transactions.utils import prepare_training_data


class Command(BaseCommand):
    help = 'Train the fraud detection model on existing transaction data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model-type',
            type=str,
            default='random_forest',
            choices=['isolation_forest', 'random_forest'],
            help='Type of model to train',
        )
        parser.add_argument(
            '--save-model',
            action='store_true',
            help='Save the trained model to disk',
        )
        parser.add_argument(
            '--min-samples',
            type=int,
            default=100,
            help='Minimum number of samples required for training',
        )

    def handle(self, *args, **options):
        model_type = options['model_type']
        save_model = options['save_model']
        min_samples = options['min_samples']

        self.stdout.write(f'Training {model_type} model...')

        # Check if we have enough data
        total_transactions = Transaction.objects.count()
        if total_transactions < min_samples:
            self.stdout.write(
                self.style.ERROR(
                    f'Not enough data for training. '
                    f'Found {total_transactions} transactions, '
                    f'need at least {min_samples}. '
                    f'Run: python manage.py generate_transactions --count {min_samples}'
                )
            )
            return

        # Prepare training data
        self.stdout.write('Preparing training data...')
        X, y = prepare_training_data(Transaction.objects.all())

        if len(X) == 0:
            self.stdout.write(
                self.style.ERROR('Failed to prepare training data')
            )
            return

        self.stdout.write(f'Training samples: {len(X)}')

        # Get or create model
        model = get_model()
        model.model_type = model_type
        model.create_model()

        # Train model
        self.stdout.write('Training model...')
        if model_type == 'isolation_forest':
            metrics = model.train(X)
        else:
            metrics = model.train(X, y)

        # Display metrics
        self.stdout.write(self.style.SUCCESS('\n=== Training Results ==='))
        for key, value in metrics.items():
            if key != 'confusion_matrix':
                if isinstance(value, float):
                    self.stdout.write(f'{key}: {value:.4f}')
                else:
                    self.stdout.write(f'{key}: {value}')

        if 'confusion_matrix' in metrics:
            cm = metrics['confusion_matrix']
            self.stdout.write('\nConfusion Matrix:')
            self.stdout.write(f"  True Negatives:  {cm['true_negatives']}")
            self.stdout.write(f"  False Positives: {cm['false_positives']}")
            self.stdout.write(f"  False Negatives: {cm['false_negatives']}")
            self.stdout.write(f"  True Positives:  {cm['true_positives']}")

        # Save metrics to database
        self.stdout.write('\nSaving metrics to database...')
        model_metrics = save_trained_model_metrics(metrics, model.version)
        self.stdout.write(
            self.style.SUCCESS(f'Model metrics saved with ID: {model_metrics.id}')
        )

        # Save model to disk if requested
        if save_model:
            model_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'models'
            )
            model.save(model_dir)
            self.stdout.write(
                self.style.SUCCESS(f'Model saved to: {model_dir}')
            )

        # Create audit log
        AuditLog.objects.create(
            action='model_trained',
            entity_type='model',
            entity_id=model_metrics.id,
            details=metrics
        )

        # Update existing transactions with predictions
        self.stdout.write('\nUpdating existing transactions with predictions...')
        updated_count = 0
        error_count = 0

        for transaction in Transaction.objects.all()[:1000]:  # Limit to avoid too long
            try:
                transaction_data = {
                    'amount': float(transaction.amount),
                    'transaction_type': transaction.transaction_type,
                    'merchant_category': transaction.merchant_category,
                    'country': transaction.country,
                    'timestamp': transaction.timestamp,
                }

                prediction = model.predict(transaction_data)
                transaction.is_fraud = prediction['is_fraud']
                transaction.risk_score = prediction['risk_score']
                transaction.is_flagged = transaction.risk_score > 0.5

                if transaction.is_fraud:
                    from transactions.ml_engine import get_fraud_reasons
                    transaction.fraud_reason = get_fraud_reasons(
                        transaction_data,
                        transaction.risk_score
                    )

                transaction.save()
                updated_count += 1

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Error updating transaction: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nTraining complete! Updated {updated_count} transactions '
                f'({error_count} errors)'
            )
        )
