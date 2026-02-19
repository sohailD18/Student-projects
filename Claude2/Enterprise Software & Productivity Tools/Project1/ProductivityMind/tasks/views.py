"""
ProductivityMind - Django Views

All views for handling HTTP requests and rendering responses.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count, Sum, Avg, F, Prefetch
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta, datetime
import json

from .models import (
    Task, Project, ProjectMember, Tag, Category,
    WorkLog, UserProfile, TaskDependency
)
from .ai_engine import (
    TaskPrioritizationEngine,
    RiskPredictionEngine,
    ProductivityAnalytics,
    run_ai_analysis
)
from .serializers import (
    TaskSerializer,
    ProjectSerializer,
    CategorySerializer,
    TagSerializer,
    WorkLogSerializer,
    DashboardSerializer,
    ReportSerializer,
    UserProfileSerializer
)


# =============================================================================
# Authentication Views
# =============================================================================

def login_view(request):
    """Custom login view"""
    if request.user.is_authenticated:
        return redirect('tasks:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me')

        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return render(request, 'tasks/auth/login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if not remember_me:
                request.session.set_expiry(0)

            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')

            next_url = request.GET.get('next', 'tasks:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password. Please try again.')

    return render(request, 'tasks/auth/login.html')


def register_view(request):
    """Custom registration view with role selection"""
    if request.user.is_authenticated:
        return redirect('tasks:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        role = request.POST.get('role', 'member')
        department = request.POST.get('department', '').strip()

        # Validation
        errors = []

        if not username:
            errors.append('Username is required.')
        elif User.objects.filter(username=username).exists():
            errors.append('Username already exists. Please choose a different one.')

        if not email:
            errors.append('Email is required.')
        elif User.objects.filter(email=email).exists():
            errors.append('Email already registered. Please use a different email.')

        if not password:
            errors.append('Password is required.')
        elif len(password) < 8:
            errors.append('Password must be at least 8 characters long.')

        if password != confirm_password:
            errors.append('Passwords do not match.')

        valid_roles = ['admin', 'manager', 'team_lead', 'member', 'viewer']
        if role not in valid_roles:
            role = 'member'

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'tasks/auth/register.html', {
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'role': role,
                'department': department,
            })

        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            # Update user profile (created automatically by signal)
            profile = user.profile
            profile.role = role
            profile.department = department
            profile.save()

            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('tasks:login')

        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'tasks/auth/register.html')

    return render(request, 'tasks/auth/register.html')


def logout_view(request):
    """Custom logout view"""
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('tasks:login')
    return render(request, 'tasks/auth/logout.html')


# =============================================================================
# Template Views (HTML Rendering)
# =============================================================================

@login_required
def index(request):
    """Dashboard home page"""
    return render(request, 'tasks/index.html')


@login_required
def dashboard_view(request):
    """Main dashboard view"""
    return render(request, 'tasks/dashboard.html')


@login_required
def tasks_view(request):
    """Tasks list/board view"""
    return render(request, 'tasks/tasks.html')


@login_required
def task_detail_view(request, task_id):
    """Single task detail view"""
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'tasks/task_detail.html', {'task': task})


@login_required
def projects_view(request):
    """Projects list view"""
    return render(request, 'tasks/projects.html')


@login_required
def reports_view(request):
    """Productivity reports view"""
    return render(request, 'tasks/reports.html')


@login_required
def calendar_view(request):
    """Calendar view of tasks"""
    return render(request, 'tasks/calendar.html')


# =============================================================================
# API Views - Task Management
# =============================================================================

@require_http_methods(["GET"])
def api_tasks_list(request):
    """
    Get list of tasks with optional filtering.

    Query params:
    - status: Filter by status (todo, in_progress, done)
    - priority: Filter by priority
    - assignee: Filter by user ID
    - project: Filter by project ID
    - tag: Filter by tag ID
    - search: Search in title/description
    - sort: Sort field (created_at, due_date, smart_priority_score)
    - order: Sort order (asc, desc)
    - limit: Limit number of results
    """
    tasks = Task.objects.select_related(
        'assignee', 'project', 'category'
    ).prefetch_related('tags', 'blocked_by', 'blocking')

    # Apply filters
    status = request.GET.get('status')
    if status:
        tasks = tasks.filter(status=status)

    priority = request.GET.get('priority')
    if priority:
        tasks = tasks.filter(priority=priority)

    assignee_id = request.GET.get('assignee')
    if assignee_id:
        tasks = tasks.filter(assignee_id=assignee_id)

    project_id = request.GET.get('project')
    if project_id:
        tasks = tasks.filter(project_id=project_id)

    tag_id = request.GET.get('tag')
    if tag_id:
        tasks = tasks.filter(tags__id=tag_id)

    search = request.GET.get('search')
    if search:
        tasks = tasks.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )

    # Risk filter
    at_risk = request.GET.get('at_risk')
    if at_risk == 'true':
        tasks = tasks.filter(is_at_risk=True)

    # Overdue filter
    overdue = request.GET.get('overdue')
    if overdue == 'true':
        now = timezone.now()
        tasks = tasks.filter(due_date__lt=now, status__in=['todo', 'in_progress'])

    # Sorting
    sort_field = request.GET.get('sort', '-smart_priority_score')
    tasks = tasks.order_by(sort_field)

    # Limit
    limit = request.GET.get('limit')
    if limit:
        tasks = tasks[:int(limit)]

    data = TaskSerializer.serialize_list(tasks)
    return JsonResponse({'success': True, 'tasks': data})


@require_http_methods(["GET"])
def api_task_detail(request, task_id):
    """Get single task details"""
    task = get_object_or_404(
        Task.objects.select_related('assignee', 'project', 'category'),
        id=task_id
    )
    data = TaskSerializer.serialize(task)
    return JsonResponse({'success': True, 'task': data})


@require_http_methods(["POST"])
@csrf_exempt
def api_task_create(request):
    """Create a new task"""
    try:
        data = json.loads(request.body)

        # Create task
        task = Task.objects.create(
            title=data.get('title'),
            description=data.get('description', ''),
            status=data.get('status', 'todo'),
            priority=data.get('priority', 'medium'),
            project_id=data.get('project'),
            assignee_id=data.get('assignee'),
            due_date=data.get('due_date'),
            estimated_hours=data.get('estimated_hours'),
            category_id=data.get('category'),
        )

        # Handle tags
        if 'tags' in data:
            task.tags.set(data['tags'])

        # Handle dependencies
        if 'blocked_by' in data:
            task.blocked_by.set(data['blocked_by'])

        # Calculate smart priority
        engine = TaskPrioritizationEngine()
        task.smart_priority_score = engine.calculate_smart_priority_score(task)

        # Assess risk
        risk_engine = RiskPredictionEngine()
        task.risk_level = risk_engine.assess_task_risk(task)
        task.is_at_risk = task.risk_level in ['high', 'critical']

        task.save()

        return JsonResponse({
            'success': True,
            'task': TaskSerializer.serialize(task),
            'message': 'Task created successfully'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@require_http_methods(["PUT", "PATCH"])
@csrf_exempt
def api_task_update(request, task_id):
    """Update an existing task"""
    try:
        task = get_object_or_404(Task, id=task_id)
        data = json.loads(request.body)

        # Update fields
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'status' in data:
            task.status = data['status']
        if 'priority' in data:
            task.priority = data['priority']
        if 'project' in data:
            task.project_id = data['project']
        if 'assignee' in data:
            task.assignee_id = data['assignee']
        if 'due_date' in data:
            if data['due_date']:
                from django.utils.dateparse import parse_datetime
                task.due_date = parse_datetime(data['due_date'])
            else:
                task.due_date = None
        if 'estimated_hours' in data:
            task.estimated_hours = data['estimated_hours']
        if 'actual_hours' in data:
            task.actual_hours = data['actual_hours']
        if 'category' in data:
            task.category_id = data['category']

        # Handle tags
        if 'tags' in data:
            task.tags.set(data['tags'])

        # Handle dependencies
        if 'blocked_by' in data:
            task.blocked_by.set(data['blocked_by'])

        # Recalculate AI scores
        engine = TaskPrioritizationEngine()
        task.smart_priority_score = engine.calculate_smart_priority_score(task)

        risk_engine = RiskPredictionEngine()
        task.risk_level = risk_engine.assess_task_risk(task)
        task.is_at_risk = task.risk_level in ['high', 'critical']

        task.save()

        return JsonResponse({
            'success': True,
            'task': TaskSerializer.serialize(task),
            'message': 'Task updated successfully'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@require_http_methods(["DELETE"])
def api_task_delete(request, task_id):
    """Delete a task"""
    try:
        task = get_object_or_404(Task, id=task_id)
        task.delete()
        return JsonResponse({
            'success': True,
            'message': 'Task deleted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@require_http_methods(["POST"])
def api_task_bulk_status(request):
    """Bulk update task status"""
    try:
        data = json.loads(request.body)
        task_ids = data.get('task_ids', [])
        new_status = data.get('status')

        if not task_ids or not new_status:
            return JsonResponse({
                'success': False,
                'error': 'task_ids and status are required'
            }, status=400)

        updated_count = Task.objects.filter(
            id__in=task_ids
        ).update(status=new_status)

        # Recalculate AI scores for affected tasks
        engine = TaskPrioritizationEngine()
        risk_engine = RiskPredictionEngine()

        for task in Task.objects.filter(id__in=task_ids):
            task.smart_priority_score = engine.calculate_smart_priority_score(task)
            task.risk_level = risk_engine.assess_task_risk(task)
            task.is_at_risk = task.risk_level in ['high', 'critical']
            task.save()

        return JsonResponse({
            'success': True,
            'updated_count': updated_count,
            'message': f'{updated_count} tasks updated'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


# =============================================================================
# API Views - Projects
# =============================================================================

@require_http_methods(["GET"])
def api_projects_list(request):
    """Get all projects"""
    projects = Project.objects.prefetch_related('members')
    data = ProjectSerializer.serialize_list(projects)
    return JsonResponse({'success': True, 'projects': data})


@require_http_methods(["GET"])
def api_project_detail(request, project_id):
    """Get single project details"""
    project = get_object_or_404(
        Project.objects.prefetch_related('members'),
        id=project_id
    )
    data = ProjectSerializer.serialize(project)
    return JsonResponse({'success': True, 'project': data})


@require_http_methods(["POST"])
@csrf_exempt
def api_project_create(request):
    """Create a new project"""
    try:
        data = json.loads(request.body)

        project = Project.objects.create(
            name=data['name'],
            description=data.get('description', '')
        )

        # Add members if provided
        if 'members' in data:
            for member_data in data['members']:
                ProjectMember.objects.create(
                    project=project,
                    user_id=member_data['user_id'],
                    role=member_data.get('role', 'member')
                )

        return JsonResponse({
            'success': True,
            'project': ProjectSerializer.serialize(project),
            'message': 'Project created successfully'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


# =============================================================================
# API Views - Categories & Tags
# =============================================================================

@require_http_methods(["GET"])
def api_categories_list(request):
    """Get all categories"""
    categories = Category.objects.all()
    data = CategorySerializer.serialize_list(categories)
    return JsonResponse({'success': True, 'categories': data})


@require_http_methods(["GET"])
def api_tags_list(request):
    """Get all tags"""
    tags = Tag.objects.all()
    data = TagSerializer.serialize_list(tags)
    return JsonResponse({'success': True, 'tags': data})


# =============================================================================
# API Views - Dashboard Analytics
# =============================================================================

@require_http_methods(["GET"])
def api_dashboard(request):
    """
    Get complete dashboard data including:
    - Summary statistics
    - Prioritized tasks
    - At-risk tasks
    - Charts data
    - Top performers
    """
    try:
        analytics = ProductivityAnalytics()
        priority_engine = TaskPrioritizationEngine()
        risk_engine = RiskPredictionEngine()

        # Summary statistics
        summary = {
            'total_tasks': Task.objects.count(),
            'completed_tasks': Task.objects.filter(status='done').count(),
            'in_progress_tasks': Task.objects.filter(status='in_progress').count(),
            'todo_tasks': Task.objects.filter(status='todo').count(),
            'at_risk_tasks': Task.objects.filter(is_at_risk=True).exclude(
                status__in=['done', 'cancelled']
            ).count(),
            'overdue_tasks': risk_engine.get_overdue_tasks().count(),
            'total_users': User.objects.count(),
            'total_projects': Project.objects.count(),
        }

        # Task lists
        tasks = {
            'prioritized': list(priority_engine.get_prioritized_tasks(limit=20)),
            'at_risk': list(risk_engine.get_at_risk_tasks(min_risk='high')),
            'overdue': list(risk_engine.get_overdue_tasks()),
            'upcoming': list(risk_engine.get_upcoming_deadlines(days=7)),
        }

        # Charts data
        charts = {
            'status_distribution': analytics.get_status_distribution(),
            'completion_trend': analytics.get_task_completion_trend(days=30),
            'task_volume': list(Task.objects.values('priority').annotate(
                count=Count('id')
            ).order_by('priority')),
        }

        # Risks
        risks = {
            'bottlenecks': list(analytics.get_bottleneck_tasks(limit=10)),
            'upcoming_deadlines': list(risk_engine.get_upcoming_deadlines(days=7)),
        }

        # Top performers
        top_performers = list(analytics.get_top_performers(limit=10, days=30))

        dashboard_data = {
            'summary': summary,
            'tasks': tasks,
            'charts': charts,
            'risks': risks,
            'top_performers': top_performers,
        }

        serialized = DashboardSerializer.serialize_dashboard(dashboard_data)
        return JsonResponse({'success': True, 'data': serialized})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }, status=500)


@require_http_methods(["GET"])
def api_analytics_trends(request):
    """
    Get productivity trends data.

    Query params:
    - days: Number of days to look back (default: 30)
    """
    try:
        days = int(request.GET.get('days', 30))
        analytics = ProductivityAnalytics()

        completion_trend = analytics.get_task_completion_trend(days=days)
        status_distribution = analytics.get_status_distribution()

        return JsonResponse({
            'success': True,
            'data': {
                'completion_trend': completion_trend,
                'status_distribution': status_distribution,
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }, status=500)


@require_http_methods(["GET"])
def api_user_stats(request, user_id=None):
    """
    Get productivity statistics for a user.

    Args:
        user_id: User ID (optional, defaults to current user)
    """
    try:
        if user_id:
            user = get_object_or_404(User, id=user_id)
        else:
            user = request.user

        analytics = ProductivityAnalytics()
        stats = analytics.get_user_productivity_stats(user=user)

        # Get user's tasks
        user_tasks = Task.objects.filter(assignee=user)
        completed_count = user_tasks.filter(status='done').count()
        in_progress_count = user_tasks.filter(status='in_progress').count()

        return JsonResponse({
            'success': True,
            'data': {
                'user_id': user.id,
                'username': user.username,
                'total_completed': stats['total_completed'],
                'total_hours': float(stats['total_hours'] or 0),
                'completed_tasks': completed_count,
                'in_progress_tasks': in_progress_count,
                'avg_completion_time': float(stats['avg_completion_time'] or 0),
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }, status=500)


# =============================================================================
# API Views - Reports
# =============================================================================

@require_http_methods(["GET"])
def api_reports_summary(request):
    """
    Get productivity summary report.

    Query params:
    - days: Number of days to include (default: 30)
    """
    try:
        days = int(request.GET.get('days', 30))
        analytics = ProductivityAnalytics()

        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Get completed tasks in period
        completed_tasks = Task.objects.filter(
            status='done',
            completed_at__gte=start_date,
            completed_at__lte=end_date
        )

        total_completed = completed_tasks.count()
        total_hours = completed_tasks.aggregate(
            total=Sum('actual_hours')
        )['total'] or 0

        # On-time completion rate
        on_time_count = completed_tasks.filter(
            completed_at__lte=F('due_date')
        ).count()

        on_time_rate = (on_time_count / total_completed * 100) if total_completed > 0 else 0

        # Average completion time
        avg_completion = completed_tasks.aggregate(
            avg=Avg('actual_hours')
        )['avg'] or 0

        summary = {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days,
            },
            'summary': {
                'total_tasks_completed': total_completed,
                'total_hours_logged': float(total_hours),
                'average_completion_time': float(avg_completion),
                'on_time_completion_rate': float(on_time_rate),
            },
            'top_performers': list(analytics.get_top_performers(limit=10, days=days)),
            'bottlenecks': list(analytics.get_bottleneck_tasks(limit=10)),
            'recommendations': _generate_recommendations(),
            'metrics': {
                'tasks_by_status': analytics.get_status_distribution(),
                'tasks_by_priority': _get_tasks_by_priority(),
                'completion_by_day': analytics.get_task_completion_trend(days=days),
                'tasks_by_category': _get_tasks_by_category(),
            },
        }

        serialized = ReportSerializer.serialize_productivity_report(summary)
        return JsonResponse({'success': True, 'report': serialized})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }, status=500)


# =============================================================================
# API Views - AI Engine Actions
# =============================================================================

@require_http_methods(["POST"])
def api_ai_recalculate(request):
    """
    Manually trigger AI recalculation for all tasks.
    Updates priority scores and risk assessments.
    """
    try:
        result = run_ai_analysis()
        return JsonResponse({
            'success': True,
            'data': result,
            'message': f'Updated {result["priority_updates"]} priorities and {result["risk_updates"]} risk assessments'
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }, status=500)


@require_http_methods(["GET"])
def api_risk_assessment(request):
    """
    Get risk assessment data.

    Query params:
    - min_risk: Minimum risk level (low, medium, high, critical)
    """
    try:
        min_risk = request.GET.get('min_risk', 'high')
        risk_engine = RiskPredictionEngine()

        at_risk_tasks = list(risk_engine.get_at_risk_tasks(min_risk=min_risk))
        overdue_tasks = list(risk_engine.get_overdue_tasks())
        upcoming_deadlines = list(risk_engine.get_upcoming_deadlines(days=7))

        return JsonResponse({
            'success': True,
            'data': {
                'at_risk': TaskSerializer.serialize_list(at_risk_tasks),
                'overdue': TaskSerializer.serialize_list(overdue_tasks),
                'upcoming': TaskSerializer.serialize_list(upcoming_deadlines),
                'total_at_risk': len(at_risk_tasks),
                'total_overdue': len(overdue_tasks),
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }, status=500)


# =============================================================================
# API Views - Work Logs
# =============================================================================

@require_http_methods(["GET"])
def api_work_logs_list(request):
    """
    Get work logs with optional filtering.

    Query params:
    - task: Filter by task ID
    - user: Filter by user ID
    - limit: Limit number of results
    """
    work_logs = WorkLog.objects.select_related('task', 'user')

    task_id = request.GET.get('task')
    if task_id:
        work_logs = work_logs.filter(task_id=task_id)

    user_id = request.GET.get('user')
    if user_id:
        work_logs = work_logs.filter(user_id=user_id)

    work_logs = work_logs.order_by('-logged_at')

    limit = request.GET.get('limit')
    if limit:
        work_logs = work_logs[:int(limit)]

    data = WorkLogSerializer.serialize_list(work_logs)
    return JsonResponse({'success': True, 'work_logs': data})


@require_http_methods(["POST"])
@csrf_exempt
def api_work_log_create(request):
    """Create a new work log entry"""
    try:
        data = json.loads(request.body)

        work_log = WorkLog.objects.create(
            task_id=data['task'],
            user_id=data['user'],
            hours=data['hours'],
            notes=data.get('notes', '')
        )

        # Update task actual hours
        task = work_log.task
        total_hours = task.work_logs.aggregate(
            total=Sum('hours')
        )['total'] or 0
        task.actual_hours = total_hours
        task.save()

        return JsonResponse({
            'success': True,
            'work_log': WorkLogSerializer.serialize(work_log),
            'message': 'Work log created successfully'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


# =============================================================================
# API Views - Users
# =============================================================================

@require_http_methods(["GET"])
def api_users_list(request):
    """Get all users with profile data"""
    users = User.objects.prefetch_related('profile').all()
    data = []
    for user in users:
        if hasattr(user, 'profile'):
            data.append(UserProfileSerializer.serialize(user.profile))

    return JsonResponse({'success': True, 'users': data})


# =============================================================================
# Helper Functions
# =============================================================================

def _generate_recommendations():
    """Generate AI-powered productivity recommendations"""
    recommendations = []

    # Check for overdue tasks
    overdue_count = Task.objects.filter(
        due_date__lt=timezone.now(),
        status__in=['todo', 'in_progress']
    ).count()

    if overdue_count > 0:
        recommendations.append({
            'type': 'warning',
            'priority': 'high',
            'message': f'You have {overdue_count} overdue tasks. Consider reassigning or reprioritizing.'
        })

    # Check for bottlenecks
    from django.db.models import Count
    bottlenecks = Task.objects.annotate(
        blocking_tasks_count=Count('blocking')
    ).filter(
        blocking_tasks_count__gte=3,
        status__in=['todo', 'in_progress']
    ).count()

    if bottlenecks > 0:
        recommendations.append({
            'type': 'info',
            'priority': 'medium',
            'message': f'{bottlenecks} tasks are blocking multiple other tasks. Focus on completing these first.'
        })

    # Check workload distribution
    from django.db.models import Count
    users_with_high_load = User.objects.annotate(
        task_count=Count('assigned_tasks', filter=Q(assigned_tasks__status__in=['todo', 'in_progress']))
    ).filter(task_count__gt=15).count()

    if users_with_high_load > 0:
        recommendations.append({
            'type': 'info',
            'priority': 'medium',
            'message': f'{users_with_high_load} team members have more than 15 active tasks. Consider redistributing workload.'
        })

    return recommendations


def _get_tasks_by_priority():
    """Get task count by priority"""
    return list(Task.objects.values('priority').annotate(
        count=Count('id')
    ).order_by('priority'))


def _get_tasks_by_category():
    """Get task count by category"""
    categories = Category.objects.annotate(
        task_count=Count('tasks')
    ).values('name', 'task_count')

    return {cat['name']: cat['task_count'] for cat in categories}
