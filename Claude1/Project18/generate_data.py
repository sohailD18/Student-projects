import os
import random
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FinShield.settings')
import django
django.setup()

from detector.models import (
    Transaction, Alert, UserProfile, FraudRule, FraudCase,
    CaseNote, CaseEvidence, ComplianceReport, SuspiciousActivityReport,
    AuditLog, NotificationTemplate, NotificationPreference, SpendingPattern
)
from detector.utils import (
    calculate_risk, AdvancedRiskScorer, SpendingPatternAnalyzer,
    log_audit_event
)


# Sample data
USERS = [
    'alice@example.com', 'bob@test.com', 'charlie@mail.com',
    'david@web.com', 'eve@domain.com', 'frank@company.com',
    'grace@tech.com', 'henry@corp.com'
]
MERCHANTS = [
    'Amazon', 'Walmart', 'Target', 'Best Buy', 'Netflix',
    'Starbucks', 'Shell', 'Apple Store', 'Crypto Exchange',
    'Jewelry Store', 'Electronics World', 'Luxury Brands',
    'Gourmet Market', 'Travel Booking', 'Online Gaming'
]
LOCATIONS = [
    'New York', 'California', 'Texas', 'Florida', 'Washington',
    'Nevada', 'Illinois', 'Foreign'
]
DEVICE_IDS = [f'device_{i:04d}' for i in range(1, 21)]
IP_ADDRESSES = [
    f'192.168.{i}.{j}' for i in range(1, 256) for j in range(1, 256)
]
ANALYSTS = ['analyst1@company.com', 'analyst2@company.com', 'senior.analyst@company.com', 'manager@company.com']


def create_default_rules():
    """Create default fraud detection rules"""
    rules = [
        {
            'name': 'Large Amount Transaction',
            'rule_type': 'amount_threshold',
            'description': 'Flag transactions above $10,000',
            'config': {'threshold': 10000, 'risk_points': 50},
            'weight': 50
        },
        {
            'name': 'Very Large Amount Transaction',
            'rule_type': 'amount_threshold',
            'description': 'Flag transactions above $25,000',
            'config': {'threshold': 25000, 'risk_points': 80},
            'weight': 80
        },
        {
            'name': 'Unusual Time Activity',
            'rule_type': 'time_based',
            'description': 'Flag transactions between 1 AM and 5 AM',
            'config': {'start_hour': 1, 'end_hour': 5, 'risk_points': 30},
            'weight': 30
        },
        {
            'name': 'Foreign Transaction',
            'rule_type': 'location_based',
            'description': 'Flag transactions from foreign locations',
            'config': {'suspicious_locations': ['Foreign'], 'risk_points': 40},
            'weight': 40
        },
        {
            'name': 'High Velocity Transactions',
            'rule_type': 'velocity_check',
            'description': 'Flag users with more than 3 transactions in 10 minutes',
            'config': {'time_window_minutes': 10, 'max_transactions': 3, 'risk_points': 60},
            'weight': 60
        },
        {
            'name': 'Very High Velocity Transactions',
            'rule_type': 'velocity_check',
            'description': 'Flag users with more than 5 transactions in 5 minutes',
            'config': {'time_window_minutes': 5, 'max_transactions': 5, 'risk_points': 85},
            'weight': 85
        },
        {
            'name': 'Spending Pattern Deviation',
            'rule_type': 'pattern_based',
            'description': 'Flag transactions that deviate significantly from user patterns',
            'config': {'max_deviation': 3.0, 'check_new_merchant': True, 'risk_points': 40, 'merchant_risk_points': 20},
            'weight': 45
        },
    ]

    for rule_data in rules:
        FraudRule.objects.get_or_create(
            name=rule_data['name'],
            defaults={
                'rule_type': rule_data['rule_type'],
                'description': rule_data['description'],
                'rule_config': rule_data['config'],
                'weight': rule_data['weight'],
                'is_active': True
            }
        )

    print("[OK] Default fraud rules created")


