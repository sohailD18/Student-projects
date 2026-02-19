"""
Database models for the fraud detection system.
"""
from django.db import models
from django.utils import timezone
import json


class Transaction(models.Model):
    """
    Model to store financial transaction data.
    """
    TRANSACTION_TYPE_CHOICES = [
        ('purchase', 'Purchase'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
        ('deposit', 'Deposit'),
        ('payment', 'Payment'),
    ]

    # Transaction details
    transaction_id = models.CharField(max_length=100, unique=True, db_index=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')

    # Location information
    location = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    # Merchant details
    merchant = models.CharField(max_length=200)
    merchant_category = models.CharField(max_length=100)

    # Account information
    account_id = models.CharField(max_length=100)
    card_number_last4 = models.CharField(max_length=4)

    # Timestamp
    timestamp = models.DateTimeField(default=timezone.now)

    # AI Detection Results
    is_fraud = models.BooleanField(default=False, db_index=True)
    risk_score = models.FloatField(default=0.0)  # 0.0 to 1.0
    fraud_reason = models.TextField(blank=True, null=True)

    # Additional metadata
    device_id = models.CharField(max_length=200, blank=True, null=True)
    browser = models.CharField(max_length=200, blank=True, null=True)
    os = models.CharField(max_length=100, blank=True, null=True)

    # Flags
    is_flagged = models.BooleanField(default=False)
    is_reviewed = models.BooleanField(default=False)

    # Raw features for AI model (stored as JSON)
    features = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['is_fraud', '-timestamp']),
            models.Index(fields=['risk_score']),
        ]

    def __str__(self):
        return f"{self.transaction_id} - ${self.amount} - {'FRAUD' if self.is_fraud else 'LEGIT'}"

    def get_risk_level(self):
        """Returns the risk level based on risk_score"""
        if self.risk_score >= 0.8:
            return 'CRITICAL'
        elif self.risk_score >= 0.6:
            return 'HIGH'
        elif self.risk_score >= 0.4:
            return 'MEDIUM'
        elif self.risk_score >= 0.2:
            return 'LOW'
        else:
            return 'VERY LOW'


class ModelMetrics(models.Model):
    """
    Model to store AI model performance metrics.
    """
    model_name = models.CharField(max_length=100)
    model_version = models.CharField(max_length=50)

    # Performance metrics
    accuracy = models.FloatField()
    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()

    # Confusion matrix
    true_positives = models.IntegerField(default=0)
    true_negatives = models.IntegerField(default=0)
    false_positives = models.IntegerField(default=0)
    false_negatives = models.IntegerField(default=0)

    # Training details
    training_samples = models.IntegerField(default=0)
    test_samples = models.IntegerField(default=0)
    fraud_samples = models.IntegerField(default=0)

    # Model parameters (stored as JSON)
    parameters = models.JSONField(default=dict, blank=True)

    # Timestamps
    trained_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-trained_at']
        verbose_name_plural = 'Model Metrics'

    def __str__(self):
        return f"{self.model_name} v{self.model_version} - F1: {self.f1_score:.4f}"


class FraudAlert(models.Model):
    """
    Model to store fraud alerts for real-time monitoring.
    """
    ALERT_STATUS_CHOICES = [
        ('new', 'New'),
        ('investigating', 'Investigating'),
        ('confirmed', 'Confirmed Fraud'),
        ('false_positive', 'False Positive'),
        ('resolved', 'Resolved'),
    ]

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=50)  # e.g., 'unusual_amount', 'suspicious_location'
    status = models.CharField(max_length=20, choices=ALERT_STATUS_CHOICES, default='new')

    description = models.TextField()
    risk_score = models.FloatField()

    # Investigation details
    assigned_to = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return f"Alert for {self.transaction.transaction_id} - {self.status}"


class AuditLog(models.Model):
    """
    Model to track system audits and actions.
    """
    ACTION_CHOICES = [
        ('transaction_created', 'Transaction Created'),
        ('fraud_detected', 'Fraud Detected'),
        ('alert_created', 'Alert Created'),
        ('model_trained', 'Model Trained'),
        ('report_generated', 'Report Generated'),
        ('investigation_started', 'Investigation Started'),
        ('investigation_closed', 'Investigation Closed'),
    ]

    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    entity_type = models.CharField(max_length=50)  # 'transaction', 'alert', 'model', etc.
    entity_id = models.CharField(max_length=100)

    user = models.CharField(max_length=100, blank=True, null=True)
    details = models.JSONField(default=dict, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} - {self.entity_type}:{self.entity_id}"
