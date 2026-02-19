from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from .models import Badge, UserBadge
from users.models import Profile


@login_required
def leaderboard(request):
    """Display leaderboard of top users by credit balance"""
    # Get top 10 users by credit balance
    top_users = Profile.objects.select_related('user').order_by(
        '-time_credits_balance'
    )[:10]

    context = {
        'top_users': top_users,
    }
    return render(request, 'gamification/leaderboard.html', context)


@login_required
def badges_list(request):
    """Display all available badges and user's earned badges"""
    all_badges = Badge.objects.all()
    user_badges = UserBadge.objects.filter(user=request.user).select_related('badge')

    earned_badge_ids = [ub.badge_id for ub in user_badges]

    context = {
        'all_badges': all_badges,
        'user_badges': user_badges,
        'earned_badge_ids': earned_badge_ids,
    }
    return render(request, 'gamification/badges_list.html', context)


def platform_stats(request):
    """Display platform statistics for public view"""
    from django.contrib.auth.models import User
    from tasks.models import Task
    from credits.models import Transaction

    total_users = User.objects.count()
    total_tasks = Task.objects.count()
    completed_tasks = Task.objects.filter(status='Completed').count()
    total_hours = Transaction.objects.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'total_users': total_users,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'total_hours': total_hours,
    }
    return render(request, 'gamification/platform_stats.html', context)