def create_notification_templates():
    """Create default notification templates"""
    templates = [
        {
            'name': 'Critical Alert Email',
            'channel': 'email',
            'subject_template': 'CRITICAL: Fraud Alert - Risk Score {risk_score}',
            'body_template': 'A critical fraud alert has been triggered. Risk Score: {risk_score}. Transaction ID: {transaction_id}.'
        },
        {
            'name': 'High Alert Email',
            'channel': 'email',
            'subject_template': 'ALERT: Suspicious Activity Detected',
            'body_template': 'Suspicious activity has been detected. Risk Score: {risk_score}. Please review immediately.'
        },
        {
            'name': 'Medium Alert Email',
            'channel': 'email',
            'subject_template': 'Medium Risk Alert - Review Required',
            'body_template': 'A medium risk transaction requires your review. Risk Score: {risk_score}.'
        },
        {
            'name': 'Alert SMS',
            'channel': 'sms',
            'body_template': 'Fraud Alert: Risk score {risk_score} for transaction {transaction_id}. Please review.'
        },
    ]

    for tmpl in templates:
        NotificationTemplate.objects.get_or_create(
            name=tmpl['name'],
            defaults={
                'channel': tmpl['channel'],
                'subject_template': tmpl.get('subject_template', ''),
                'body_template': tmpl['body_template'],
                'is_active': True
            }
        )

    print("[OK] Notification templates created")


def create_notification_preferences():
    """Create notification preferences for demo users"""
    for user in USERS:
        NotificationPreference.objects.get_or_create(
            user=user,
            defaults={
                'email_enabled': True,
                'sms_enabled': random.choice([True, False]),
                'phone_number': f'+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}',
                'email_address': user,
                'notify_on_low_severity': False,
                'notify_on_medium_severity': True,
                'notify_on_high_severity': True,
                'notify_on_critical_severity': True,
                'digest_mode': random.choice([True, False]),
                'digest_frequency': random.choice(['hourly', 'daily', 'weekly'])
            }
        )

    print("[OK] Notification preferences created")


def generate_transaction_with_risk(user_idx=None, risk_level='random'):
    """Generate a transaction with specific risk profile"""
    if user_idx is None:
        user = random.choice(USERS)
    else:
        user = USERS[user_idx % len(USERS)]

    # Generate transaction based on risk level
    if risk_level == 'high' or (risk_level == 'random' and random.random() < 0.15):
        # High-risk transaction
        location = random.choice(['Foreign', 'Foreign', 'Foreign', 'Nevada'])
        amount = random.uniform(8000, 35000)
        merchant = random.choice(['Crypto Exchange', 'Jewelry Store', 'Luxury Brands'])
        hour = random.choice([1, 2, 3, 4, 5, 23])
        txn_type = random.choice(['transfer', 'withdrawal'])

    elif risk_level == 'medium' or (risk_level == 'random' and random.random() < 0.30):
        # Medium-risk transaction
        location = random.choice(['New York', 'California', 'Texas'])
        amount = random.uniform(3000, 12000)
        merchant = random.choice(['Electronics World', 'Travel Booking', 'Online Gaming'])
        hour = random.choice([0, 1, 2, 3, 4, 5, 22, 23])
        txn_type = random.choice(['purchase', 'transfer'])

    elif risk_level == 'low' or (risk_level == 'random' and random.random() < 0.55):
        # Low-risk transaction
        location = random.choice(['New York', 'California', 'Texas', 'Florida'])
        amount = random.uniform(100, 2000)
        merchant = random.choice(['Amazon', 'Walmart', 'Target', 'Best Buy'])
        hour = random.choice([9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20])
        txn_type = 'purchase'

    else:
        # Safe transaction
        location = random.choice(['New York', 'California', 'Texas', 'Florida'])
        amount = random.uniform(10, 500)
        merchant = random.choice(['Starbucks', 'Netflix', 'Shell', 'Gourmet Market'])
        hour = random.choice([9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20])
        txn_type = 'purchase'

    # Create timestamp
    days_ago = random.randint(0, 60)
    timestamp = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
    timestamp = timestamp.replace(hour=hour, minute=random.randint(0, 59))

    # Create transaction
    transaction = Transaction.objects.create(
        user=user,
        amount=round(amount, 2),
        location=location,
        merchant=merchant,
        timestamp=timestamp,
        transaction_type=txn_type,
        device_id=random.choice(DEVICE_IDS),
        ip_address=random.choice(IP_ADDRESSES)
    )

    # Calculate risk using advanced scorer
    scorer = AdvancedRiskScorer()
    risk_score, risk_factors, severity = scorer.calculate_comprehensive_risk(transaction)
    transaction.risk_score = risk_score

    # Update status based on risk
    if risk_score >= 80:
        transaction.status = 'fraud'
    elif risk_score >= 50:
        transaction.status = 'suspicious'
    else:
        transaction.status = 'safe'
    transaction.save()

    # Create alert if risk > 40
    alert = None
    if risk_score > 40:
        alert = Alert.objects.create(
            transaction=transaction,
            risk_score=risk_score,
            severity=severity,
            rule_triggered=f"High risk detected: Score {risk_score} ({severity})",
            description=f"Risk factors detected"
        )

        # Log the alert
        log_audit_event(
            action_type='alert_triggered',
            entity_type='Alert',
            entity_id=alert.id,
            actor='system',
            changes={'risk_score': risk_score, 'severity': severity}
        )

    # Log the transaction
    log_audit_event(
        action_type='transaction_created',
        entity_type='Transaction',
        entity_id=transaction.id,
        actor='system',
        changes={'amount': float(amount), 'status': transaction.status, 'risk_score': risk_score}
    )

    return transaction, risk_score, severity, alert


