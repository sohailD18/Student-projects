from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import json


class Transaction(models.Model):
    STATUS_CHOICES = [
        ('safe', 'Safe'),
        ('suspicious', 'Suspicious'),
        ('fraud', 'Fraud'),
        ('under_review', 'Under Review'),
    ]

    TRANSACTION_TYPES = [
        ('purchase', 'Purchase'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
        ('deposit', 'Deposit'),
        ('payment', 'Payment'),
    ]

    user = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=200)
    merchant = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='safe')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='purchase')
    device_id = models.CharField(max_length=200, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    risk_score = models.IntegerField(default=0)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.merchant}: ${self.amount}"

    class Meta:
        ordering = ['-timestamp']


class Alert(models.Model):
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('acknowledged', 'Acknowledged'),
        ('investigating', 'Investigating'),
        ('resolved', 'Resolved'),
        ('false_positive', 'False Positive'),
    ]

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='alerts')
    risk_score = models.IntegerField()
    rule_triggered = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(blank=True, null=True)
    acknowledged_by = models.CharField(max_length=100, blank=True, null=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolution_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Alert for {self.transaction.id} - Score: {self.risk_score} ({self.severity})"

    class Meta:
        ordering = ['-created_at']


# Spending Pattern Analysis Module
class UserProfile(models.Model):
    user = models.CharField(max_length=100, unique=True)
    avg_transaction_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_transaction_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    min_transaction_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    typical_locations = models.JSONField(default=list)
    typical_merchants = models.JSONField(default=list)
    typical_hours = models.JSONField(default=list)
    risk_level = models.CharField(max_length=20, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='low')
    last_updated = models.DateTimeField(auto_now=True)
    total_transactions = models.IntegerField(default=0)
    account_age_days = models.IntegerField(default=0)

    def __str__(self):
        return f"Profile: {self.user} ({self.risk_level} risk)"


class SpendingPattern(models.Model):
    user = models.CharField(max_length=100)
    pattern_type = models.CharField(max_length=50)  # 'hourly', 'daily', 'weekly', 'merchant'
    pattern_data = models.JSONField()  # Store pattern statistics
    baseline_value = models.DecimalField(max_digits=12, decimal_places=2)
    std_deviation = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.pattern_type} pattern"


# Rule-Based Screening Module
class FraudRule(models.Model):
    RULE_TYPES = [
        ('amount_threshold', 'Amount Threshold'),
        ('time_based', 'Time Based'),
        ('location_based', 'Location Based'),
        ('velocity_check', 'Velocity Check'),
        ('pattern_based', 'Pattern Based'),
        ('composite', 'Composite'),
    ]

    name = models.CharField(max_length=200, unique=True)
    rule_type = models.CharField(max_length=50, choices=RULE_TYPES)
    description = models.TextField()
    rule_config = models.JSONField()  # Store rule parameters
    is_active = models.BooleanField(default=True)
    weight = models.IntegerField(default=50)  # Weight in risk scoring (0-100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (Weight: {self.weight})"


class RuleExecutionLog(models.Model):
    rule = models.ForeignKey(FraudRule, on_delete=models.CASCADE, related_name='executions')
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='rule_executions')
    triggered = models.BooleanField(default=False)
    risk_points_added = models.IntegerField(default=0)
    execution_time = models.FloatField(default=0)  # Execution time in milliseconds
    executed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rule.name} - Transaction {self.transaction.id}"


# Fraud Case Management Module
class FraudCase(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('investigating', 'Investigating'),
        ('evidence_collection', 'Evidence Collection'),
        ('pending_review', 'Pending Review'),
        ('closed', 'Closed'),
        ('escalated', 'Escalated'),
    ]

    PRIORITY_LEVELS = [
        ('p1', 'P1 - Critical'),
        ('p2', 'P2 - High'),
        ('p3', 'P3 - Medium'),
        ('p4', 'P4 - Low'),
    ]

    case_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='p3')
    assigned_to = models.CharField(max_length=100, blank=True, null=True)
    related_transactions = models.ManyToManyField(Transaction, related_name='fraud_cases')
    related_alerts = models.ManyToManyField(Alert, related_name='fraud_cases')
    suspected_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    confirmed_fraud_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(blank=True, null=True)
    closed_by = models.CharField(max_length=100, blank=True, null=True)
    resolution_summary = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Case {self.case_number} - {self.title}"

    class Meta:
        ordering = ['-created_at']


