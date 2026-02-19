from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from .forms import CustomUserCreationForm, UserProfileForm
from .models import UserProfile
from jobs.models import Job, JobApplication, Skill, CandidateSkill


def custom_login(request):
    """Custom login view"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', 'accounts:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


def custom_register(request):
    """Custom registration view"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully for {username}!')

            # Auto-login after registration
            user = authenticate(username=username, password=form.cleaned_data.get('password1'))
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome to JobPortal, {username}!')
                return redirect('accounts:dashboard')

            return redirect('accounts:login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def custom_logout(request):
    """Custom logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def dashboard(request):
    """Dashboard view - redirects to appropriate dashboard based on user type"""
    # Admin users (staff/superuser) go to admin panel
    if request.user.is_staff or request.user.is_superuser:
        return redirect('/admin-panel/')

    try:
        profile = request.user.profile

        # Employers go to Employer Dashboard
        if profile.is_employer:
            return redirect('accounts:employer_dashboard')
        else:
            # Job Seekers go to home page (job portal)
            return redirect('jobs:home')
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        UserProfile.objects.create(user=request.user)
        # After creating profile, redirect to home (will be job_seeker by default)
        return redirect('jobs:home')


@login_required
def job_seeker_dashboard(request):
    """Job seeker dashboard"""
    # Get user's applications
    applications = JobApplication.objects.filter(
        email=request.user.email
    ).select_related('job').order_by('-applied_at')[:5]

    # Get saved jobs
    saved_jobs = request.user.saved_jobs.all().select_related('job')[:5]

    # Recommended jobs (jobs in categories user has applied to)
    applied_categories = JobApplication.objects.filter(
        email=request.user.email
    ).values_list('job__category_id', flat=True).distinct()

    recommended_jobs = Job.objects.filter(
        status='active',
        category_id__in=applied_categories
    ).exclude(
        applications__email=request.user.email
    ).order_by('-created_at')[:5]

    context = {
        'applications': applications,
        'saved_jobs': saved_jobs,
        'recommended_jobs': recommended_jobs,
        'total_applications': JobApplication.objects.filter(email=request.user.email).count(),
        'total_saved': request.user.saved_jobs.count(),
    }
    return render(request, 'accounts/job_seeker_dashboard.html', context)


@login_required
def employer_dashboard(request):
    """Employer dashboard"""
    # Check if user is an employer
    try:
        profile = request.user.profile
        if not profile.is_employer:
            messages.warning(request, 'Access denied. Employer dashboard is for employers only.')
            return redirect('jobs:home')
    except UserProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('accounts:profile')

    # Get search and filter parameters
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    job_filter = request.GET.get('job', '')

    # Get user's posted jobs
    posted_jobs = Job.objects.filter(
        created_by=request.user
    ).order_by('-created_at')

    # Build applications query with filters
    applications = JobApplication.objects.filter(
        job__created_by=request.user
    ).select_related('job', 'job__category').order_by('-applied_at')

    # Apply search filter
    if search:
        applications = applications.filter(
            Q(applicant_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )

    # Apply status filter
    if status_filter:
        applications = applications.filter(status=status_filter)

    # Apply job filter
    if job_filter:
        applications = applications.filter(job_id=job_filter)

    # Get recent applications (for top section)
    recent_applications = applications[:10]

    # Get all applications for filtering
    all_applications = applications

    # Statistics
    total_jobs = posted_jobs.count()
    active_jobs = posted_jobs.filter(status='active').count()
    total_applications = JobApplication.objects.filter(
        job__created_by=request.user
    ).count()

    pending_applications = JobApplication.objects.filter(
        job__created_by=request.user,
        status='pending'
    ).count()

    # Status choices for filter
    statuses = JobApplication.STATUS_CHOICES

    context = {
        'posted_jobs': posted_jobs[:5],
        'recent_applications': recent_applications,
        'all_applications': all_applications,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'jobs': posted_jobs,
        'statuses': statuses,
        'search': search,
        'status_filter': status_filter,
        'job_filter': job_filter,
    }
    return render(request, 'accounts/employer_dashboard.html', context)


@login_required
def profile(request):
    """User profile view"""
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)

    # Check if user is an employer
    is_employer = user_profile.is_employer

    # Get user's skills and all available skills
    skills = user_profile.candidate_skills.select_related('skill').all()
    all_skills = Skill.objects.all().order_by('name')

    if request.method == 'POST':
        # Update user fields
        user = request.user
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.save()

        # Update profile fields
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            if is_employer:
                return redirect('accounts:employer_profile')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=user_profile)

    context = {
        'form': form,
        'user_profile': user_profile,
        'skills': skills,
        'all_skills': all_skills,
    }

    # Render employer-specific template if user is employer
    if is_employer:
        return render(request, 'accounts/employer_profile.html', context)
    return render(request, 'accounts/profile.html', context)


@login_required
def employer_profile(request):
    """Employer profile view (redirects to profile with employer template)"""
    return profile(request)