def create_demo_fraud_cases():
    """Create demo fraud cases"""
    # Delete existing demo fraud cases and related data
    print("  Cleaning up existing demo cases...")
    CaseNote.objects.all().delete()
    CaseEvidence.objects.all().delete()
    FraudCase.objects.all().delete()

    case_count = 0

    # First, ensure we have enough high-risk alerts by creating specific high-risk transactions
    print("  Generating additional high-risk transactions for cases...")
    for i in range(15):
        user = USERS[i % len(USERS)]
        alert = generate_transaction_with_risk(user_idx=i, risk_level='high')[3]

    # Get high-risk alerts to create cases from
    high_risk_alerts = Alert.objects.filter(
        risk_score__gte=50,
        fraud_cases__isnull=True
    )[:12]

    for alert in high_risk_alerts:
        # Generate unique case number with timestamp and random suffix
        import time
        timestamp = int(time.time())
        case_number = 'FC-' + datetime.now().strftime('%Y%m%d') + '-' + f'{case_count + 1:04d}' + '-' + f'{timestamp % 10000:04d}'

        # Determine priority based on severity
        priority_map = {'critical': 'p1', 'high': 'p2', 'medium': 'p3', 'low': 'p4'}
        priority = priority_map.get(alert.severity, 'p3')

        # Vary the case descriptions
        descriptions = [
            f"Multiple high-value transactions detected from {alert.transaction.location}",
            f"Unusual spending pattern detected for user {alert.transaction.user}",
            f"Foreign transaction with high risk score ({alert.risk_score})",
            f"Suspicious merchant activity: {alert.transaction.merchant}",
            f"Liquid transfer outside normal business hours",
            f"High-velocity transaction pattern detected"
        ]

        # Create case
        case = FraudCase.objects.create(
            case_number=case_number,
            title=random.choice([
                f"Potential Fraud - {alert.transaction.user}",
                f"Suspicious Activity Pattern - {alert.transaction.merchant}",
                f"Anomalous Transaction - {alert.transaction.location}",
                f"High-Risk Transfer - Case #{case_count + 1}"
            ]),
            description=random.choice(descriptions),
            priority=priority,
            status=random.choice(['open', 'open', 'investigating', 'investigating', 'evidence_collection', 'pending_review', 'closed']),
            assigned_to=random.choice(ANALYSTS),
            suspected_amount=alert.transaction.amount,
            confirmed_fraud_amount=random.choice([0, 0, float(alert.transaction.amount), float(alert.transaction.amount) * 0.5, float(alert.transaction.amount) * 0.75])
        )

        # Link transaction and alert
        case.related_transactions.add(alert.transaction)
        case.related_alerts.add(alert)

        # Add additional related transactions for some cases
        if case_count < 6:  # First 6 cases get multiple transactions
            user_transactions = Transaction.objects.filter(
                user=alert.transaction.user,
                status__in=['suspicious', 'fraud']
            ).exclude(id=alert.transaction.id)[:3]

            for txn in user_transactions:
                case.related_transactions.add(txn)
                case.suspected_amount += txn.amount

        case.save()

        # Add notes with timeline
        note_timeline = [
            (1, "Case opened and assigned for investigation."),
            (2, "Initial analysis of transaction patterns completed."),
            (3, "Contacted user for verification of transactions."),
            (4, "Analyzing historical transaction data."),
            (5, "Compiling evidence for case file."),
            (6, "Preparing final case report."),
        ]

        num_notes = random.randint(2, 5)
        for i in range(num_notes):
            days_ago = random.randint(1, 30)
            note_timestamp = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))

            note = CaseNote(
                fraud_case=case,
                author=random.choice(ANALYSTS),
                note=f"{note_timeline[min(i, len(note_timeline)-1)][1]} " +
                      random.choice([
                          "Transaction velocity analysis shows unusual pattern.",
                          "Amount exceeds typical user spending by 400%.",
                          "Geolocation analysis shows foreign transaction.",
                          "User confirmed no knowledge of this transaction.",
                          "Merchant category known for high fraud incidence.",
                          "Time of transaction outside normal business hours.",
                          "Device fingerprint matches user's known devices.",
                          "IP address geolocation mismatch with user's registered address."
                      ]),
                is_internal=random.choice([True, False])
            )
            note.created_at = note_timestamp
            note.save()

        # Close some cases with resolution
        if case.status == 'closed':
            days_closed = random.randint(1, 30)
            case.closed_at = datetime.now() - timedelta(days=days_closed)
            case.closed_by = random.choice(ANALYSTS)
            case.resolution_summary = random.choice([
                "Confirmed fraudulent activity. Account has been flagged and blocked.",
                "After investigation, confirmed as unauthorized transaction. Card blocked and reissued.",
                "User verified transaction was legitimate. False positive - case closed.",
                "Insufficient evidence to proceed. Case closed pending additional information.",
                "Transaction traced back to family member. Case resolved as authorized.",
                "Merchant confirmed transaction was valid. No fraud detected."
            ])
            case.save()

            # Log case closure
            log_audit_event(
                action_type='case_updated',
                entity_type='FraudCase',
                entity_id=case.id,
                actor=case.closed_by,
                changes={'status': 'closed'}
            )

        case_count += 1

    print(f"[OK] Created {case_count} demo fraud cases")


