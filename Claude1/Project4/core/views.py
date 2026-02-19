from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from datetime import timedelta, datetime
import json
from .forms import ActivityLogForm, UserProfileForm
from .models import ActivityLog, UserProfile, Badge, UserBadge, Challenge, ChallengeParticipant


def staff_required(view_func):
    """Decorator to check if user is staff."""
    return user_passes_test(lambda u: u.is_staff, login_url='dashboard')(view_func)


def custom_login(request):
    """Custom login view that uses our template."""
    from django.contrib.auth.views import LoginView
    from django.contrib.auth.forms import AuthenticationForm

    if request.user.is_authenticated:
        # Redirect admins to admin panel, regular users to dashboard
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin:index')
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            # Redirect admins to admin panel, regular users to dashboard
            if user.is_staff or user.is_superuser:
                return redirect('admin:index')
            return redirect('dashboard')
    else:
        form = AuthenticationForm(request)

    return render(request, 'registration/login.html', {'form': form})


from django.views.decorators.http import require_POST


@require_POST
def custom_logout(request):
    """Custom logout view - requires POST for security."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to EcoTrack!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})


def check_and_award_badges(user, total_points):
    """
    Check if user qualifies for any new badges based on their total points.
    Returns a list of newly awarded badges.
    """
    # Get all badges that user hasn't earned yet
    earned_badge_ids = user.badges.values_list('badge_id', flat=True)
    available_badges = Badge.objects.filter(
        points_required__lte=total_points
    ).exclude(id__in=earned_badge_ids)

    new_badges = []
    for badge in available_badges:
        # Award the badge to the user
        UserBadge.objects.create(user=user, badge=badge)
        new_badges.append(badge)

    return new_badges


@login_required
def log_activity(request):
    if request.method == 'POST':
        form = ActivityLogForm(request.POST)
        if form.is_valid():
            # Save the activity (calculated_carbon is auto-calculated in model save method)
            activity = form.save(commit=False)
            activity.user = request.user
            activity.save()

            # Calculate and add points to user profile
            # Points are based on carbon saved: 1 point per kg of CO2
            points_earned = int(activity.calculated_carbon)
            user_profile = request.user.profile
            user_profile.total_points += points_earned

            # Update streak
            user_profile.update_streak()

            user_profile.save()

            # Check for new badges
            new_badges = check_and_award_badges(request.user, user_profile.total_points)

            # Success message with badge information
            success_message = f'Activity logged successfully! You earned {points_earned} points. '
            success_message += f'Carbon footprint: {activity.calculated_carbon} kg CO2'

            if new_badges:
                badge_names = ', '.join([badge.icon + ' ' + badge.name for badge in new_badges])
                success_message += f'<br><strong>🎉 New Badges Earned: {badge_names}!</strong>'

            messages.success(request, success_message, extra_tags='safe')

            return redirect('dashboard')
    else:
        form = ActivityLogForm()

    return render(request, 'core/log_activity.html', {'form': form})


@login_required
def dashboard(request):
    # Get user's last 7 activities
    recent_activities = ActivityLog.objects.filter(user=request.user)[:7]

    # Get user profile
    profile = request.user.profile

    # Calculate total stats
    total_activities = ActivityLog.objects.filter(user=request.user).count()
    total_carbon = ActivityLog.objects.filter(user=request.user).aggregate(
        total=models.Sum('calculated_carbon')
    )['total'] or 0
    total_points = profile.total_points

    # Get user's earned badges
    earned_badges = UserBadge.objects.filter(user=request.user).select_related('badge')

    # Calculate stats by activity type
    activity_stats = {}
    for activity in ActivityLog.ACTIVITY_TYPES:
        activity_type = activity[0]
        carbon_sum = ActivityLog.objects.filter(
            user=request.user,
            activity_type=activity_type
        ).aggregate(total=models.Sum('calculated_carbon'))['total'] or 0
        count = ActivityLog.objects.filter(
            user=request.user,
            activity_type=activity_type
        ).count()
        activity_stats[activity_type] = {
            'carbon': carbon_sum,
            'count': count
        }

    # Prepare chart data for last 7 days
    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=6)

    # Get daily carbon emissions for the last 7 days - simple approach for SQLite
    daily_emissions = {}
    activities = ActivityLog.objects.filter(
        user=request.user,
        date__gte=seven_days_ago,
        date__lte=today
    )

    # Group by date
    for activity in activities:
        if activity.date not in daily_emissions:
            daily_emissions[activity.date] = 0
        daily_emissions[activity.date] += float(activity.calculated_carbon)

    # Create a complete 7-day range with zero values for days with no activity
    chart_data = []
    chart_labels = []
    for i in range(7):
        date = seven_days_ago + timedelta(days=i)
        date_str = date.strftime('%b %d')  # e.g., "Jan 15"
        chart_labels.append(date_str)

        # Get carbon for this date, or 0 if no activity
        carbon = daily_emissions.get(date, 0)
        chart_data.append(carbon)

    context = {
        'recent_activities': recent_activities,
        'profile': profile,
        'total_activities': total_activities,
        'total_carbon': total_carbon,
        'total_points': total_points,
        'earned_badges': earned_badges,
        'activity_stats': activity_stats,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }

    return render(request, 'core/dashboard.html', context)


@staff_required
def community_stats(request):
    """
    Staff-only view showing community-wide statistics.
    Displays total carbon saved and points earned by all users.
    """
    # Total users
    total_users = User.objects.filter(is_active=True).count()

    # Total activities across all users
    total_activities = ActivityLog.objects.count()

    # Total carbon footprint across all users
    total_carbon = ActivityLog.objects.aggregate(
        total=models.Sum('calculated_carbon')
    )['total'] or 0

    # Total points earned across all users
    total_points = UserProfile.objects.aggregate(
        total=models.Sum('total_points')
    )['total'] or 0

    # Average points per user
    avg_points = UserProfile.objects.aggregate(
        avg=models.Avg('total_points')
    )['avg'] or 0

    # Top 5 users by points
    top_users = UserProfile.objects.select_related('user').order_by('-total_points')[:5]

    # Stats by activity type (community-wide)
    activity_breakdown = {}
    for activity in ActivityLog.ACTIVITY_TYPES:
        activity_type = activity[0]
        carbon_sum = ActivityLog.objects.filter(
            activity_type=activity_type
        ).aggregate(total=models.Sum('calculated_carbon'))['total'] or 0
        count = ActivityLog.objects.filter(
            activity_type=activity_type
        ).count()
        activity_breakdown[activity_type] = {
            'carbon': carbon_sum,
            'count': count
        }

    # Total badges awarded
    total_badges_awarded = UserBadge.objects.count()

    # Most popular badges (most awarded)
    popular_badges = UserBadge.objects.values('badge__name', 'badge__icon').annotate(
        count=models.Count('id')
    ).order_by('-count')[:5]

    # Recent community activities (last 10)
    recent_activities = ActivityLog.objects.select_related('user').order_by('-created_at')[:10]

    # Prepare chart data for community emissions (last 7 days)
    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=6)

    # Get daily carbon emissions - simple approach for SQLite
    daily_emissions = {}
    activities = ActivityLog.objects.filter(
        date__gte=seven_days_ago,
        date__lte=today
    )

    # Group by date
    for activity in activities:
        if activity.date not in daily_emissions:
            daily_emissions[activity.date] = 0
        daily_emissions[activity.date] += float(activity.calculated_carbon)

    chart_data = []
    chart_labels = []
    for i in range(7):
        date = seven_days_ago + timedelta(days=i)
        date_str = date.strftime('%b %d')
        chart_labels.append(date_str)

        carbon = daily_emissions.get(date, 0)
        chart_data.append(carbon)

    context = {
        'total_users': total_users,
        'total_activities': total_activities,
        'total_carbon': total_carbon,
        'total_points': total_points,
        'avg_points': avg_points,
        'top_users': top_users,
        'activity_breakdown': activity_breakdown,
        'total_badges_awarded': total_badges_awarded,
        'popular_badges': popular_badges,
        'recent_activities': recent_activities,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }

    return render(request, 'core/community_stats.html', context)


@login_required
def profile(request):
    """User profile page with editing capabilities."""
    profile = request.user.profile

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)

    # Get user's statistics
    total_activities = ActivityLog.objects.filter(user=request.user).count()
    total_carbon = ActivityLog.objects.filter(user=request.user).aggregate(
        total=models.Sum('calculated_carbon')
    )['total'] or 0

    # Get recent activities
    recent_activities = ActivityLog.objects.filter(user=request.user)[:5]

    # Get badges
    earned_badges = UserBadge.objects.filter(user=request.user).select_related('badge').count()

    context = {
        'form': form,
        'profile': profile,
        'total_activities': total_activities,
        'total_carbon': total_carbon,
        'recent_activities': recent_activities,
        'earned_badges': earned_badges,
    }

    return render(request, 'core/profile.html', context)


@login_required
def leaderboard(request):
    """Global leaderboard showing top users by points."""
    # Get top users by points
    top_users = UserProfile.objects.select_related('user').order_by('-total_points')[:50]

    # Get current user's rank
    try:
        current_user_rank = list(
            UserProfile.objects.select_related('user')
            .order_by('-total_points')
            .values_list('user_id', flat=True)
        ).index(request.user.id) + 1
    except ValueError:
        current_user_rank = None

    # Get statistics around the current user
    if current_user_rank and current_user_rank > 10:
        # Get users around current user's rank
        start_rank = max(1, current_user_rank - 2)
        end_rank = min(current_user_rank + 2, len(top_users))
        surrounding_users = UserProfile.objects.select_related('user').order_by('-total_points')[start_rank-1:end_rank]
    else:
        surrounding_users = []

    context = {
        'top_users': top_users[:10],  # Top 10 users
        'all_users': top_users,  # All top 50 users
        'current_user_rank': current_user_rank,
        'surrounding_users': surrounding_users,
    }

    return render(request, 'core/leaderboard.html', context)
