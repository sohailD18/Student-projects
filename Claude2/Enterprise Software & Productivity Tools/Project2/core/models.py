"""
OptiFlow - AI-Based Business Process Optimizer
Database Models for Process Management and Analysis
"""

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
import json


class BusinessProcess(models.Model):
    """
    Represents a complete business process workflow.
    Examples: Order Processing, Customer Onboarding, Product Development
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived'),
    ]

    name = models.CharField(max_length=200, unique=True, help_text="Name of the business process")
    description = models.TextField(blank=True, help_text="Detailed description of the process")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    target_cycle_time = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Target cycle time in minutes"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Business Process"
        verbose_name_plural = "Business Processes"

    def __str__(self):
        return self.name

    def get_average_cycle_time(self):
        """Calculate average cycle time for this process"""
        logs = self.logs.filter(status='completed').exclude(execution_time__isnull=True)
        if logs.exists():
            return logs.aggregate(avg=models.Avg('execution_time'))['avg']
        return 0

    def get_total_steps(self):
        """Return total number of steps in this process"""
        return self.steps.count()

    def get_completion_rate(self):
        """Calculate the completion rate percentage"""
        total = self.logs.count()
        completed = self.logs.filter(status='completed').count()
        if total > 0:
            return round((completed / total) * 100, 2)
        return 0


class ProcessStep(models.Model):
    """
    Individual steps within a business process.
    Each step represents a distinct phase or task in the workflow.
    """
    STEP_TYPE_CHOICES = [
        ('manual', 'Manual Task'),
        ('automated', 'Automated Task'),
        ('approval', 'Approval Gate'),
        ('notification', 'Notification'),
        ('integration', 'System Integration'),
    ]

    process = models.ForeignKey(
        BusinessProcess,
        on_delete=models.CASCADE,
        related_name='steps',
        help_text="Parent business process"
    )
    name = models.CharField(max_length=200, help_text="Name of the process step")
    description = models.TextField(blank=True, help_text="Detailed description of the step")
    step_order = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Order of execution in the workflow"
    )
    step_type = models.CharField(max_length=20, choices=STEP_TYPE_CHOICES, default='manual')
    estimated_duration = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Estimated duration in minutes"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['process', 'step_order']
        unique_together = ['process', 'step_order']
        verbose_name = "Process Step"
        verbose_name_plural = "Process Steps"

    def __str__(self):
        return f"{self.process.name} - Step {self.step_order}: {self.name}"

    def get_average_execution_time(self):
        """Calculate average execution time for this step"""
        logs = self.logs.filter(status='completed').exclude(execution_time__isnull=True)
        if logs.exists():
            return logs.aggregate(avg=models.Avg('execution_time'))['avg']
        return 0

    def get_failure_rate(self):
        """Calculate the failure/error rate percentage"""
        total = self.logs.count()
        failed = self.logs.filter(status='failed').count()
        if total > 0:
            return round((failed / total) * 100, 2)
        return 0


class OperationalData(models.Model):
    """
    Logs execution data for each process step.
    Tracks actual performance metrics for analysis.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    # Identifiers
    process = models.ForeignKey(
        BusinessProcess,
        on_delete=models.CASCADE,
        related_name='logs',
        help_text="Associated business process"
    )
    step = models.ForeignKey(
        ProcessStep,
        on_delete=models.CASCADE,
        related_name='logs',
        null=True,
        blank=True,
        help_text="Associated process step (null for process-level logs)"
    )

    # Execution details
    run_id = models.CharField(max_length=100, help_text="Unique identifier for this execution run")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')

    # Timing metrics
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    execution_time = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Execution time in minutes"
    )

    # Additional data
    assigned_to = models.CharField(max_length=100, blank=True, help_text="Person or system assigned")
    notes = models.TextField(blank=True, help_text="Additional notes or comments")
    error_message = models.TextField(blank=True, help_text="Error details if failed")

    # Metadata
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional metadata as JSON")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['run_id']),
            models.Index(fields=['status']),
            models.Index(fields=['process', 'step']),
            models.Index(fields=['created_at']),
        ]
        verbose_name = "Operational Data"
        verbose_name_plural = "Operational Data"

    def __str__(self):
        step_name = self.step.name if self.step else "Process Level"
        return f"{self.process.name} - {step_name} - {self.run_id}"

    def save(self, *args, **kwargs):
        """Calculate execution time before saving"""
        if self.start_time and self.end_time:
            from datetime import datetime
            diff = self.end_time - self.start_time
            self.execution_time = diff.total_seconds() / 60  # Convert to minutes
        super().save(*args, **kwargs)


class Recommendation(models.Model):
    """
    AI-generated recommendations for process optimization.
    Created by the AI engine based on bottleneck analysis.
    """
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('implemented', 'Implemented'),
        ('rejected', 'Rejected'),
    ]

    CATEGORY_CHOICES = [
        ('bottleneck', 'Bottleneck Removal'),
        ('automation', 'Automation Opportunity'),
        ('resource', 'Resource Allocation'),
        ('process', 'Process Redesign'),
        ('performance', 'Performance Improvement'),
    ]

    # Relationships
    process = models.ForeignKey(
        BusinessProcess,
        on_delete=models.CASCADE,
        related_name='recommendations',
        help_text="Process this recommendation applies to"
    )
    step = models.ForeignKey(
        ProcessStep,
        on_delete=models.CASCADE,
        related_name='recommendations',
        null=True,
        blank=True,
        help_text="Step this recommendation applies to (optional)"
    )

    # Recommendation details
    title = models.CharField(max_length=300, help_text="Brief title of the recommendation")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='performance')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Analysis data
    description = models.TextField(help_text="Detailed description of the issue")
    recommendation = models.TextField(help_text="Specific recommendation for improvement")

    # Metrics
    current_value = models.FloatField(null=True, blank=True, help_text="Current metric value")
    target_value = models.FloatField(null=True, blank=True, help_text="Target metric value")
    potential_savings = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Potential time savings in minutes"
    )
    impact_score = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Impact score (0-100)"
    )

    # Analysis details
    analysis_data = models.JSONField(default=dict, blank=True, help_text="Raw analysis data")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    implemented_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-impact_score', '-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['category']),
        ]
        verbose_name = "Recommendation"
        verbose_name_plural = "Recommendations"

    def __str__(self):
        return f"{self.title} ({self.get_priority_display()})"

    def get_roi_percentage(self):
        """Calculate return on investment percentage"""
        if self.current_value and self.target_value and self.current_value > 0:
            improvement = self.current_value - self.target_value
            return round((improvement / self.current_value) * 100, 2)
        return 0


class ProcessMetric(models.Model):
    """
    Aggregated metrics for business processes.
    Stores calculated metrics for dashboard display.
    """
    METRIC_TYPE_CHOICES = [
        ('cycle_time', 'Average Cycle Time'),
        ('throughput', 'Throughput'),
        ('efficiency', 'Efficiency Score'),
        ('quality', 'Quality Score'),
        ('bottleneck_score', 'Bottleneck Score'),
    ]

    process = models.ForeignKey(
        BusinessProcess,
        on_delete=models.CASCADE,
        related_name='metrics'
    )
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPE_CHOICES)
    value = models.FloatField(help_text="Metric value")
    date = models.DateField(help_text="Date of metric calculation")

    # Additional context
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']
        unique_together = ['process', 'metric_type', 'date']
        verbose_name = "Process Metric"
        verbose_name_plural = "Process Metrics"

    def __str__(self):
        return f"{self.process.name} - {self.get_metric_type_display()}: {self.value}"