def create_demo_sar_reports():
    """Create demo Suspicious Activity Reports"""
    sar_count = 0
    closed_cases = FraudCase.objects.filter(
        status='closed',
        sar__isnull=True
    )[:5]

    for case in closed_cases:
        # Generate SAR number
        sar_number = 'SAR-' + datetime.now().strftime('%Y%m%d') + '-' + f'{sar_count + 1:04d}'

        # Get transaction date range
        transactions = case.related_transactions.all()
        if not transactions:
            continue

        date_range = {
            'start': transactions.order_by('timestamp').first().timestamp.strftime('%Y-%m-%d'),
            'end': transactions.order_by('-timestamp').first().timestamp.strftime('%Y-%m-%d')
        }

        # Create SAR
        sar = SuspiciousActivityReport.objects.create(
            case=case,
            sar_number=sar_number,
            filing_date=datetime.now().date() - timedelta(days=random.randint(1, 60)),
            suspicious_amount=float(case.confirmed_fraud_amount or case.suspected_amount),
            activity_description=random.choice([
                "Multiple high-value electronic fund transfers from foreign jurisdiction with no apparent business purpose.",
                "Structured transactions to avoid currency reporting requirements.",
                "Unusual transaction pattern inconsistent with customer's stated business.",
                "Rapid movement of funds through multiple accounts with no legitimate purpose.",
                "Large cash deposits followed immediately by wire transfers to high-risk jurisdictions."
            ]),
            transaction_dates=date_range,
            involved_parties=list(case.related_transactions.values_list('user', flat=True).distinct()),
            fraud_types=['money_laundering', 'structuring', 'unusual_activity'][sar_count % 3:sar_count % 3 + 1],
            law_enforcement_referral=random.choice([True, False, False]),
            agency_contacted=random.choice(['FBI', 'FinCEN', 'DHS', None, None]),
            filed_by=random.choice(ANALYSTS)
        )

        # Also create a compliance report
        ComplianceReport.objects.create(
            report_type='sar',
            title=f"SAR {sar_number} for Case {case.case_number}",
            description=f"Suspicious Activity Report filed for case {case.case_number}",
            report_data={'sar_number': sar_number, 'case_id': case.case_number},
            date_range_start=datetime.now() - timedelta(days=90),
            date_range_end=datetime.now(),
            generated_by=sar.filed_by
        )

        sar_count += 1

    print(f"[OK] Created {sar_count} Suspicious Activity Reports")


