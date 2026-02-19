"""
OptiFlow - AI-Based Business Process Optimizer
Views for Dashboard, Data Entry, and Analytics
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Avg, Count, Q, F, Sum, Max, Min
from django.db.models.functions import TruncDate, TruncDay
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json

from .models import (
    BusinessProcess, ProcessStep, OperationalData, Recommendation, ProcessMetric
)
from .ai_engine import analyze_process, ProcessAnalyzer


# ========== DASHBOARD VIEWS ==========

def dashboard(request):
    """
    Main dashboard view with aggregated metrics and insights.
    """
    # Get all active processes
    processes = BusinessProcess.objects.filter(status='active')

    # Calculate overall metrics
    total_processes = processes.count()
    total_steps = ProcessStep.objects.filter(process__status='active', is_active=True).count()
    total_executions = OperationalData.objects.filter(process__status='active').count()
    completed_executions = OperationalData.objects.filter(
        process__status='active',
        status='completed'
    ).count()

    # Calculate completion rate
    completion_rate = (completed_executions / total_executions * 100) if total_executions > 0 else 0

    # Get recent recommendations
    recent_recommendations = Recommendation.objects.filter(
        process__status='active'
    ).order_by('-created_at')[:5]

    # Get processes with their metrics
    process_list = []
    for process in processes:
        process_data = {
            'id': process.id,
            'name': process.name,
            'total_steps': process.get_total_steps(),
            'completion_rate': process.get_completion_rate(),
            'avg_cycle_time': round(process.get_average_cycle_time(), 2),
            'target_cycle_time': process.target_cycle_time,
            'created_at': process.created_at,
        }
        process_list.append(process_data)

    # Get execution trends for last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    daily_executions = OperationalData.objects.filter(
        created_at__gte=thirty_days_ago
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id'),
        avg_time=Avg('execution_time')
    ).order_by('date')

    execution_trend = [
        {
            'date': item['date'].strftime('%Y-%m-%d'),
            'count': item['count'],
            'avg_time': round(item['avg_time'], 2) if item['avg_time'] else 0
        }
        for item in daily_executions
    ]

    # Get status distribution
    status_distribution = OperationalData.objects.filter(
        process__status='active'
    ).values('status').annotate(
        count=Count('id')
    ).order_by('status')

    status_data = {item['status']: item['count'] for item in status_distribution}

    # Top 5 bottleneck steps
    bottleneck_steps = []
    for step in ProcessStep.objects.filter(is_active=True).select_related('process'):
        avg_time = step.get_average_execution_time()
        if avg_time > 0:
            bottleneck_steps.append({
                'process_name': step.process.name,
                'step_name': step.name,
                'avg_time': avg_time,
                'failure_rate': step.get_failure_rate()
            })

    bottleneck_steps.sort(key=lambda x: x['avg_time'], reverse=True)
    bottleneck_steps = bottleneck_steps[:5]

    context = {
        'total_processes': total_processes,
        'total_steps': total_steps,
        'total_executions': total_executions,
        'completed_executions': completed_executions,
        'completion_rate': round(completion_rate, 2),
        'processes': process_list,
        'recent_recommendations': recent_recommendations,
        'execution_trend': json.dumps(execution_trend),
        'status_data': json.dumps(status_data),
        'bottleneck_steps': bottleneck_steps,
    }

    return render(request, 'core/dashboard.html', context)


def process_dashboard(request, process_id):
    """
    Detailed dashboard for a specific process.
    """
    process = get_object_or_404(BusinessProcess, id=process_id)

    # Get steps
    steps = ProcessStep.objects.filter(process=process, is_active=True).order_by('step_order')

    # Step metrics
    step_metrics = []
    for step in steps:
        logs = step.logs.filter(status='completed').exclude(execution_time__isnull=True)

        if logs.exists():
            times = [log.execution_time for log in logs]
            step_metrics.append({
                'order': step.step_order,
                'name': step.name,
                'type': step.step_type,
                'avg_time': round(step.get_average_execution_time(), 2),
                'estimated_duration': step.estimated_duration,
                'total_executions': logs.count(),
                'failure_rate': step.get_failure_rate(),
            })

    # Recent executions
    recent_executions = OperationalData.objects.filter(
        process=process
    ).select_related('step').order_by('-created_at')[:10]

    # Recent recommendations
    recommendations = Recommendation.objects.filter(
        process=process
    ).order_by('-impact_score', '-created_at')

    # Execution trend
    thirty_days_ago = timezone.now() - timedelta(days=30)
    execution_data = OperationalData.objects.filter(
        process=process,
        status='completed',
        created_at__gte=thirty_days_ago
    ).exclude(execution_time__isnull=True).order_by('created_at')

    trend_data = [
        {
            'date': log.created_at.strftime('%Y-%m-%d %H:%M'),
            'time': log.execution_time,
            'step': log.step.name if log.step else 'Process Level'
        }
        for log in execution_data
    ]

    context = {
        'process': process,
        'steps': steps,
        'step_metrics': step_metrics,
        'recent_executions': recent_executions,
        'recommendations': recommendations,
        'trend_data': json.dumps(trend_data),
    }

    return render(request, 'core/process_dashboard.html', context)


# ========== PROCESS MANAGEMENT VIEWS ==========

def process_list(request):
    """
    List all business processes.
    """
    processes = BusinessProcess.objects.all().order_by('-created_at')

    # Add metrics to each process
    process_data = []
    for process in processes:
        process_data.append({
            'process': process,
            'total_steps': process.get_total_steps(),
            'avg_cycle_time': round(process.get_average_cycle_time(), 2),
            'completion_rate': process.get_completion_rate(),
        })

    return render(request, 'core/process_list.html', {'processes': process_data})


def process_create(request):
    """
    Create a new business process.
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        target_cycle_time = request.POST.get('target_cycle_time')
        status = request.POST.get('status', 'active')

        if not name:
            messages.error(request, 'Process name is required.')
            return render(request, 'core/process_form.html')

        process = BusinessProcess.objects.create(
            name=name,
            description=description,
            target_cycle_time=float(target_cycle_time) if target_cycle_time else None,
            status=status
        )

        messages.success(request, f'Process "{name}" created successfully.')
        return redirect('core:process_detail', process_id=process.id)

    return render(request, 'core/process_form.html')


