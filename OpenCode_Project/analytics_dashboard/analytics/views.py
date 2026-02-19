from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.http import JsonResponse
from django.db import models
from django.db.models import Avg, Sum, Count, Max, Min
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models.functions import TruncHour, TruncDay, TruncWeek, TruncMonth
from .models import (
    DataSource, Metric, Dashboard, Widget,
    MetricData, Report, Alert, AlertLog
)


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('analytics:dashboard_list')
    else:
        form = UserCreationForm()
    return render(request, 'analytics/signup.html', {'form': form})


@login_required
def dashboard_list(request):
    dashboards = Dashboard.objects.filter(
        models.Q(created_by=request.user) | models.Q(viewers=request.user) | models.Q(is_public=True)
    ).distinct()

    return render(request, 'analytics/dashboard_list.html', {
        'dashboards': dashboards,
    })


@login_required
def dashboard_detail(request, dashboard_id):
    dashboard = get_object_or_404(
        Dashboard.objects.filter(
            models.Q(created_by=request.user) | models.Q(viewers=request.user) | models.Q(is_public=True)
        ),
        id=dashboard_id
    )

    widgets = dashboard.widgets.select_related('metric').all()

    return render(request, 'analytics/dashboard_detail.html', {
        'dashboard': dashboard,
        'widgets': widgets,
    })


@login_required
def dashboard_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        is_public = request.POST.get('is_public') == 'on'

        dashboard = Dashboard.objects.create(
            name=name,
            description=description,
            is_public=is_public,
            created_by=request.user
        )
        return redirect('analytics:dashboard_detail', dashboard_id=dashboard.id)

    return render(request, 'analytics/dashboard_form.html')


@login_required
def widget_data_api(request, widget_id):
    widget = get_object_or_404(Widget, id=widget_id)

    metric = widget.metric
    time_range = request.GET.get('range', '7d')

    now = timezone.now()
    if time_range == '1d':
        start_time = now - timedelta(days=1)
        trunc_func = TruncHour
    elif time_range == '7d':
        start_time = now - timedelta(days=7)
        trunc_func = TruncDay
    elif time_range == '30d':
        start_time = now - timedelta(days=30)
        trunc_func = TruncDay
    elif time_range == '90d':
        start_time = now - timedelta(days=90)
        trunc_func = TruncWeek
    else:
        start_time = now - timedelta(days=7)
        trunc_func = TruncDay

    data_points = MetricData.objects.filter(
        metric=metric,
        timestamp__gte=start_time
    ).annotate(
        period=trunc_func('timestamp')
    ).values('period').annotate(
        avg_value=Avg('value'),
        sum_value=Sum('value'),
        count=Count('id')
    ).order_by('period')

    labels = [dp['period'].strftime('%Y-%m-%d %H:%M') for dp in data_points]
    values = [float(dp['avg_value']) for dp in data_points]

    response_data = {
        'widget_id': widget_id,
        'widget_type': widget.widget_type,
        'title': widget.title,
        'labels': labels,
        'data': values,
        'unit': metric.unit,
        'display_config': widget.display_config,
    }

    if widget.widget_type in ['pie', 'doughnut']:
        response_data['data'] = {
            'values': values,
            'labels': labels,
        }

    return JsonResponse(response_data)


@login_required
def metric_list(request):
    metrics = Metric.objects.filter(created_by=request.user)

    return render(request, 'analytics/metric_list.html', {
        'metrics': metrics,
    })


@login_required
def metric_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        metric_type = request.POST.get('metric_type', 'count')
        unit = request.POST.get('unit', '')
        aggregation_period = request.POST.get('aggregation_period', 'daily')
        target_value = request.POST.get('target_value')

        metric = Metric.objects.create(
            name=name,
            description=description,
            metric_type=metric_type,
            unit=unit,
            aggregation_period=aggregation_period,
            target_value=float(target_value) if target_value else None,
            created_by=request.user
        )
        return redirect('analytics:metric_detail', metric_id=metric.id)

    return render(request, 'analytics/metric_form.html', {


        'metric_types': Metric.METRIC_TYPES,
    })


@login_required
def metric_detail(request, metric_id):
    metric = get_object_or_404(Metric, id=metric_id)

    recent_data = metric.data_points.all()[:100]

    return render(request, 'analytics/metric_detail.html', {
        'metric': metric,
        'recent_data': recent_data,
    })