def create_compliance_reports():
    """Create additional compliance reports"""
    report_count = 0

    # Create fraud summary reports for different periods
    periods = [7, 14, 30, 60, 90]

    for days in periods:
        start_date = datetime.now() - timedelta(days=days)
        end_date = datetime.now()

        transactions = Transaction.objects.filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date
        )
        alerts = Alert.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        cases = FraudCase.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )

        report_data = {
            'period_days': days,
            'transactions': {
                'total': transactions.count(),
                'safe': transactions.filter(status='safe').count(),
                'suspicious': transactions.filter(status='suspicious').count(),
                'fraud': transactions.filter(status='fraud').count(),
                'total_amount': sum(float(t.amount) for t in transactions),
                'fraud_amount': sum(float(t.amount) for t in transactions.filter(status='fraud')),
            },
            'alerts': {
                'total': alerts.count(),
                'critical': alerts.filter(severity='critical').count(),
                'high': alerts.filter(severity='high').count(),
                'medium': alerts.filter(severity='medium').count(),
                'low': alerts.filter(severity='low').count(),
            },
            'cases': {
                'total': cases.count(),
                'open': cases.filter(status='open').count(),
                'investigating': cases.filter(status='investigating').count(),
                'closed': cases.filter(status='closed').count(),
            }
        }

        ComplianceReport.objects.create(
            report_type='fraud_summary',
            title=f"Fraud Summary Report - {days} Days",
            description=f"Summary of fraud detection activity over the past {days} days",
            report_data=report_data,
            date_range_start=start_date,
            date_range_end=end_date,
            generated_by=random.choice(ANALYSTS)
        )

        report_count += 1

    print(f"[OK] Created {report_count} compliance reports")