def process_detail(request, process_id):
    """
    Show detailed view of a process.
    """
    process = get_object_or_404(BusinessProcess, id=process_id)
    steps = ProcessStep.objects.filter(process=process).order_by('step_order')

    return render(request, 'core/process_detail.html', {
        'process': process,
        'steps': steps
    })


def step_create(request, process_id):
    """
    Create a new step for a process.
    """
    process = get_object_or_404(BusinessProcess, id=process_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        step_order = request.POST.get('step_order')
        step_type = request.POST.get('step_type', 'manual')
        estimated_duration = request.POST.get('estimated_duration')

        if not name or not step_order:
            messages.error(request, 'Step name and order are required.')
            return render(request, 'core/step_form.html', {'process': process})

        ProcessStep.objects.create(
            process=process,
            name=name,
            description=description,
            step_order=int(step_order),
            step_type=step_type,
            estimated_duration=float(estimated_duration) if estimated_duration else None
        )

        messages.success(request, f'Step "{name}" created successfully.')
        return redirect('core:process_detail', process_id=process.id)

    return render(request, 'core/step_form.html', {'process': process})


# ========== DATA ENTRY VIEWS ==========

def log_entry(request):
    """
    Log operational data for a process step.
    """
    if request.method == 'POST':
        process_id = request.POST.get('process')
        step_id = request.POST.get('step')
        run_id = request.POST.get('run_id')
        status = request.POST.get('status', 'pending')
        priority = request.POST.get('priority', 'medium')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        assigned_to = request.POST.get('assigned_to', '')
        notes = request.POST.get('notes', '')

        if not process_id or not run_id:
            messages.error(request, 'Process and Run ID are required.')
            return _render_log_form(request)

        process = get_object_or_404(BusinessProcess, id=process_id)
        step = None
        if step_id:
            step = get_object_or_404(ProcessStep, id=step_id)

        # Parse datetime
        start_dt = datetime.fromisoformat(start_time) if start_time else None
        end_dt = datetime.fromisoformat(end_time) if end_time else None

        log = OperationalData.objects.create(
            process=process,
            step=step,
            run_id=run_id,
            status=status,
            priority=priority,
            start_time=start_dt,
            end_time=end_dt,
            assigned_to=assigned_to,
            notes=notes
        )

        messages.success(request, f'Log entry "{run_id}" created successfully.')
        return redirect('core:log_list')

    return _render_log_form(request)


def _render_log_form(request):
    """Helper to render log entry form."""
    processes = BusinessProcess.objects.filter(status='active')
    return render(request, 'core/log_entry.html', {'processes': processes})


def log_list(request):
    """
    List all operational data logs.
    """
    logs = OperationalData.objects.select_related(
        'process', 'step'
    ).order_by('-created_at')

    # Filter by process if provided
    process_id = request.GET.get('process')
    if process_id:
        logs = logs.filter(process_id=process_id)

    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        logs = logs.filter(status=status)

    return render(request, 'core/log_list.html', {
        'logs': logs[:100],  # Limit to 100 most recent
        'process_id': process_id,
        'status': status
    })


def log_detail(request, log_id):
    """
    Show detailed view of a log entry.
    """
    log = get_object_or_404(OperationalData, id=log_id)
    return render(request, 'core/log_detail.html', {'log': log})


# ========== ANALYTICS VIEWS ==========

def analytics_dashboard(request):
    """
    Main analytics dashboard with charts and insights.
    """
    processes = BusinessProcess.objects.filter(status='active')

    # Cycle time data for chart
    cycle_time_data = []
    for process in processes:
        cycle_time_data.append({
            'name': process.name,
            'avg_time': round(process.get_average_cycle_time(), 2),
            'target_time': process.target_cycle_time or 0
        })

    # Efficiency scores
    efficiency_data = []
    for process in processes:
        logs = process.logs.filter(status='completed').exclude(execution_time__isnull=True)
        if logs.exists():
            times = [log.execution_time for log in logs]
            analyzer = ProcessAnalyzer()
            metrics = analyzer.calculate_efficiency_score(
                times,
                process.target_cycle_time
            )
            efficiency_data.append({
                'name': process.name,
                'efficiency': metrics['efficiency_score'],
                'consistency': metrics['consistency_score']
            })

    # Step performance comparison
    step_performance = []
    for step in ProcessStep.objects.filter(is_active=True).select_related('process')[:15]:
        step_performance.append({
            'process': step.process.name,
            'step': step.name,
            'avg_time': round(step.get_average_execution_time(), 2),
            'estimated': step.estimated_duration or 0
        })

    # Daily throughput (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    throughput_data = OperationalData.objects.filter(
        status='completed',
        created_at__gte=thirty_days_ago
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')

    throughput = [
        {
            'date': item['date'].strftime('%Y-%m-%d'),
            'count': item['count']
        }
        for item in throughput_data
    ]

    context = {
        'cycle_time_data': json.dumps(cycle_time_data),
        'efficiency_data': json.dumps(efficiency_data),
        'step_performance': json.dumps(step_performance),
        'throughput_data': json.dumps(throughput),
        'processes': processes,
    }

    return render(request, 'core/analytics.html', context)


def process_analysis(request, process_id):
    """
    Run AI analysis on a specific process.
    """
    process = get_object_or_404(BusinessProcess, id=process_id)

    # Run AI analysis
    analysis_results = analyze_process(process_id)

    # Store recommendations in database
    for rec in analysis_results['recommendations']:
        # Check if similar recommendation already exists
        existing = Recommendation.objects.filter(
            process=process,
            title=rec['title'],
            status__in=['pending', 'approved']
        ).first()

        if not existing:
            step = None
            if 'step_name' in rec:
                step = ProcessStep.objects.filter(
                    process=process,
                    name=rec['step_name']
                ).first()

            Recommendation.objects.create(
                process=process,
                step=step,
                title=rec['title'],
                category=rec['category'],
                priority=rec['priority'],
                description=rec['description'],
                recommendation=rec['recommendation'],
                current_value=rec['current_value'],
                target_value=rec['target_value'],
                potential_savings=rec['potential_savings'],
                impact_score=rec['impact_score'],
                analysis_data=rec['analysis_data']
            )

    # Get steps for visualization
    steps = ProcessStep.objects.filter(process=process).order_by('step_order')

    # Prepare step data for charts
    step_chart_data = []
    for step in steps:
        logs = step.logs.filter(status='completed').exclude(execution_time__isnull=True)
        if logs.exists():
            times = [log.execution_time for log in logs]
            step_chart_data.append({
                'name': step.name,
                'times': times,
                'avg': sum(times) / len(times),
                'min': min(times),
                'max': max(times)
            })

    context = {
        'process': process,
        'analysis': analysis_results,
        'steps': steps,
        'step_chart_data': json.dumps(step_chart_data),
    }

    return render(request, 'core/process_analysis.html', context)


# ========== RECOMMENDATION VIEWS ==========

def recommendation_list(request):
    """
    List all recommendations.
    """
    recommendations = Recommendation.objects.select_related(
        'process', 'step'
    ).order_by('-impact_score', '-created_at')

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        recommendations = recommendations.filter(status=status_filter)

    # Filter by priority
    priority_filter = request.GET.get('priority')
    if priority_filter:
        recommendations = recommendations.filter(priority=priority_filter)

    return render(request, 'core/recommendations.html', {
        'recommendations': recommendations,
        'status_filter': status_filter,
        'priority_filter': priority_filter
    })


def recommendation_detail(request, rec_id):
    """
    Show detailed view of a recommendation.
    """
    recommendation = get_object_or_404(Recommendation, id=rec_id)
    return render(request, 'core/recommendation_detail.html', {
        'recommendation': recommendation
    })


def recommendation_update_status(request, rec_id):
    """
    Update recommendation status.
    """
    if request.method == 'POST':
        recommendation = get_object_or_404(Recommendation, id=rec_id)
        new_status = request.POST.get('status')

        if new_status in ['pending', 'approved', 'implemented', 'rejected']:
            recommendation.status = new_status
            if new_status == 'implemented':
                recommendation.implemented_at = timezone.now()
            recommendation.save()

            messages.success(request, f'Recommendation status updated to "{new_status}".')
        else:
            messages.error(request, 'Invalid status.')

    return redirect('core:recommendation_detail', rec_id=rec_id)


# ========== API VIEWS ==========

def api_process_metrics(request, process_id):
    """
    API endpoint to get process metrics for AJAX calls.
    """
    process = get_object_or_404(BusinessProcess, id=process_id)

    steps = ProcessStep.objects.filter(process=process, is_active=True)

    metrics = {
        'process_name': process.name,
        'avg_cycle_time': round(process.get_average_cycle_time(), 2),
        'completion_rate': process.get_completion_rate(),
        'total_steps': steps.count(),
        'steps': []
    }

    for step in steps:
        logs = step.logs.filter(status='completed').exclude(execution_time__isnull=True)
        if logs.exists():
            times = [log.execution_time for log in logs]
            metrics['steps'].append({
                'name': step.name,
                'avg_time': round(sum(times) / len(times), 2),
                'min_time': round(min(times), 2),
                'max_time': round(max(times), 2),
                'count': len(times),
                'failure_rate': step.get_failure_rate()
            })

    return JsonResponse(metrics)


def api_analyze_process(request, process_id):
    """
    API endpoint to trigger process analysis.
    """
    try:
        analysis = analyze_process(process_id)
        return JsonResponse({'success': True, 'analysis': analysis})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ========== REPORTING VIEWS ==========

def optimization_report(request):
    """
    Generate optimization impact report.
    """
    # Get all recommendations
    all_recommendations = Recommendation.objects.all()

    # Calculate potential impact
    total_potential_savings = 0
    implemented_savings = 0

    for rec in all_recommendations:
        if rec.potential_savings:
            total_potential_savings += rec.potential_savings
            if rec.status == 'implemented':
                implemented_savings += rec.potential_savings

    # Category breakdown
    category_breakdown = all_recommendations.values('category').annotate(
        count=Count('id'),
        avg_impact=Avg('impact_score')
    ).order_by('-avg_impact')

    # Status breakdown
    status_breakdown = all_recommendations.values('status').annotate(
        count=Count('id')
    ).order_by('status')

    # Top impact recommendations
    top_recommendations = all_recommendations.order_by('-impact_score')[:10]

    # Recent implemented
    recent_implemented = all_recommendations.filter(
        status='implemented'
    ).order_by('-implemented_at')[:5]

    context = {
        'total_recommendations': all_recommendations.count(),
        'total_potential_savings': round(total_potential_savings, 2),
        'implemented_savings': round(implemented_savings, 2),
        'implementation_rate': round(
            (all_recommendations.filter(status='implemented').count() / all_recommendations.count() * 100)
            if all_recommendations.count() > 0 else 0, 2
        ),
        'category_breakdown': category_breakdown,
        'status_breakdown': status_breakdown,
        'top_recommendations': top_recommendations,
        'recent_implemented': recent_implemented,
    }

    return render(request, 'core/optimization_report.html', context)
