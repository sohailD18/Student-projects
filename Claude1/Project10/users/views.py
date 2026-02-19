from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import User
from .models import UserProfile, Badge
from core.models import Session

@login_required
def dashboard(request):
    """Route users to appropriate dashboard based on their role"""
    # Admin users go to admin dashboard
    if request.user.is_staff or request.user.is_superuser:
        return redirect('users:admin_dashboard')

    # Check if user has any skills they're teaching
    is_teacher = request.user.skills_teaching.exists()

    if is_teacher:
        return redirect('users:teacher_dashboard')
    else:
        return redirect('users:student_dashboard')


@login_required
def admin_dashboard(request):
    """Admin dashboard with platform overview"""
    if not request.user.is_staff and not request.user.is_superuser:
        messages.warning(request, 'You do not have permission to access the admin dashboard.')
        return redirect('core:home')

    from core.models import Skill

    profile = getattr(request.user, 'profile', None)
    if not profile:
        profile = UserProfile.objects.create(user=request.user)

    # Platform stats
    total_users = User.objects.count()
    total_skills = Skill.objects.count()
    total_sessions = Session.objects.count()
    completed_sessions = Session.objects.filter(status='completed').count()

    # Get all available badges
    all_badges = Badge.objects.all()
    earned_badges = profile.badges.all()
    available_badges = all_badges.exclude(id__in=earned_badges)

    context = {
        'profile': profile,
        'user': request.user,
        'total_users': total_users,
        'total_skills': total_skills,
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'earned_badges': earned_badges,
        'available_badges': available_badges,
    }
    return render(request, 'users/admin_dashboard.html', context)


@login_required
def teacher_dashboard(request):
    """Teacher dashboard for managing skills and teaching sessions"""
    profile = getattr(request.user, 'profile', None)
    if not profile:
        profile = UserProfile.objects.create(user=request.user)

    # Check and award new badges
    new_badges_count = profile.check_and_award_badges()
    if new_badges_count > 0:
        messages.success(request, f'Congratulations! You earned {new_badges_count} new badge(s)!')

    # Get skills taught by this user
    skills_teaching = request.user.skills_teaching.all()

    # Get teaching sessions
    teaching_sessions = Session.objects.filter(
        teacher=request.user
    ).select_related('skill', 'student')

    # Calculate teaching stats
    completed_teaching = teaching_sessions.filter(status='completed').count()
    total_teaching = teaching_sessions.count()
    total_earned_points = completed_teaching * 50  # Approximate

    # Get upcoming teaching sessions
    now = timezone.now()
    upcoming_teaching = teaching_sessions.filter(
        scheduled_time__gt=now,
        status__in=['pending', 'accepted']
    )

    # Get all available badges
    all_badges = Badge.objects.all()
    earned_badges = profile.badges.all()
    available_badges = all_badges.exclude(id__in=earned_badges)

    context = {
        'profile': profile,
        'user': request.user,
        'skills_teaching': skills_teaching,
        'teaching_sessions': teaching_sessions,
        'upcoming_teaching': upcoming_teaching,
        'completed_teaching': completed_teaching,
        'total_teaching': total_teaching,
        'total_earned_points': total_earned_points,
        'earned_badges': earned_badges,
        'available_badges': available_badges,
    }
    return render(request, 'users/teacher_dashboard.html', context)


@login_required
def student_dashboard(request):
    """Student dashboard for learning sessions and progress"""
    profile = getattr(request.user, 'profile', None)
    if not profile:
        profile = UserProfile.objects.create(user=request.user)

    # Check and award new badges
    new_badges_count = profile.check_and_award_badges()
    if new_badges_count > 0:
        messages.success(request, f'Congratulations! You earned {new_badges_count} new badge(s)!')

    # Get learning sessions
    learning_sessions = Session.objects.filter(
        student=request.user
    ).select_related('skill', 'teacher')

    # Calculate learning stats
    completed_learning = learning_sessions.filter(status='completed').count()
    total_learning = learning_sessions.count()

    # Get upcoming learning sessions
    now = timezone.now()
    upcoming_learning = learning_sessions.filter(
        scheduled_time__gt=now,
        status__in=['pending', 'accepted']
    )

    # Get all available badges
    all_badges = Badge.objects.all()
    earned_badges = profile.badges.all()
    available_badges = all_badges.exclude(id__in=earned_badges)

    context = {
        'profile': profile,
        'user': request.user,
        'learning_sessions': learning_sessions,
        'upcoming_learning': upcoming_learning,
        'completed_learning': completed_learning,
        'total_learning': total_learning,
        'earned_badges': earned_badges,
        'available_badges': available_badges,
    }
    return render(request, 'users/student_dashboard.html', context)

def profile_view(request, username):
    """View another user's profile"""
    user = get_object_or_404(User, username=username)
    profile = getattr(user, 'profile', None)

    context = {
        'profile_user': user,
        'profile': profile,
        'skills': user.skills_teaching.all(),
    }
    return render(request, 'users/profile.html', context)

@login_required
def profile_update(request):
    """Update your own profile"""
    profile = getattr(request.user, 'profile', None)
    if not profile:
        profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        profile.bio = request.POST.get('bio', '')
        profile.skills_to_teach = request.POST.get('skills_to_teach', '')
        profile.skills_to_learn = request.POST.get('skills_to_learn', '')
        profile.save()
        messages.success(request, 'Profile updated successfully!')

        # Redirect to appropriate dashboard based on role
        if request.user.is_staff or request.user.is_superuser:
            return redirect('users:admin_dashboard')
        elif request.user.skills_teaching.exists():
            return redirect('users:teacher_dashboard')
        else:
            return redirect('users:student_dashboard')

    return render(request, 'users/profile_update.html', {'profile': profile})

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('core:home')
    else:
        form = UserCreationForm()

    return render(request, 'users/register.html', {'form': form})


def custom_login(request):
    """Custom login view"""
    if request.user.is_authenticated:
        return redirect('users:dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')

            # Check if there's a next parameter, redirect there first
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)

            # Check if user is admin/staff and redirect to appropriate dashboard
            if user.is_staff or user.is_superuser:
                return redirect('users:admin_dashboard')
            else:
                # Regular user redirect to dashboard (will route to teacher/student)
                return redirect('users:dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form})


def custom_logout(request):
    """Custom logout view"""
    # Add message before logout to ensure it persists
    messages.success(request, 'You have been logged out successfully.')
    logout(request)
    return redirect('core:home')