def create_spending_patterns():
    """Create spending pattern data for users"""
    pattern_count = 0

    for user in USERS:
        transactions = Transaction.objects.filter(user=user)

        if transactions.count() < 5:
            continue

        # Hourly pattern
        hourly_data = {}
        for hour in range(24):
            hour_count = transactions.filter(timestamp__hour=hour).count()
            if hour_count > 0:
                hourly_data[str(hour)] = hour_count

        if hourly_data:
            SpendingPattern.objects.update_or_create(
                user=user,
                pattern_type='hourly',
                defaults={
                    'pattern_data': hourly_data,
                    'baseline_value': sum(hourly_data.values()) / 24 if hourly_data else 0,
                    'std_deviation': 0  # Simplified
                }
            )
            pattern_count += 1

        # Daily pattern
        daily_data = {}
        for day in range(7):
            day_transactions = transactions.filter(
                timestamp__week_day=day
            )
            if day_transactions.exists():
                daily_data[str(day)] = day_transactions.count()

        if daily_data:
            SpendingPattern.objects.update_or_create(
                user=user,
                pattern_type='daily',
                defaults={
                    'pattern_data': daily_data,
                    'baseline_value': sum(daily_data.values()) / 7 if daily_data else 0,
                    'std_deviation': 0
                }
            )
            pattern_count += 1

        # Merchant pattern
        merchant_data = {}
        for txn in transactions:
            merchant_data[txn.merchant] = merchant_data.get(txn.merchant, 0) + float(txn.amount)

        if merchant_data:
            SpendingPattern.objects.update_or_create(
                user=user,
                pattern_type='merchant',
                defaults={
                    'pattern_data': merchant_data,
                    'baseline_value': sum(merchant_data.values()) / len(merchant_data),
                    'std_deviation': 0
                }
            )
            pattern_count += 1

    print(f"[OK] Created {pattern_count} spending patterns")


def create_audit_log_entries():
    """Create demo audit log entries"""
    log_count = 0

    # Create various audit log entries
    actions = [
        ('transaction_created', 'Transaction', lambda: Transaction.objects.first().id if Transaction.exists() else '1'),
        ('alert_triggered', 'Alert', lambda: Alert.objects.first().id if Alert.exists() else '1'),
        ('alert_acknowledged', 'Alert', lambda: Alert.objects.first().id if Alert.exists() else '1'),
        ('case_created', 'FraudCase', lambda: FraudCase.objects.first().case_number if FraudCase.exists() else 'FC-001'),
        ('case_updated', 'FraudCase', lambda: FraudCase.objects.first().case_number if FraudCase.exists() else 'FC-001'),
        ('rule_modified', 'FraudRule', lambda: FraudRule.objects.first().id if FraudRule.exists() else '1'),
        ('report_generated', 'ComplianceReport', lambda: ComplianceReport.objects.first().id if ComplianceReport.exists() else '1'),
    ]

    # Create logs spanning the last 30 days
    for i in range(100):
        action_type, entity_type, entity_id_fn = random.choice(actions)

        try:
            entity_id = entity_id_fn()
            timestamp = datetime.now() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )

            log = AuditLog(
                action_type=action_type,
                entity_type=entity_type,
                entity_id=str(entity_id),
                actor=random.choice(ANALYSTS + ['system', 'admin']),
                changes={'demo': True},
                timestamp=timestamp,
                ip_address=random.choice(IP_ADDRESSES)
            )
            log.save()
            log_count += 1
        except:
            pass

    print(f"[OK] Created {log_count} audit log entries")


def update_user_profiles():
    """Update spending profiles for all users"""
    analyzer = SpendingPatternAnalyzer()

    for user in USERS:
        profile = analyzer.analyze_and_update_profile(user)
        if profile:
            risk_badge = {
                'low': '[OK]',
                'medium': '[WARN]',
                'high': '[!]'
            }
            print(f"  {profile.user} - Risk: {profile.risk_level} {risk_badge.get(profile.risk_level, '')} ({profile.total_transactions} transactions)")


