from datetime import datetime, timedelta
from decimal import Decimal
from collections import defaultdict
from statistics import mean, stdev
from .models import (
    Transaction, Alert, UserProfile, SpendingPattern,
    FraudRule, RuleExecutionLog, AuditLog, NotificationLog
)
import json
import time


# ============================================================================
# ANOMALY DETECTION ENGINE
# ============================================================================

class AnomalyDetectionEngine:
    """Advanced anomaly detection with multiple detection strategies"""

    def __init__(self):
        self.rules = self._load_active_rules()

    def _load_active_rules(self):
        """Load all active fraud detection rules from database"""
        return FraudRule.objects.filter(is_active=True)

    def analyze_transaction(self, transaction):
        """
        Run all active rules against a transaction and return total risk score
        Returns: (total_risk_score, triggered_rules)
        """
        total_risk = 0
        triggered_rules = []

        for rule in self.rules:
            risk_points, triggered = self._apply_rule(transaction, rule)

            # Log execution
            RuleExecutionLog.objects.create(
                rule=rule,
                transaction=transaction,
                triggered=triggered,
                risk_points_added=risk_points if triggered else 0,
                execution_time=0
            )

            if triggered:
                total_risk += risk_points
                triggered_rules.append({
                    'rule': rule.name,
                    'points': risk_points,
                    'description': rule.description
                })

        return total_risk, triggered_rules

    def _apply_rule(self, transaction, rule):
        """Apply a single rule to a transaction"""
        config = rule.rule_config
        triggered = False
        risk_points = 0

        if rule.rule_type == 'amount_threshold':
            triggered, risk_points = self._check_amount_threshold(transaction, config)
        elif rule.rule_type == 'time_based':
            triggered, risk_points = self._check_time_based(transaction, config)
        elif rule.rule_type == 'location_based':
            triggered, risk_points = self._check_location_based(transaction, config)
        elif rule.rule_type == 'velocity_check':
            triggered, risk_points = self._check_velocity(transaction, config)
        elif rule.rule_type == 'pattern_based':
            triggered, risk_points = self._check_pattern_based(transaction, config)

        return (risk_points if triggered else 0), triggered

    def _check_amount_threshold(self, transaction, config):
        """Check if transaction amount exceeds threshold"""
        threshold = config.get('threshold', 10000)
        risk_points = config.get('risk_points', 50)

        triggered = float(transaction.amount) > threshold
        return triggered, risk_points if triggered else 0

    def _check_time_based(self, transaction, config):
        """Check if transaction occurs at unusual hours"""
        start_hour = config.get('start_hour', 1)
        end_hour = config.get('end_hour', 5)
        risk_points = config.get('risk_points', 30)

        hour = transaction.timestamp.hour
        triggered = start_hour <= hour <= end_hour
        return triggered, risk_points if triggered else 0

    def _check_location_based(self, transaction, config):
        """Check if transaction is from suspicious location"""
        suspicious_locations = config.get('suspicious_locations', [])
        risk_points = config.get('risk_points', 40)

        triggered = transaction.location in suspicious_locations
        return triggered, risk_points if triggered else 0

    def _check_velocity(self, transaction, config):
        """Check for high-velocity transactions (multiple transactions in short time)"""
        time_window_minutes = config.get('time_window_minutes', 10)
        max_transactions = config.get('max_transactions', 3)
        risk_points = config.get('risk_points', 60)

        cutoff_time = transaction.timestamp - timedelta(minutes=time_window_minutes)
        recent_txns = Transaction.objects.filter(
            user=transaction.user,
            timestamp__gte=cutoff_time
        ).count()

        triggered = recent_txns > max_transactions
        return triggered, risk_points if triggered else 0

    def _check_pattern_based(self, transaction, config):
        """Check transaction against user's spending patterns"""
        try:
            profile = UserProfile.objects.get(user=transaction.user)

            # Check amount deviation
            avg_amount = float(profile.avg_transaction_amount)
            if avg_amount > 0:
                deviation_ratio = abs(float(transaction.amount) - avg_amount) / avg_amount
                max_deviation = config.get('max_deviation', 3.0)  # 3x normal amount

                if deviation_ratio > max_deviation:
                    return True, config.get('risk_points', 40)

            # Check unusual location
            if profile.typical_locations and transaction.location not in profile.typical_locations:
                return True, config.get('risk_points', 30)

            # Check unusual merchant
            if profile.typical_merchants and transaction.merchant not in profile.typical_merchants:
                # Lower risk for new merchant
                if config.get('check_new_merchant', False):
                    return True, config.get('merchant_risk_points', 20)

        except UserProfile.DoesNotExist:
            pass  # No profile exists yet

        return False, 0


