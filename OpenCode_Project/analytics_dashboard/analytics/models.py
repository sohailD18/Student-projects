from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class DataSource(models.Model):
    """Data sources for analytics - API, Database, File uploads"""
    SOURCE_TYPES = [
        ('api', 'API Endpoint'),
        ('database', 'Database'),
        ('file', 'File Upload'),
        ('manual', 'Manual Entry'),
    ]

    name = models.CharField(max_length=200)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES, default='manual')
    connection_config = models.JSONField(default=dict, blank=True)
    refresh_interval = models.IntegerField(default=3600, help_text='Seconds between refreshes')
    is_active = models.BooleanField(default=True)
    last_refreshed = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='data_sources')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Metric(models.Model):
    """Metrics to track and visualize"""
    METRIC_TYPES = [
        ('count', 'Count'),
        ('sum', 'Sum'),
        ('average', 'Average'),
        ('percentage', 'Percentage'),
        ('rate', 'Rate'),
        ('custom', 'Custom Formula'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES, default='count')
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name='metrics', null=True, blank=True)
    query_config = models.JSONField(default=dict, blank=True, help_text='Query or calculation configuration')
    unit = models.CharField(max_length=50, blank=True)
    aggregation_period = models.CharField(max_length=20, default='daily',
                                         help_text='hourly, daily, weekly, monthly')
    target_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='metrics')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Dashboard(models.Model):
    """Main dashboard container"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    layout_config = models.JSONField(default=dict, blank=True)
    refresh_interval = models.IntegerField(default=300, help_text='Auto-refresh interval in seconds')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboards')
    viewers = models.ManyToManyField(User, related_name='shared_dashboards', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Widget(models.Model):
    """Individual widgets on dashboards"""
    WIDGET_TYPES = [
        ('line', 'Line Chart'),
        ('bar', 'Bar Chart'),
        ('pie', 'Pie Chart'),
        ('doughnut', 'Doughnut Chart'),
        ('number', 'Number Card'),
        ('gauge', 'Gauge/Meter'),
        ('table', 'Data Table'),
        ('area', 'Area Chart'),
        ('scatter', 'Scatter Plot'),
    ]

    title = models.CharField(max_length=200)
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES, default='line')
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='widgets')
    metric = models.ForeignKey(Metric, on_delete=models.CASCADE, related_name='widgets')
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    width = models.IntegerField(default=4)
    height = models.IntegerField(default=3)
    display_config = models.JSONField(default=dict, blank=True)
    refresh_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['dashboard', 'position_y', 'position_x']

    def __str__(self):
        return f"{self.title} ({self.dashboard.name})"


class MetricData(models.Model):
    """Historical data points for metrics"""
    metric = models.ForeignKey(Metric, on_delete=models.CASCADE, related_name='data_points')
    value = models.DecimalField(max_digits=15, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['metric', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.metric.name}: {self.value} at {self.timestamp}"


class Report(models.Model):
    """Scheduled and on-demand reports"""
    REPORT_TYPES = [
        ('summary', 'Summary Report'),
        ('detailed', 'Detailed Report'),
        ('comparison', 'Comparison Report'),
        ('trend', 'Trend Analysis'),
    ]

    SCHEDULE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('on_demand', 'On Demand'),
    ]

    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, default='summary')
    dashboards = models.ManyToManyField(Dashboard, related_name='reports')
    schedule = models.CharField(max_length=20, choices=SCHEDULE_CHOICES, default='on_demand')
    recipients = models.ManyToManyField(User, related_name='received_reports', blank=True)
    email_recipients = models.TextField(blank=True, help_text='Comma-separated email addresses')
    format = models.CharField(max_length=10, default='pdf', choices=[('pdf', 'PDF'), ('csv', 'CSV'), ('excel', 'Excel')])
    last_generated = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Alert(models.Model):
    """Alerts based on metric thresholds"""
    CONDITION_TYPES = [
        ('greater_than', 'Greater Than'),
        ('less_than', 'Less Than'),
        ('equals', 'Equals'),
        ('percentage_change', 'Percentage Change'),
        ('anomaly', 'Anomaly Detection'),
    ]

    SEVERITY_LEVELS = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    metric = models.ForeignKey(Metric, on_delete=models.CASCADE, related_name='alerts')
    condition_type = models.CharField(max_length=20, choices=CONDITION_TYPES, default='greater_than')
    threshold_value = models.DecimalField(max_digits=15, decimal_places=2)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='warning')
    is_active = models.BooleanField(default=True)
    notification_channels = models.JSONField(default=dict, blank=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    trigger_count = models.IntegerField(default=0)
    cooldown_period = models.IntegerField(default=300, help_text='Seconds between alerts')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class AlertLog(models.Model):
    """Log of triggered alerts"""
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='logs')
    metric_value = models.DecimalField(max_digits=15, decimal_places=2)
    message = models.TextField()
    severity = models.CharField(max_length=20)
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    triggered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-triggered_at']

    def __str__(self):
        return f"{self.alert.name} - {self.triggered_at.strftime('%Y-%m-%d %H:%M')}"
