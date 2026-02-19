from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator
from jobs.models import Job, JobApplication, JobCategory, SavedJob
from accounts.models import UserProfile
from django.contrib.auth.models import User


@staff_member_required
def admin_home(request):
    """Custom admin home page with app list"""
    apps = [
        {
            'name': 'Jobs',
            'app_label': 'jobs',
            'models': [
                {'name': 'Jobs', 'url': '/admin-panel/jobs/', 'icon': 'briefcase', 'count': Job.objects.count()},
                {'name': 'Job Applications', 'url': '/admin-panel/applications/', 'icon': 'users', 'count': JobApplication.objects.count()},
                {'name': 'Job Categories', 'url': '/admin-panel/categories/', 'icon': 'folder', 'count': JobCategory.objects.count()},
                {'name': 'Saved Jobs', 'url': '/admin-panel/saved-jobs/', 'icon': 'heart', 'count': SavedJob.objects.count()},
            ]
        },
        {
            'name': 'Accounts',
            'app_label': 'accounts',
            'models': [
                {'name': 'User Profiles', 'url': '/admin-panel/user-profiles/', 'icon': 'user-circle', 'count': UserProfile.objects.count()},
            ]
        },
    ]

    # Get statistics from main home page
    total_jobs = Job.objects.count()
    total_companies = Job.objects.values_list('company', flat=True).distinct().count()
    categories = JobCategory.objects.all()

    # Get recent active jobs (showing most recent instead of featured)
    recent_jobs = Job.objects.filter(status='active').select_related('category').order_by('-created_at')[:6]

    context = {
        'apps': apps,
        'title': 'Site Administration',
        'total_jobs': total_jobs,
        'total_companies': total_companies,
        'categories': categories,
        'recent_jobs': recent_jobs,
    }
    return render(request, 'admin/admin_home.html', context)


@staff_member_required
def admin_jobs_list(request):
    """Custom jobs list view"""
    jobs = Job.objects.all().select_related('category', 'created_by')

    # Search
    search = request.GET.get('search', '')
    if search:
        jobs = jobs.filter(Q(title__icontains=search) | Q(company__icontains=search))

    # Filter by status
    status = request.GET.get('status')
    if status:
        jobs = jobs.filter(status=status)

    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        jobs = jobs.filter(category_id=category_id)

    # Pagination
    paginator = Paginator(jobs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get application counts for all jobs in this page
    job_ids = [job.id for job in page_obj]
    app_counts = JobApplication.objects.filter(job_id__in=job_ids).values('job_id').annotate(count=Count('id'))
    app_count_dict = {item['job_id']: item['count'] for item in app_counts}

    categories = JobCategory.objects.all()

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search': search,
        'status': status,
        'category_id': category_id,
        'app_count_dict': app_count_dict,
        'title': 'Jobs',
    }
    return render(request, 'admin/jobs_list.html', context)


@staff_member_required
def admin_applications_list(request):
    """Custom applications list view"""
    applications = JobApplication.objects.all().select_related('job', 'job__category')

    # Search
    search = request.GET.get('search', '')
    if search:
        applications = applications.filter(
            Q(applicant_name__icontains=search) |
            Q(email__icontains=search) |
            Q(job__title__icontains=search)
        )

    # Filter by status
    status = request.GET.get('status')
    if status:
        applications = applications.filter(status=status)

    # Filter by job
    job_id = request.GET.get('job')
    if job_id:
        applications = applications.filter(job_id=job_id)

    # Filter by company
    company = request.GET.get('company')
    if company:
        applications = applications.filter(job__company=company)

    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        applications = applications.filter(job__category_id=category_id)

    # Pagination
    paginator = Paginator(applications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    jobs = Job.objects.all()
    statuses = JobApplication.STATUS_CHOICES
    categories = JobCategory.objects.all()
    companies = Job.objects.values_list('company', flat=True).distinct().order_by('company')

    context = {
        'page_obj': page_obj,
        'jobs': jobs,
        'statuses': statuses,
        'categories': categories,
        'companies': companies,
        'search': search,
        'status': status,
        'job_id': job_id,
        'company': company,
        'category_id': category_id,
        'title': 'Job Applications',
    }
    return render(request, 'admin/applications_list.html', context)


@staff_member_required
def admin_categories_list(request):
    """Custom categories list view"""
    categories = JobCategory.objects.all().annotate(job_count=Count('jobs')).order_by('name')

    # Search
    search = request.GET.get('search', '')
    if search:
        categories = categories.filter(name__icontains=search)

    # Pagination
    paginator = Paginator(categories, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search': search,
        'title': 'Job Categories',
    }
    return render(request, 'admin/categories_list.html', context)


@staff_member_required
def admin_user_profiles_list(request):
    """Custom user profiles list view"""
    profiles = UserProfile.objects.all().select_related('user').order_by('-user__date_joined')

    # Search
    search = request.GET.get('search', '')
    if search:
        profiles = profiles.filter(
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search) |
            Q(company__icontains=search)
        )

    # Filter by user type
    user_type = request.GET.get('user_type')
    if user_type:
        profiles = profiles.filter(user_type=user_type)

    # Pagination
    paginator = Paginator(profiles, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search': search,
        'user_type': user_type,
        'title': 'User Profiles',
    }
    return render(request, 'admin/user_profiles_list.html', context)


@staff_member_required
def admin_users_list(request):
    """Custom users list view"""
    users = User.objects.all().annotate(job_count=Count('posted_jobs')).order_by('-date_joined')

    # Search
    search = request.GET.get('search', '')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )

    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search': search,
        'title': 'Users',
    }
    return render(request, 'admin/users_list.html', context)


@staff_member_required
def delete_job(request, job_id):
    """Delete a job"""
    job = get_object_or_404(Job, id=job_id)
    job.delete()
    messages.success(request, f'Job "{job.title}" has been deleted.')
    return redirect('/admin-panel/jobs/')


@staff_member_required
def admin_application_detail(request, application_id):
    """View application details"""
    application = get_object_or_404(JobApplication, id=application_id)

    context = {
        'application': application,
        'title': f'Application - {application.applicant_name}',
    }
    return render(request, 'admin/application_detail.html', context)


@staff_member_required
def delete_application(request, application_id):
    """Delete an application"""
    application = get_object_or_404(JobApplication, id=application_id)
    application.delete()
    messages.success(request, f'Application from "{application.applicant_name}" has been deleted.')
    return redirect('/admin-panel/applications/')


@staff_member_required
def admin_saved_jobs_list(request):
    """Custom saved jobs list view"""
    saved_jobs = SavedJob.objects.all().select_related('job', 'job__category', 'user')

    # Search
    search = request.GET.get('search', '')
    if search:
        saved_jobs = saved_jobs.filter(
            Q(user__username__icontains=search) |
            Q(job__title__icontains=search) |
            Q(job__company__icontains=search)
        )

    # Pagination
    paginator = Paginator(saved_jobs.order_by('-created_at'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search': search,
        'title': 'Saved Jobs',
    }
    return render(request, 'admin/saved_jobs_list.html', context)