class CaseNote(models.Model):
    fraud_case = models.ForeignKey(FraudCase, on_delete=models.CASCADE, related_name='notes')
    author = models.CharField(max_length=100)
    note = models.TextField()
    is_internal = models.BooleanField(default=True)  # Internal notes not visible to customers
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note for Case {self.fraud_case.case_number}"


class CaseEvidence(models.Model):
    EVIDENCE_TYPES = [
        ('transaction_log', 'Transaction Log'),
        ('screenshot', 'Screenshot'),
        ('document', 'Document'),
        ('email', 'Email'),
        ('system_log', 'System Log'),
        ('other', 'Other'),
    ]

    fraud_case = models.ForeignKey(FraudCase, on_delete=models.CASCADE, related_name='evidence')
    evidence_type = models.CharField(max_length=50, choices=EVIDENCE_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    uploaded_by = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - Case {self.fraud_case.case_number}"


# Compliance Reporting Module
class AuditLog(models.Model):
    ACTION_TYPES = [
        ('transaction_created', 'Transaction Created'),
        ('alert_triggered', 'Alert Triggered'),
        ('alert_acknowledged', 'Alert Acknowledged'),
        ('case_created', 'Case Created'),
        ('case_updated', 'Case Updated'),
        ('case_closed', 'Case Closed'),
        ('rule_modified', 'Rule Modified'),
        ('user_login', 'User Login'),
        ('report_generated', 'Report Generated'),
    ]

    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    actor = models.CharField(max_length=100, blank=True, null=True)
    entity_type = models.CharField(max_length=100)  # Transaction, Alert, Case, etc.
    entity_id = models.CharField(max_length=100)
    changes = models.JSONField(default=dict)  # Store what changed
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return f"{self.action_type} - {self.entity_type}:{self.entity_id}"

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['action_type']),
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['timestamp']),
        ]


class ComplianceReport(models.Model):
    REPORT_TYPES = [
        ('sar', 'Suspicious Activity Report'),
        ('aml', 'AML Compliance'),
        ('fraud_summary', 'Fraud Summary'),
        ('case_summary', 'Case Summary'),
        ('audit_trail', 'Audit Trail'),
        ('custom', 'Custom Report'),
    ]

    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    report_data = models.JSONField()
    date_range_start = models.DateTimeField()
    date_range_end = models.DateTimeField()
    generated_by = models.CharField(max_length=100)
    generated_at = models.DateTimeField(auto_now_add=True)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], default='completed')

    def __str__(self):
        return f"{self.report_type} - {self.title}"

    class Meta:
        ordering = ['-generated_at']


class SuspiciousActivityReport(models.Model):
    """SAR - Suspicious Activity Report for regulatory filing"""
    case = models.OneToOneField(FraudCase, on_delete=models.CASCADE, related_name='sar')
    sar_number = models.CharField(max_length=50, unique=True)
    filing_date = models.DateField()
    suspicious_amount = models.DecimalField(max_digits=12, decimal_places=2)
    activity_description = models.TextField()
    transaction_dates = models.JSONField()  # List of date ranges
    involved_parties = models.JSONField()  # List of user identifiers
    fraud_types = models.JSONField()  # List of fraud type codes
    law_enforcement_referral = models.BooleanField(default=False)
    agency_contacted = models.CharField(max_length=200, blank=True, null=True)
    filed_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"SAR {self.sar_number}"


# Alert Notification System Enhancements
class NotificationTemplate(models.Model):
    CHANNELS = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('webhook', 'Webhook'),
        ('in_app', 'In-App'),
    ]

    name = models.CharField(max_length=200, unique=True)
    channel = models.CharField(max_length=20, choices=CHANNELS)
    subject_template = models.CharField(max_length=200, blank=True, null=True)
    body_template = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.channel})"


class NotificationLog(models.Model):
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='notifications')
    template = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, null=True)
    channel = models.CharField(max_length=20)
    recipient = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('sent', 'Sent'), ('failed', 'Failed')])
    error_message = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.channel} notification to {self.recipient}"

    class Meta:
        ordering = ['-created_at']


class NotificationPreference(models.Model):
    user = models.CharField(max_length=100, unique=True)
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email_address = models.EmailField(blank=True, null=True)
    notify_on_low_severity = models.BooleanField(default=False)
    notify_on_medium_severity = models.BooleanField(default=True)
    notify_on_high_severity = models.BooleanField(default=True)
    notify_on_critical_severity = models.BooleanField(default=True)
    digest_mode = models.BooleanField(default=False)  # Send notifications in batches
    digest_frequency = models.CharField(max_length=20, choices=[('hourly', 'Hourly'), ('daily', 'Daily'), ('weekly', 'Weekly')], default='daily')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user}"