# ============================================================================
# SPENDING PATTERN ANALYSIS
# ============================================================================

class SpendingPatternAnalyzer:
    """Analyze and update user spending patterns"""

    def analyze_and_update_profile(self, user):
        """Analyze user transactions and update their profile"""
        transactions = Transaction.objects.filter(user=user)

        if not transactions.exists():
            return None

        # Calculate statistics
        amounts = [float(t.amount) for t in transactions]
        avg_amount = mean(amounts)
        max_amount = max(amounts)
        min_amount = min(amounts)

        # Analyze locations
        location_counts = defaultdict(int)
        merchant_counts = defaultdict(int)
        hour_counts = defaultdict(int)

        for t in transactions:
            location_counts[t.location] += 1
            merchant_counts[t.merchant] += 1
            hour_counts[t.timestamp.hour] += 1

        # Get top locations and merchants
        total_txns = len(transactions)
        typical_locations = [
            loc for loc, count in sorted(location_counts.items(), key=lambda x: x[1], reverse=True)
            if count / total_txns > 0.1  # Locations with >10% of transactions
        ][:5]

        typical_merchants = [
            merch for merch, count in sorted(merchant_counts.items(), key=lambda x: x[1], reverse=True)
            if count / total_txns > 0.05  # Merchants with >5% of transactions
        ][:10]

        # Get typical hours
        typical_hours = [
            hour for hour, count in sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
            if count / total_txns > 0.05  # Hours with >5% of transactions
        ]

        # Calculate user risk level based on transaction patterns
        fraud_count = transactions.filter(status__in=['suspicious', 'fraud']).count()
        fraud_ratio = fraud_count / total_txns if total_txns > 0 else 0

        if fraud_ratio > 0.3:
            risk_level = 'high'
        elif fraud_ratio > 0.1:
            risk_level = 'medium'
        else:
            risk_level = 'low'

        # Create or update profile
        profile, created = UserProfile.objects.update_or_create(
            user=user,
            defaults={
                'avg_transaction_amount': round(avg_amount, 2),
                'max_transaction_amount': round(max_amount, 2),
                'min_transaction_amount': round(min_amount, 2),
                'typical_locations': typical_locations,
                'typical_merchants': typical_merchants,
                'typical_hours': typical_hours,
                'risk_level': risk_level,
                'total_transactions': total_txns,
            }
        )

        return profile

    def detect_spending_anomalies(self, user, transaction):
        """
        Detect if a transaction deviates from user's typical spending patterns
        Returns: (is_anomaly, anomaly_score, reasons)
        """
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return False, 0, ["No profile exists"]

        anomaly_score = 0
        reasons = []

        # Check amount anomaly
        if profile.avg_transaction_amount > 0:
            amount_ratio = float(transaction.amount) / float(profile.avg_transaction_amount)
            if amount_ratio > 5:
                anomaly_score += 50
                reasons.append(f"Amount is {amount_ratio:.1f}x user average")
            elif amount_ratio > 3:
                anomaly_score += 30
                reasons.append(f"Amount is {amount_ratio:.1f}x user average")

        # Check location anomaly
        if profile.typical_locations and transaction.location not in profile.typical_locations:
            anomaly_score += 25
            reasons.append(f"Unusual location: {transaction.location}")

        # Check merchant anomaly
        if profile.typical_merchants and transaction.merchant not in profile.typical_merchants:
            anomaly_score += 15
            reasons.append(f"Unusual merchant: {transaction.merchant}")

        # Check time anomaly
        if profile.typical_hours:
            hour = transaction.timestamp.hour
            if hour not in profile.typical_hours:
                anomaly_score += 10
                reasons.append(f"Unusual time: {hour}:00")

        is_anomaly = anomaly_score >= 40
        return is_anomaly, anomaly_score, reasons

    def generate_spending_report(self, user, days=30):
        """Generate a spending analysis report for a user"""
        cutoff_date = datetime.now() - timedelta(days=days)
        transactions = Transaction.objects.filter(
            user=user,
            timestamp__gte=cutoff_date
        )

        if not transactions.exists():
            return None

        report = {
            'user': user,
            'period_days': days,
            'total_transactions': transactions.count(),
            'total_amount': sum(float(t.amount) for t in transactions),
            'by_merchant': defaultdict(float),
            'by_location': defaultdict(float),
            'by_day': defaultdict(int),
            'high_risk_count': transactions.filter(status__in=['suspicious', 'fraud']).count(),
        }

        for t in transactions:
            report['by_merchant'][t.merchant] += float(t.amount)
            report['by_location'][t.location] += float(t.amount)
            report['by_day'][t.timestamp.strftime('%Y-%m-%d')] += 1

        # Convert defaultdicts to regular dicts
        report['by_merchant'] = dict(sorted(
            report['by_merchant'].items(),
            key=lambda x: x[1],
            reverse=True
        ))
        report['by_location'] = dict(sorted(
            report['by_location'].items(),
            key=lambda x: x[1],
            reverse=True
        ))
        report['by_day'] = dict(report['by_day'])

        return report