@login_required
def add_metric_data(request, metric_id):
    metric = get_object_or_404(Metric, id=metric_id)

    if request.method == 'POST':
        value = request.POST.get('value')
        metadata = request.POST.get('metadata', '{}')

        try:
            MetricData.objects.create(
                metric=metric,
                value=float(value),
                metadata=metadata if metadata else {}
            )
            return redirect('analytics:metric_detail', metric_id=metric.id)
        except ValueError:
            pass

    return render(request, 'analytics/add_metric_data.html', {
        'metric': metric,
    })


@login_required
def alert_list(request):
    alerts = Alert.objects.filter(created_by=request.user)

    return render(request, 'analytics/alert_list.html', {
        'alerts': alerts,
    })


@login_required
def alert_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        metric_id = request.POST.get('metric')
        condition_type = request.POST.get('condition_type', 'greater_than')
        threshold_value = request.POST.get('threshold_value')
        severity = request.POST.get('severity', 'warning')

        metric = get_object_or_404(Metric, id=metric_id, created_by=request.user)

        Alert.objects.create(
            name=name,
            description=description,
            metric=metric,
            condition_type=condition_type,
            threshold_value=float(threshold_value),
            severity=severity,
            created_by=request.user
        )
        return redirect('analytics:alert_list')

    metrics = Metric.objects.filter(created_by=request.user)
    return render(request, 'analytics/alert_form.html', {
        'metrics': metrics,
        'condition_types': Alert.CONDITION_TYPES,
        'severity_levels': Alert.SEVERITY_LEVELS,
    })


@login_required
def alert_logs(request):
    logs = AlertLog.objects.select_related('alert').order_by('-triggered_at')

    return render(request, 'analytics/alert_logs.html', {
        'logs': logs,
    })


@login_required
def acknowledge_alert(request, log_id):
    log = get_object_or_404(AlertLog, id=log_id)
    log.is_acknowledged = True
    log.acknowledged_by = request.user
    log.acknowledged_at = timezone.now()
    log.save()

    return redirect('analytics:alert_logs')


@login_required
def report_list(request):
    reports = Report.objects.filter(created_by=request.user)

    return render(request, 'analytics/report_list.html', {
        'reports': reports,
    })


@login_required
def data_source_list(request):
    data_sources = DataSource.objects.filter(created_by=request.user)

    return render(request, 'analytics/data_source_list.html', {
        'data_sources': data_sources,
    })


@login_required
def data_source_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        source_type = request.POST.get('source_type', 'manual')

        DataSource.objects.create(
            name=name,
            source_type=source_type,
            created_by=request.user
        )
        return redirect('analytics:data_source_list')

    return render(request, 'analytics/data_source_form.html', {
        'source_types': DataSource.SOURCE_TYPES,
    })


@login_required
def home(request):
    # Get user's dashboards
    user_dashboards = Dashboard.objects.filter(
        models.Q(created_by=request.user) | models.Q(viewers=request.user)
    ).distinct()

    # Get user's metrics
    user_metrics = Metric.objects.filter(created_by=request.user)

    # Get user's data sources
    user_data_sources = DataSource.objects.filter(created_by=request.user)

    # Get user's alerts
    user_alerts = Alert.objects.filter(created_by=request.user)

    # Get recent alert logs for user's alerts only
    user_alert_ids = user_alerts.values_list('id', flat=True)
    recent_alerts = AlertLog.objects.filter(
        alert_id__in=user_alert_ids,
        is_acknowledged=False
    ).select_related('alert').order_by('-triggered_at')[:10]

    # Get total data points for user's metrics
    total_data_points = MetricData.objects.filter(
        metric__in=user_metrics
    ).count()

    # Get recent activity (recently created items)
    recent_dashboards = user_dashboards.order_by('-created_at')[:5]
    recent_metrics = user_metrics.order_by('-created_at')[:5]

    # User statistics
    user_stats = {
        'dashboards_count': user_dashboards.count(),
        'metrics_count': user_metrics.count(),
        'data_sources_count': user_data_sources.count(),
        'alerts_count': user_alerts.filter(is_active=True).count(),
        'data_points_count': total_data_points,
        'unacknowledged_alerts': recent_alerts.count(),
    }

    return render(request, 'analytics/home.html', {
        'user_dashboards': user_dashboards,
        'user_metrics': user_metrics,
        'user_data_sources': user_data_sources,
        'user_alerts': user_alerts,
        'recent_alerts': recent_alerts,
        'recent_dashboards': recent_dashboards,
        'recent_metrics': recent_metrics,
        'user_stats': user_stats,
    })
