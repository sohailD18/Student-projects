from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import random

from analytics.models import (
    DataSource, Metric, Dashboard, Widget,
    MetricData, Report, Alert, AlertLog
)


class Command(BaseCommand):
    help = 'Create demo data for the Analytics Dashboard'

    def handle(self, *args, **options):
        self.stdout.write('Creating demo data...')

        # Get or create admin user
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created user: {user.username}'))

        # Create Data Sources
        data_sources = []
        ds_names = [
            ('Production Database', 'database'),
            ('Google Analytics API', 'api'),
            ('Sales CSV Import', 'file'),
            ('User Feedback Form', 'manual'),
        ]
        for name, source_type in ds_names:
            ds, created = DataSource.objects.get_or_create(
                name=name,
                created_by=user,
                defaults={
                    'source_type': source_type,
                    'refresh_interval': random.choice([300, 600, 1800, 3600]),
                    'is_active': True,
                }
            )
            data_sources.append(ds)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created data source: {name}'))

        # Create Metrics
        metrics = []
        metric_data = [
            ('Daily Active Users', 'count', 'users', 'daily', 5000),
            ('Revenue', 'sum', '$', 'daily', 50000),
            ('Conversion Rate', 'percentage', '%', 'daily', 3.5),
            ('Page Load Time', 'average', 'ms', 'hourly', 2000),
            ('Server CPU Usage', 'average', '%', 'hourly', 60),
            ('New Signups', 'count', 'users', 'daily', 150),
            ('Bounce Rate', 'percentage', '%', 'daily', 45),
            ('Customer Satisfaction', 'average', 'score', 'weekly', 8.5),
        ]

        for name, metric_type, unit, period, target in metric_data:
            metric, created = Metric.objects.get_or_create(
                name=name,
                created_by=user,
                defaults={
                    'metric_type': metric_type,
                    'unit': unit,
                    'aggregation_period': period,
                    'target_value': target,
                    'data_source': random.choice(data_sources),
                    'description': f'Tracking {name.lower()} over time',
                }
            )
            metrics.append(metric)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created metric: {name}'))

        # Create historical data for metrics (last 30 days)
        self.stdout.write('Creating historical data...')
        for metric in metrics:
            # Check if data already exists
            if metric.data_points.count() > 100:
                continue

            days = 30 if metric.aggregation_period in ['daily', 'weekly'] else 7
            interval = timedelta(days=1) if metric.aggregation_period in ['daily', 'weekly'] else timedelta(hours=1)

            now = timezone.now()
            for i in range(days * 24 if interval < timedelta(days=1) else days):
                timestamp = now - (interval * i)

                # Generate realistic values based on metric type
                base_value = float(metric.target_value or 100)

                # Add some randomness
                if metric.metric_type == 'percentage':
                    value = base_value * random.uniform(0.7, 1.3)
                    value = max(0, min(100, value))
                elif metric.metric_type == 'count':
                    value = base_value * random.uniform(0.5, 1.5)
                    value = max(0, value)
                else:
                    value = base_value * random.uniform(0.8, 1.2)

                MetricData.objects.get_or_create(
                    metric=metric,
                    timestamp=timestamp,
                    defaults={
                        'value': round(value, 2),
                        'metadata': {'generated': True}
                    }
                )

        self.stdout.write(self.style.SUCCESS('Historical data created'))

        # Create Dashboards
        dashboards = []
        dashboard_names = [
            ('Executive Overview', 'High-level KPIs and business metrics'),
            ('Marketing Performance', 'Campaign and conversion metrics'),
            ('System Health', 'Server and application performance'),
            ('Sales Dashboard', 'Revenue and customer metrics'),
        ]

        for name, description in dashboard_names:
            dashboard, created = Dashboard.objects.get_or_create(
                name=name,
                created_by=user,
                defaults={
                    'description': description,
                    'is_public': random.choice([True, False]),
                    'refresh_interval': 300,
                }
            )
            dashboards.append(dashboard)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created dashboard: {name}'))

        # Create Widgets for dashboards
        widget_types = ['line', 'bar', 'pie', 'doughnut', 'number', 'area']

        for dashboard in dashboards:
            # Skip if widgets already exist
            if dashboard.widgets.count() >= 4:
                continue

            # Assign 3-5 random metrics to each dashboard
            assigned_metrics = random.sample(metrics, random.randint(3, 5))

            for idx, metric in enumerate(assigned_metrics):
                widget_type = random.choice(widget_types)
                Widget.objects.get_or_create(
                    dashboard=dashboard,
                    metric=metric,
                    defaults={
                        'title': f'{metric.name} - {metric.aggregation_period}',
                        'widget_type': widget_type,
                        'position_x': (idx % 3) * 4,
                        'position_y': (idx // 3) * 3,
                        'width': random.choice([3, 4, 6]),
                        'height': random.choice([2, 3, 4]),
                        'display_config': {
                            'showLegend': True,
                            'showGrid': True,
                            'colors': ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
                        }
                    }
                )

        self.stdout.write(self.style.SUCCESS('Widgets created'))

        # Create Alerts
        alerts = []
        alert_configs = [
            ('High CPU Alert', 'Server CPU Usage is too high', 'greater_than', 80, 'warning'),
            ('Low Conversion Alert', 'Conversion rate dropped below threshold', 'less_than', 2.0, 'critical'),
            ('Revenue Milestone', 'Daily revenue target achieved!', 'greater_than', 45000, 'info'),
            ('High Bounce Rate', 'Bounce rate is concerning', 'greater_than', 60, 'warning'),
            ('Server Response Time', 'Page load time is slow', 'greater_than', 3000, 'critical'),
        ]

        for name, description, condition, threshold, severity in alert_configs:
            # Find appropriate metric
            metric = None
            if 'CPU' in name:
                metric = Metric.objects.filter(name__icontains='cpu').first()
            elif 'Conversion' in name:
                metric = Metric.objects.filter(name__icontains='conversion').first()
            elif 'Revenue' in name:
                metric = Metric.objects.filter(name__icontains='revenue').first()
            elif 'Bounce' in name:
                metric = Metric.objects.filter(name__icontains='bounce').first()
            elif 'Response' in name or 'Load' in name:
                metric = Metric.objects.filter(name__icontains='load').first()

            if not metric:
                metric = random.choice(metrics)

            alert, created = Alert.objects.get_or_create(
                name=name,
                created_by=user,
                defaults={
                    'description': description,
                    'metric': metric,
                    'condition_type': condition,
                    'threshold_value': threshold,
                    'severity': severity,
                    'is_active': True,
                    'cooldown_period': 300,
                }
            )
            alerts.append(alert)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created alert: {name}'))

        # Create some alert logs
        for alert in alerts[:3]:
            if alert.logs.count() > 0:
                continue

            AlertLog.objects.create(
                alert=alert,
                metric_value=float(alert.threshold_value * random.uniform(1.1, 1.3)),
                message=f'{alert.name} triggered: Current value exceeds threshold of {alert.threshold_value}',
                severity=alert.severity,
            )

        self.stdout.write(self.style.SUCCESS('Alert logs created'))

        # Create Reports
        report_names = [
            ('Weekly Executive Summary', 'summary', 'weekly'),
            ('Monthly Performance Report', 'detailed', 'monthly'),
            ('Daily Operations Report', 'detailed', 'daily'),
        ]

        for name, report_type, schedule in report_names:
            report, created = Report.objects.get_or_create(
                name=name,
                created_by=user,
                defaults={
                    'report_type': report_type,
                    'schedule': schedule,
                    'format': 'pdf',
                    'is_active': True,
                }
            )
            if created:
                report.dashboards.set(random.sample(dashboards, random.randint(1, 2)))
                report.recipients.set([user])
                self.stdout.write(self.style.SUCCESS(f'Created report: {name}'))

        self.stdout.write(self.style.SUCCESS('\nDemo data created successfully!'))
        self.stdout.write(self.style.SUCCESS('Login with: username: admin, password: admin123'))
        self.stdout.write(self.style.SUCCESS('Access the application at: http://127.0.0.1:8000/'))
