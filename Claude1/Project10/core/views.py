from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Sum, Avg, Q, F
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta
from .models import Skill, Session, Review
from .forms import SkillForm, BookingForm, ReviewForm
from users.models import UserProfile, Badge

def home(request):
    """Home page view with stats and featured skills"""
    # Get statistics
    users_count = UserProfile.objects.count()
    skills_count = Skill.objects.count()
    sessions_count = Session.objects.filter(status='completed').count()
    badges_count = sum(profile.badges.count() for profile in UserProfile.objects.all())

    # Get category counts
    tech_count = Skill.objects.filter(category='tech').count()
    art_count = Skill.objects.filter(category='art').count()
    language_count = Skill.objects.filter(category='language').count()
    music_count = Skill.objects.filter(category='music').count()

    # Get featured skills (most booked or recently created)
    featured_skills = Skill.objects.annotate(
        booking_count=Count('sessions')
    ).order_by('-booking_count', '-created_at')[:6]

    context = {
        'users_count': users_count,
        'skills_count': skills_count,
        'sessions_count': sessions_count,
        'badges_count': badges_count,
        'tech_count': tech_count,
        'art_count': art_count,
        'language_count': language_count,
        'music_count': music_count,
        'featured_skills': featured_skills,
    }
    return render(request, 'core/home.html', context)

def skill_list(request):
    """List all available skills with search functionality"""
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')

    skills = Skill.objects.all()

    # Search by title or description
    if query:
        skills = skills.filter(title__icontains=query) | skills.filter(description__icontains=query)

    # Filter by category
    if category:
        skills = skills.filter(category=category)

    # Get all categories for the filter dropdown
    categories = Skill.CATEGORY_CHOICES

    return render(request, 'core/skill_list.html', {
        'skills': skills,
        'query': query,
        'selected_category': category,
        'categories': categories
    })

def skill_detail(request, skill_id):
    """Show details of a specific skill"""
    skill = get_object_or_404(Skill, id=skill_id)
    return render(request, 'core/skill_detail.html', {'skill': skill})

@login_required
def create_skill(request):
    """Create a new skill listing - Accessible to all (students become teachers by creating)"""
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.teacher = request.user
            skill.save()
            messages.success(request, f'Your skill "{skill.title}" has been posted successfully!')
            return redirect('users:teacher_dashboard')
    else:
        form = SkillForm()

    return render(request, 'core/create_skill.html', {'form': form})

@login_required
def update_skill(request, skill_id):
    """Update an existing skill listing - TEACHER ONLY"""
    skill = get_object_or_404(Skill, id=skill_id)

    # Only the teacher who created the skill can update it
    if skill.teacher != request.user:
        messages.error(request, 'You can only edit your own skill listings.')
        return redirect('core:skill_detail', skill_id=skill.id)

    # Check if user is a teacher (has skills) - block pure students
    if not request.user.skills_teaching.exists():
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('core:home')

    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, f'Your skill "{skill.title}" has been updated successfully!')
            return redirect('users:teacher_dashboard')
    else:
        form = SkillForm(instance=skill)

    return render(request, 'core/update_skill.html', {'form': form, 'skill': skill})