def main():
    """Generate comprehensive demo data for FinShield"""
    print("="*70)
    print("FinShield - Comprehensive Demo Data Generator")
    print("="*70)
    print()

    # Step 1: Create default fraud rules
    print("Step 1: Creating fraud detection rules...")
    create_default_rules()
    print()

    # Step 2: Create notification templates and preferences
    print("Step 2: Creating notification templates and preferences...")
    create_notification_templates()
    create_notification_preferences()
    print()

    # Step 3: Generate transactions with varied risk levels
    print("Step 3: Generating 350 transactions with varied risk profiles...")
    safe_count = 0
    suspicious_count = 0
    fraud_count = 0

    # Generate transactions with specific risk distribution
    for i in range(350):
        if i < 60:  # First 60: high risk
            txn, risk_score, severity, alert = generate_transaction_with_risk(risk_level='high')
        elif i < 150:  # Next 90: medium risk
            txn, risk_score, severity, alert = generate_transaction_with_risk(risk_level='medium')
        elif i < 240:  # Next 90: low risk
            txn, risk_score, severity, alert = generate_transaction_with_risk(risk_level='low')
        else:  # Last 110: safe
            txn, risk_score, severity, alert = generate_transaction_with_risk(risk_level='safe')

        if txn.status == 'safe':
            safe_count += 1
        elif txn.status == 'suspicious':
            suspicious_count += 1
        elif txn.status == 'fraud':
            fraud_count += 1

        if (i + 1) % 50 == 0:
            print(f"  Generated {i + 1} transactions...")

    print()
    print("Transaction Statistics:")
    print(f"  Total: 350")
    print(f"  Safe: {safe_count} ({safe_count/3.5:.1f}%)")
    print(f"  Suspicious: {suspicious_count} ({suspicious_count/3.5:.1f}%)")
    print(f"  Fraud: {fraud_count} ({fraud_count/3.5:.1f}%)")
    print()

    # Step 4: Update user profiles
    print("Step 4: Updating user spending profiles...")
    update_user_profiles()
    print()

    # Step 5: Create demo fraud cases
    print("Step 5: Creating demo fraud cases...")
    create_demo_fraud_cases()
    print()

    # Step 6: Create SAR reports
    print("Step 6: Creating Suspicious Activity Reports...")
    create_demo_sar_reports()
    print()

    # Step 7: Create compliance reports
    print("Step 7: Creating compliance reports...")
    create_compliance_reports()
    print()

    # Step 8: Create spending patterns
    print("Step 8: Creating spending pattern data...")
    create_spending_patterns()
    print()

    # Step 9: Create audit log entries
    print("Step 9: Creating audit log entries...")
    create_audit_log_entries()
    print()

    # Step 10: Summary
    print("="*70)
    print("Demo Data Generation Complete!")
    print("="*70)
    print()
    print("Database Statistics:")
    print(f"  Transactions: {Transaction.objects.count()}")
    print(f"  Alerts: {Alert.objects.count()}")
    print(f"  User Profiles: {UserProfile.objects.count()}")
    print(f"  Spending Patterns: {SpendingPattern.objects.count()}")
    print(f"  Fraud Rules: {FraudRule.objects.count()}")
    print(f"  Fraud Cases: {FraudCase.objects.count()}")
    print(f"  Case Notes: {CaseNote.objects.count()}")
    print(f"  Case Evidence: {CaseEvidence.objects.count()}")
    print(f"  SAR Reports: {SuspiciousActivityReport.objects.count()}")
    print(f"  Compliance Reports: {ComplianceReport.objects.count()}")
    print(f"  Audit Log Entries: {AuditLog.objects.count()}")
    print(f"  Notification Templates: {NotificationTemplate.objects.count()}")
    print(f"  Notification Preferences: {NotificationPreference.objects.count()}")
    print()
    print("Demo Users:")
    for user in USERS:
        txn_count = Transaction.objects.filter(user=user).count()
        fraud_count = Transaction.objects.filter(user=user, status='fraud').count()
        suspicious_count = Transaction.objects.filter(user=user, status='suspicious').count()
        print(f"  {user} - {txn_count} txns, {fraud_count} fraud, {suspicious_count} suspicious")
    print()
    print("Access the application at:")
    print("  • Dashboard:     http://127.0.0.1:8000/")
    print("  • Alerts:        http://127.0.0.1:8000/alerts/")
    print("  • Cases:         http://127.0.0.1:8000/cases/")
    print("  • Profiles:      http://127.0.0.1:8000/profiles/")
    print("  • Rules:         http://127.0.0.1:8000/rules/")
    print("  • Reports:       http://127.0.0.1:8000/reports/")
    print("  • Analytics:     http://127.0.0.1:8000/analytics/")
    print("  • Audit Log:     http://127.0.0.1:8000/audit-log/")
    print("  • Admin Panel:   http://127.0.0.1:8000/admin/")
    print()
    print("="*70)


if __name__ == '__main__':
    main()
