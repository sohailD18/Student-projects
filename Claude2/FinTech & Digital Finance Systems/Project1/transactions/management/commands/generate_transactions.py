"""
Django management command to generate synthetic transaction data.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random
import string
from decimal import Decimal

from transactions.models import Transaction, FraudAlert, AuditLog
from transactions.ml_engine import get_model, get_fraud_reasons


class Command(BaseCommand):
    help = 'Generate synthetic transaction data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=100,
            help='Number of transactions to generate',
        )
        parser.add_argument(
            '--fraud-ratio',
            type=float,
            default=0.1,
            help='Ratio of fraudulent transactions (0.0 to 1.0)',
        )

    def handle(self, *args, **options):
        count = options['count']
        fraud_ratio = options['fraud_ratio']

        self.stdout.write(f'Generating {count} synthetic transactions...')

        # Data sources
        transaction_types = ['purchase', 'withdrawal', 'transfer', 'deposit', 'payment']
        merchants = [
            ('Amazon', 'online_services'),
            ('Walmart', 'electronics'),
            ('Target', 'clothing'),
            ('Starbucks', 'food'),
            ('Shell Gas Station', 'gas_station'),
            ('Delta Airlines', 'travel'),
            ('Netflix', 'online_services'),
            ('Best Buy', 'electronics'),
            ('Whole Foods', 'food'),
            ('Marriott Hotels', 'travel'),
        ]
        countries = ['US', 'CA', 'GB', 'AU', 'DE', 'FR', 'JP', 'IN', 'BR', 'MX']
        cities = {
            'US': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'],
            'CA': ['Toronto', 'Vancouver', 'Montreal', 'Calgary'],
            'GB': ['London', 'Manchester', 'Birmingham', 'Glasgow'],
            'AU': ['Sydney', 'Melbourne', 'Brisbane', 'Perth'],
            'DE': ['Berlin', 'Munich', 'Hamburg', 'Frankfurt'],
            'FR': ['Paris', 'Lyon', 'Marseille', 'Nice'],
            'JP': ['Tokyo', 'Osaka', 'Kyoto', 'Yokohama'],
            'IN': ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad'],
            'BR': ['Sao Paulo', 'Rio de Janeiro', 'Brasilia', 'Salvador'],
            'MX': ['Mexico City', 'Guadalajara', 'Monterrey', 'Cancun'],
        }

        # Get or train model
        model = get_model()

        generated_count = 0
        fraud_count = 0

        for i in range(count):
            # Generate transaction data
            transaction_type = random.choice(transaction_types)
            merchant_name, merchant_category = random.choice(merchants)
            country = random.choices(countries, weights=[50, 20, 10, 5, 3, 3, 3, 2, 2, 2])[0]
            city = random.choice(cities[country])

            # Generate amount (with some outliers)
            if random.random() < 0.05:  # 5% chance of very large amount
                amount = Decimal(str(random.uniform(1000, 5000)))
            else:
                amount = Decimal(str(random.uniform(10, 500)))

            # Generate timestamp (last 30 days)
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 24)
            timestamp = timezone.now() - timedelta(days=days_ago, hours=hours_ago)

            # Generate transaction ID
            transaction_id = f"TXN{''.join(random.choices(string.digits, k=12))}"

            # Generate account and card info
            account_id = f"ACC{random.randint(100000, 999999)}"
            card_number_last4 = ''.join(random.choices(string.digits, k=4))

            # Generate IP address
            ip_address = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"

            # Create transaction
            transaction = Transaction.objects.create(
                transaction_id=transaction_id,
                transaction_type=transaction_type,
                amount=amount,
                currency='USD',
                location=f"{city}, {country}",
                country=country,
                city=city,
                ip_address=ip_address,
                merchant=merchant_name,
                merchant_category=merchant_category,
                account_id=account_id,
                card_number_last4=card_number_last4,
                timestamp=timestamp,
                device_id=f"DEV{random.randint(10000, 99999)}",
                browser=random.choice(['Chrome', 'Firefox', 'Safari', 'Edge']),
                os=random.choice(['Windows', 'MacOS', 'Linux', 'iOS', 'Android']),
            )

            # Make prediction if model is trained
            if model.is_trained:
                # Prepare features for prediction
                transaction_data = {
                    'amount': float(amount),
                    'transaction_type': transaction_type,
                    'merchant_category': merchant_category,
                    'country': country,
                    'timestamp': timestamp,
                }

                try:
                    prediction = model.predict(transaction_data)
                    transaction.is_fraud = prediction['is_fraud']
                    transaction.risk_score = prediction['risk_score']
                    transaction.is_flagged = transaction.risk_score > 0.5

                    if transaction.is_fraud:
                        transaction.fraud_reason = get_fraud_reasons(
                            transaction_data,
                            transaction.risk_score
                        )

                    # Create fraud alert for high-risk transactions
                    if transaction.risk_score > 0.6:
                        FraudAlert.objects.create(
                            transaction=transaction,
                            alert_type='high_risk_detection',
                            status='new',
                            description=f"High risk transaction detected: {transaction.fraud_reason}",
                            risk_score=transaction.risk_score,
                        )

                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'Prediction error: {e}')
                    )

            else:
                # Simulate fraud based on fraud_ratio if model not trained
                is_fraud = random.random() < fraud_ratio
                transaction.is_fraud = is_fraud
                transaction.risk_score = random.uniform(0.7, 1.0) if is_fraud else random.uniform(0.0, 0.3)
                transaction.is_flagged = transaction.risk_score > 0.5

                if is_fraud:
                    transaction.fraud_reason = "Synthetic fraud for testing"

                    FraudAlert.objects.create(
                        transaction=transaction,
                        alert_type='synthetic_fraud',
                        status='new',
                        description="Synthetic fraud transaction for testing",
                        risk_score=transaction.risk_score,
                    )

            transaction.save()

            # Create audit log
            AuditLog.objects.create(
                action='transaction_created',
                entity_type='transaction',
                entity_id=transaction.transaction_id,
                details={
                    'amount': str(amount),
                    'is_fraud': transaction.is_fraud,
                    'risk_score': transaction.risk_score,
                }
            )

            generated_count += 1
            if transaction.is_fraud:
                fraud_count += 1

            if generated_count % 100 == 0:
                self.stdout.write(f'Generated {generated_count} transactions...')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully generated {generated_count} transactions '
                f'({fraud_count} fraudulent)'
            )
        )
