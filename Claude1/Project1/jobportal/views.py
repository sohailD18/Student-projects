from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from jobs.models import Job, JobApplication, JobCategory, SavedJob
from accounts.models import UserProfile
from django.contrib.auth.models import User


@staff_member_required
def custom_admin_dashboard(request):
    """Custom admin dashboard with statistics"""

    # Get current user's jobs (if employer) or all jobs (if superuser)
    if request.user.is_superuser:
        base_jobs = Job.objects.all()
        base_applications = JobApplication.objects.all()
    else:
        base_jobs = Job.objects.filter(created_by=request.user)
        base_applications = JobApplication.objects.filter(job__created_by=request.user)

    # Statistics
    total_jobs = base_jobs.count()
    active_jobs = base_jobs.filter(status='active').count()
    total_applications = base_applications.count()
    pending_applications = base_applications.filter(status='pending').count()

    # Recent activity
    recent_jobs = base_jobs.order_by('-created_at')[:5]
    recent_applications = base_applications.select_related('job').order_by('-applied_at')[:10]

    # Application status breakdown
    status_stats = base_applications.values('status').annotate(count=Count('id'))

    # Job type breakdown
    job_type_stats = base_jobs.values('job_type').annotate(count=Count('id'))

    # Jobs by category (for superuser)
    category_stats = None
    if request.user.is_superuser:
        category_stats = Job.objects.values('category__name').annotate(count=Count('id')).order_by('-count')[:10]

    # Recent users (for superuser)
    recent_users = None
    if request.user.is_superuser:
        recent_users = User.objects.order_by('-date_joined')[:5]

    # Statistics for last 7 days
    seven_days_ago = timezone.now() - timedelta(days=7)
    jobs_this_week = base_jobs.filter(created_at__gte=seven_days_ago).count()
    applications_this_week = base_applications.filter(applied_at__gte=seven_days_ago).count()

    # Top performing jobs (most applications)
    top_jobs = base_jobs.annotate(app_count=Count('applications')).order_by('-app_count')[:5]

    context = {
        'title': 'Dashboard',
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'recent_jobs': recent_jobs,
        'recent_applications': recent_applications,
        'status_stats': status_stats,
        'job_type_stats': job_type_stats,
        'category_stats': category_stats,
        'recent_users': recent_users,
        'jobs_this_week': jobs_this_week,
        'applications_this_week': applications_this_week,
        'top_jobs': top_jobs,
        'is_superuser': request.user.is_superuser,
    }

    return render(request, 'admin/custom_dashboard.html', context)
