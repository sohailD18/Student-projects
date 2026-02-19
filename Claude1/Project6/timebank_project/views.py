from django.shortcuts import render
from django.contrib.auth.models import User
from tasks.models import Task
from credits.models import Transaction
from gamification.models import Badge, UserBadge


def home(request):
    """Home page with platform overview"""
    # Get platform statistics
    total_users = User.objects.count()
    open_tasks = Task.objects.filter(status='Open').count()
    completed_tasks = Task.objects.filter(status='Completed').count()

    # Get recent tasks
    recent_tasks = Task.objects.filter(status='Open').order_by('-created_at')[:6]

    # Get top contributors
    from users.models import Profile
    top_contributors = Profile.objects.select_related('user').order_by(
        '-time_credits_balance'
    )[:5]

    context = {
        'total_users': total_users,
        'open_tasks': open_tasks,
        'completed_tasks': completed_tasks,
        'recent_tasks': recent_tasks,
        'top_contributors': top_contributors,
    }
    return render(request, 'home.html', context)