@login_required
def book_session(request, skill_id):
    """Book a session for a skill with a form - Accessible to all (peer-to-peer)"""
    skill = get_object_or_404(Skill, id=skill_id)

    # Prevent users from booking their own skills
    if skill.teacher == request.user:
        messages.error(request, 'You cannot book your own skill!')
        return redirect('core:skill_detail', skill_id=skill.id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            session = Session.objects.create(
                skill=skill,
                student=request.user,
                teacher=skill.teacher,
                scheduled_time=form.cleaned_data['scheduled_time'],
                status='pending'
            )
            messages.success(request, 'Session booking request sent successfully!')
            # Redirect based on role
            if request.user.skills_teaching.exists():
                return redirect('core:teacher_sessions')
            else:
                return redirect('core:student_sessions')
    else:
        form = BookingForm()

    return render(request, 'core/book_session.html', {
        'skill': skill,
        'form': form
    })

@login_required
def session_list(request):
    """List user's sessions (both as student and teacher)"""
    learning_sessions = Session.objects.filter(student=request.user)
    teaching_sessions = Session.objects.filter(teacher=request.user)
    return render(request, 'core/session_list.html', {
        'learning_sessions': learning_sessions,
        'teaching_sessions': teaching_sessions
    })


@login_required
def teacher_sessions(request):
    """List all teaching sessions - TEACHER ONLY"""
    # BLOCK students - only users with skills can access
    if not request.user.skills_teaching.exists():
        messages.error(request, 'You do not have permission to access this page. Only teachers can access this page.')
        return redirect('core:home')

    teaching_sessions = Session.objects.filter(
        teacher=request.user
    ).select_related('skill', 'student')

    return render(request, 'core/teacher_sessions.html', {
        'teaching_sessions': teaching_sessions
    })


@login_required
def student_sessions(request):
    """List all learning sessions - STUDENT ONLY"""
    # BLOCK teachers - only users WITHOUT skills can access
    if request.user.skills_teaching.exists():
        messages.error(request, 'Access denied. This page is for students only. Please use your teacher dashboard.')
        return redirect('users:teacher_dashboard')

    learning_sessions = Session.objects.filter(
        student=request.user
    ).select_related('skill', 'teacher')

    return render(request, 'core/student_sessions.html', {
        'learning_sessions': learning_sessions
    })

@login_required
def session_detail(request, session_id):
    """Show details of a specific session - accessible to both student and teacher"""
    session = get_object_or_404(Session, id=session_id)

    # Check if user is either the student or the teacher
    if session.student != request.user and session.teacher != request.user:
        messages.error(request, 'You do not have permission to view this session.')
        if request.user.skills_teaching.exists():
            return redirect('core:teacher_sessions')
        else:
            return redirect('core:student_sessions')

    # Determine what actions are available to the current user
    is_teacher = (session.teacher == request.user)
    is_student = (session.student == request.user)

    return render(request, 'core/session_detail.html', {
        'session': session,
        'is_teacher': is_teacher,
        'is_student': is_student
    })

@login_required
def update_session_status(request, session_id):
    """Update session status - cancel session"""
    session = get_object_or_404(Session, id=session_id)

    # Only teacher or student can cancel
    if session.teacher != request.user and session.student != request.user:
        messages.error(request, 'You do not have permission to modify this session.')
        return redirect('core:home')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status == 'cancelled':
            session.status = new_status
            session.save()
            messages.success(request, 'Session cancelled successfully!')

    # Redirect based on role
    if session.teacher == request.user:
        return redirect('core:teacher_sessions')
    else:
        return redirect('core:student_sessions')


@login_required
def accept_session(request, session_id):
    """Accept a pending session booking - TEACHER ONLY"""
    session = get_object_or_404(Session, id=session_id)

    # BLOCK students - only users with skills can access
    if not request.user.skills_teaching.exists():
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('core:home')

    # Only the session teacher can accept
    if session.teacher != request.user:
        messages.error(request, 'Only the teacher of this session can accept it.')
        return redirect('core:teacher_sessions')

    # Can only accept pending sessions
    if session.status != 'pending':
        messages.error(request, 'This session has already been processed.')
        return redirect('core:teacher_sessions')

    if request.method == 'POST':
        session.status = 'accepted'
        session.save()
        messages.success(request, 'Session accepted! Awaiting completion.')

    return redirect('core:teacher_sessions')


@login_required
def complete_session(request, session_id):
    """Mark a session as completed with optional review - both student and teacher can do this"""
    session = get_object_or_404(Session, id=session_id)

    # Check if user is either student or teacher
    if session.student != request.user and session.teacher != request.user:
        messages.error(request, 'You do not have permission to modify this session.')
        return redirect('core:home')

    # Can only complete accepted sessions
    if session.status != 'accepted':
        messages.error(request, 'You can only complete accepted sessions.')
        # Redirect based on role
        if session.teacher == request.user:
            return redirect('core:teacher_sessions')
        else:
            return redirect('core:student_sessions')

    if request.method == 'POST':
        # Check if already completed to prevent duplicate point awards
        if session.status == 'completed':
            messages.warning(request, 'This session is already completed.')
            # Redirect based on role
            if session.teacher == request.user:
                return redirect('core:teacher_sessions')
            else:
                return redirect('core:student_sessions')

        session.status = 'completed'
        session.save()
        # Signal will automatically award points to both teacher and student

        # Handle review submission (only from student)
        if session.student == request.user:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.session = session
                review.reviewer = request.user
                review.save()
                messages.success(request, f'Session marked as completed! Points awarded: Teacher (+{session.skill.hourly_rate_points}), Student (+10). Review saved!')
            else:
                messages.success(request, f'Session marked as completed! Points awarded: Teacher (+{session.skill.hourly_rate_points}), Student (+10)')
        else:
            messages.success(request, f'Session marked as completed! Points awarded: Teacher (+{session.skill.hourly_rate_points}), Student (+10)')

    # Redirect based on role
    if session.teacher == request.user:
        return redirect('core:teacher_sessions')
    else:
        return redirect('core:student_sessions')


@staff_member_required
def admin_analytics(request):
    """
    Admin dashboard with analytics:
    - Top contributors (teachers by sessions/completed)
    - Active skills (most booked)
    - Engagement trends
    - Platform statistics
    """
    # Calculate date ranges
    today = timezone.now()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)

    # Overall Statistics
    total_users = UserProfile.objects.count()
    total_skills = Skill.objects.count()
    total_sessions = Session.objects.count()
    total_reviews = Review.objects.count()

    # Status breakdown
    pending_sessions = Session.objects.filter(status='pending').count()
    accepted_sessions = Session.objects.filter(status='accepted').count()
    completed_sessions = Session.objects.filter(status='completed').count()
    cancelled_sessions = Session.objects.filter(status='cancelled').count()

    # Top Contributors (Teachers) - by completed sessions and points earned
    top_teachers_by_sessions = UserProfile.objects.filter(
        user__sessions_teaching__status='completed'
    ).annotate(
        completed_sessions_count=Count('user__sessions_teaching', filter=Q(user__sessions_teaching__status='completed'))
    ).order_by('-completed_sessions_count')[:10]

    top_teachers_by_points = UserProfile.objects.all().order_by('-points_earned')[:10]

    # Top Students (by learning activity)
    top_students = UserProfile.objects.filter(
        user__sessions_learning__status='completed'
    ).annotate(
        completed_learning_sessions=Count('user__sessions_learning', filter=Q(user__sessions_learning__status='completed'))
    ).order_by('-completed_learning_sessions')[:10]

    # Active Skills (most booked)
    active_skills = Skill.objects.annotate(
        booking_count=Count('sessions')
    ).order_by('-booking_count')[:10]

    # Highest Rated Skills (teachers with reviews)
    highly_rated_skills = Skill.objects.filter(
        sessions__review__isnull=False
    ).annotate(
        avg_rating=Avg('sessions__review__rating'),
        review_count=Count('sessions__review')
    ).order_by('-avg_rating')[:10]

    # Category Distribution
    category_stats = Skill.objects.values('category').annotate(
        count=Count('id')
    ).order_by('-count')

    # Engagement Trends (Last 30 days)
    new_users_last_30 = UserProfile.objects.filter(user__date_joined__gte=last_30_days).count()

    # Recent Activity (Last 7 days)
    recent_completions = Session.objects.filter(
        status='completed',
        updated_at__gte=last_7_days
    ).count() * 2  # Multiply by 2 for teacher + student activity

    pending_bookings = Session.objects.filter(
        status='pending',
        created_at__gte=last_7_days
    ).count()

    # Top Badge Earners
    top_badge_earners = UserProfile.objects.annotate(
        badge_count=Count('badges')
    ).order_by('-badge_count')[:10]

    # Skills needing attention (no bookings)
    skills_no_bookings = Skill.objects.filter(
        sessions__isnull=True
    ).count()

    # Average rating across platform
    avg_platform_rating = Review.objects.aggregate(
        avg_rating=Avg('rating')
    )['avg_rating'] or 0

    context = {
        # Overall Stats
        'total_users': total_users,
        'total_skills': total_skills,
        'total_sessions': total_sessions,
        'total_reviews': total_reviews,
        'pending_sessions': pending_sessions,
        'accepted_sessions': accepted_sessions,
        'completed_sessions': completed_sessions,
        'cancelled_sessions': cancelled_sessions,

        # Top Contributors
        'top_teachers_by_sessions': top_teachers_by_sessions,
        'top_teachers_by_points': top_teachers_by_points,
        'top_students': top_students,

        # Active Skills
        'active_skills': active_skills,
        'highly_rated_skills': highly_rated_skills,

        # Categories
        'category_stats': category_stats,

        # Engagement
        'new_users_last_30': new_users_last_30,
        'recent_completions': recent_completions,
        'pending_bookings': pending_bookings,
        'skills_no_bookings': skills_no_bookings,

        # Badges
        'top_badge_earners': top_badge_earners,

        # Platform Health
        'avg_platform_rating': round(avg_platform_rating, 1),

        # Date info
        'last_30_days': last_30_days,
        'last_7_days': last_7_days,
    }

    return render(request, 'core/admin_analytics.html', context)