# ============================================================================
# ADVANCED RISK SCORING MODULE
# ============================================================================

class AdvancedRiskScorer:
    """Enhanced risk scoring with multiple factors and weights"""

    # Risk factor weights
    BASE_WEIGHTS = {
        'amount_anomaly': 0.25,
        'pattern_deviation': 0.30,
        'velocity_risk': 0.20,
        'historical_risk': 0.15,
        'contextual_risk': 0.10,
    }

    def __init__(self):
        self.anomaly_engine = AnomalyDetectionEngine()
        self.pattern_analyzer = SpendingPatternAnalyzer()

    def calculate_comprehensive_risk(self, transaction):
        """
        Calculate comprehensive risk score (0-100) using multiple factors
        Returns: (risk_score, risk_factors, severity)
        """
        risk_factors = {}
        total_weighted_risk = 0

        # 1. Amount Anomaly Risk
        amount_risk = self._calculate_amount_risk(transaction)
        risk_factors['amount_anomaly'] = amount_risk
        total_weighted_risk += amount_risk * self.BASE_WEIGHTS['amount_anomaly']

        # 2. Pattern Deviation Risk
        pattern_risk = self._calculate_pattern_risk(transaction)
        risk_factors['pattern_deviation'] = pattern_risk
        total_weighted_risk += pattern_risk * self.BASE_WEIGHTS['pattern_deviation']

        # 3. Velocity Risk
        velocity_risk = self._calculate_velocity_risk(transaction)
        risk_factors['velocity_risk'] = velocity_risk
        total_weighted_risk += velocity_risk * self.BASE_WEIGHTS['velocity_risk']

        # 4. Historical Risk
        historical_risk = self._calculate_historical_risk(transaction)
        risk_factors['historical_risk'] = historical_risk
        total_weighted_risk += historical_risk * self.BASE_WEIGHTS['historical_risk']

        # 5. Contextual Risk
        contextual_risk = self._calculate_contextual_risk(transaction)
        risk_factors['contextual_risk'] = contextual_risk
        total_weighted_risk += contextual_risk * self.BASE_WEIGHTS['contextual_risk']

        # Final risk score (0-100)
        final_risk = min(100, max(0, int(total_weighted_risk)))

        # Determine severity
        severity = self._determine_severity(final_risk)

        return final_risk, risk_factors, severity

    def _calculate_amount_risk(self, transaction):
        """Calculate risk based on transaction amount"""
        amount = float(transaction.amount)

        # Progressive amount risk
        if amount > 50000:
            return 100
        elif amount > 25000:
            return 80
        elif amount > 10000:
            return 60
        elif amount > 5000:
            return 40
        elif amount > 1000:
            return 20
        else:
            return 5

    def _calculate_pattern_risk(self, transaction):
        """Calculate risk based on deviation from user patterns"""
        is_anomaly, anomaly_score, reasons = self.pattern_analyzer.detect_spending_anomalies(
            transaction.user, transaction
        )
        return anomaly_score if is_anomaly else 0

    def _calculate_velocity_risk(self, transaction):
        """Calculate risk based on transaction velocity"""
        # Check transactions in last hour
        one_hour_ago = transaction.timestamp - timedelta(hours=1)
        recent_count = Transaction.objects.filter(
            user=transaction.user,
            timestamp__gte=one_hour_ago
        ).count()

        # Check transactions in last 24 hours
        one_day_ago = transaction.timestamp - timedelta(days=1)
        daily_count = Transaction.objects.filter(
            user=transaction.user,
            timestamp__gte=one_day_ago
        ).count()

        # Calculate velocity risk
        if recent_count > 10:
            return 100
        elif recent_count > 5:
            return 75
        elif recent_count > 3:
            return 50
        elif daily_count > 50:
            return 60
        elif daily_count > 20:
            return 30
        else:
            return 0

    def _calculate_historical_risk(self, transaction):
        """Calculate risk based on user's historical behavior"""
        try:
            profile = UserProfile.objects.get(user=transaction.user)

            if profile.risk_level == 'high':
                return 50
            elif profile.risk_level == 'medium':
                return 25
            else:
                # Check recent fraud/suspicious transactions
                thirty_days_ago = datetime.now() - timedelta(days=30)
                recent_fraud = Transaction.objects.filter(
                    user=transaction.user,
                    timestamp__gte=thirty_days_ago,
                    status__in=['suspicious', 'fraud']
                ).count()

                if recent_fraud > 5:
                    return 60
                elif recent_fraud > 2:
                    return 30
                else:
                    return 5
        except UserProfile.DoesNotExist:
            # New user with no history
            return 10

    def _calculate_contextual_risk(self, transaction):
        """Calculate risk based on transaction context"""
        risk = 0

        # Foreign location
        if transaction.location.lower() in ['foreign', 'international', 'abroad']:
            risk += 40

        # Unusual time (late night)
        hour = transaction.timestamp.hour
        if hour >= 1 and hour <= 5:
            risk += 30

        # High-risk merchant categories (could be extended)
        high_risk_merchants = ['jewelry', 'electronics', 'crypto', 'gambling']
        if any(merchant in transaction.merchant.lower() for merchant in high_risk_merchants):
            risk += 20

        return min(100, risk)

    def _determine_severity(self, risk_score):
        """Determine severity level based on risk score"""
        if risk_score >= 80:
            return 'critical'
        elif risk_score >= 60:
            return 'high'
        elif risk_score >= 40:
            return 'medium'
        else:
            return 'low'


# ============================================================================
# SIMPLIFIED LEGACY FUNCTION (for backward compatibility)
# ============================================================================

def calculate_risk(transaction):
    """
    Legacy function - uses AdvancedRiskScorer for compatibility
    Returns simple risk score for backward compatibility
    """
    scorer = AdvancedRiskScorer()
    risk_score, risk_factors, severity = scorer.calculate_comprehensive_risk(transaction)
    return risk_score


# ============================================================================
# AUDIT LOGGING
# ============================================================================

def log_audit_event(action_type, entity_type, entity_id, actor=None, changes=None, ip_address=None):
    """Log an audit event"""
    AuditLog.objects.create(
        action_type=action_type,
        actor=actor,
        entity_type=entity_type,
        entity_id=str(entity_id),
        changes=changes or {},
        ip_address=ip_address
    )
