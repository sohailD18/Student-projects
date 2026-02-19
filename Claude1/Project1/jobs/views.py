from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
import os
from .models import (
    Job, JobCategory, JobApplication, SavedJob, CandidateRecommendation, JobMatch,
    InterviewSession, InterviewQuestion, InterviewResponse, Notification
)
from .forms import JobForm, JobApplicationForm
from .services.matchmaker import JobMatchmaker
from .services.interview_bot import InterviewBot
from accounts.models import UserProfile


def home(request):
    """Home page with featured jobs and statistics"""
    featured_jobs = Job.objects.filter(status='active').order_by('-created_at')[:6]
    categories = JobCategory.objects.all()
    total_jobs = Job.objects.filter(status='active').count()
    total_companies = Job.objects.filter(status='active').values('company').distinct().count()

    context = {
        'featured_jobs': featured_jobs,
        'categories': categories,
        'total_jobs': total_jobs,
        'total_companies': total_companies,
    }
    return render(request, 'jobs/home.html', context)


def job_list(request):
    """List all active jobs with filtering and search"""
    jobs = Job.objects.filter(status='active')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Category filter
    category_id = request.GET.get('category')
    if category_id:
        jobs = jobs.filter(category_id=category_id)

    # Job type filter
    job_type = request.GET.get('job_type')
    if job_type:
        jobs = jobs.filter(job_type=job_type)

    # Experience level filter
    experience_level = request.GET.get('experience_level')
    if experience_level:
        jobs = jobs.filter(experience_level=experience_level)

    # Location filter
    location = request.GET.get('location')
    if location:
        jobs = jobs.filter(location__icontains=location)

    # Pagination
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = JobCategory.objects.all()

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
        'selected_job_type': job_type,
        'selected_experience': experience_level,
        'selected_location': location,
    }
    return render(request, 'jobs/job_list.html', context)


def job_detail(request, job_id):
    """Display job details and application form"""
    job = get_object_or_404(Job, id=job_id, status='active')

    # Increment view count
    job.views_count += 1
    job.save()

    # Check if user has already applied
    has_applied = False
    if request.user.is_authenticated:
        has_applied = JobApplication.objects.filter(
            job=job,
            email=request.user.email
        ).exists()

    # Check if job is saved
    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedJob.objects.filter(
            user=request.user,
            job=job
        ).exists()

    application_form = JobApplicationForm(initial={'job': job})

    context = {
        'job': job,
        'application_form': application_form,
        'has_applied': has_applied,
        'is_saved': is_saved,
    }
    return render(request, 'jobs/job_detail.html', context)


@login_required
def post_job(request):
    """Create a new job posting"""
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.created_by = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('jobs:job_detail', job_id=job.id)
    else:
        form = JobForm()

    # Check if user is an employer
    is_employer = hasattr(request.user, 'profile') and request.user.profile.is_employer

    context = {
        'form': form,
        'is_employer': is_employer,
    }

    # Render employer-specific template if user is employer
    if is_employer:
        return render(request, 'jobs/employer_post_job.html', context)
    return render(request, 'jobs/post_job.html', context)


@login_required
def submit_application(request, job_id):
    """Handle job application submission"""
    job = get_object_or_404(Job, id=job_id)

    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

    # Check if user has already applied
    if JobApplication.objects.filter(job=job, email=request.user.email).exists():
        return JsonResponse({'error': 'You have already applied for this job'}, status=400)

    form = JobApplicationForm(request.POST, request.FILES)
    if form.is_valid():
        application = form.save(commit=False)
        application.job = job
        application.applicant_name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
        application.email = request.user.email
        application.save()

        # Create notification for employer
        Notification.objects.create(
            recipient=job.created_by,
            notification_type='job_application',
            title=f'New Application for {job.title}',
            message=f'{application.applicant_name} has applied for the position of {job.title}.',
            link=f'/jobs/{job.id}/applicants/'
        )

        messages.success(request, 'Application submitted successfully!')
        return JsonResponse({'success': True, 'message': 'Application submitted successfully!'})

    errors = {}
    for field, errors_list in form.errors.items():
        errors[field] = [str(error) for error in errors_list]

    return JsonResponse({'error': 'Invalid form data', 'errors': errors}, status=400)


@login_required
def my_applications(request):
    """Display user's job applications"""
    applications = JobApplication.objects.filter(
        email=request.user.email
    ).select_related('job').order_by('-applied_at')

    context = {
        'applications': applications,
    }
    return render(request, 'jobs/my_applications.html', context)


@login_required
def my_posted_jobs(request):
    """Display jobs posted by the user"""
    jobs = Job.objects.filter(
        created_by=request.user
    ).order_by('-created_at')

    # Check if user is an employer
    is_employer = hasattr(request.user, 'profile') and request.user.profile.is_employer

    context = {
        'jobs': jobs,
        'is_employer': is_employer,
    }

    # Render employer-specific template if user is employer
    if is_employer:
        return render(request, 'jobs/employer_my_jobs.html', context)
    return render(request, 'jobs/my_posted_jobs.html', context)


@login_required
def save_job(request, job_id):
    """Save/unsave a job"""
    job = get_object_or_404(Job, id=job_id)

    if request.method == 'POST':
        saved_job, created = SavedJob.objects.get_or_create(
            user=request.user,
            job=job
        )

        if not created:
            # Job was already saved, unsave it
            saved_job.delete()
            return JsonResponse({'saved': False, 'message': 'Job removed from saved jobs'})

        return JsonResponse({'saved': True, 'message': 'Job saved successfully'})

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def saved_jobs(request):
    """Display user's saved jobs"""
    saved = SavedJob.objects.filter(
        user=request.user
    ).select_related('job').order_by('-created_at')

    context = {
        'saved_jobs': saved,
    }
    return render(request, 'jobs/saved_jobs.html', context)


@login_required
def update_application_status(request, application_id):
    """Update application status (for job posters)"""
    application = get_object_or_404(JobApplication, id=application_id)

    # Check if user is the job poster
    if application.job.created_by != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')

        if new_status in dict(JobApplication.STATUS_CHOICES).keys():
            application.status = new_status
            application.notes = notes
            application.save()
            messages.success(request, 'Application status updated!')
            return JsonResponse({'success': True, 'message': 'Status updated successfully'})

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def delete_job(request, job_id):
    """Delete a job posting"""
    job = get_object_or_404(Job, id=job_id)

    # Check if user is the job poster
    if job.created_by != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted successfully!')
        return JsonResponse({'success': True, 'message': 'Job deleted successfully'})

    return JsonResponse({'error': 'Invalid request'}, status=400)


def job_applicants(request, job_id):
    """Display applicants for a specific job (for job posters)"""
    job = get_object_or_404(Job, id=job_id)

    # Check if user is the job poster
    if job.created_by != request.user:
        messages.error(request, 'Permission denied')
        return redirect('/jobs/')

    applications = job.applications.all().order_by('-applied_at')

    context = {
        'job': job,
        'applications': applications,
    }
    return render(request, 'jobs/job_applicants.html', context)


def download_resume(request, application_id):
    """Download resume file"""
    application = get_object_or_404(JobApplication, id=application_id)

    # Check if user is the job poster, the applicant, or a staff member
    if (application.job.created_by != request.user and
        application.email != request.user.email and
        not request.user.is_staff):
        messages.error(request, 'Permission denied')
        return redirect('/jobs/')

    if application.resume:
        response = HttpResponse(application.resume.read(), content_type='application/octet-stream')
        filename = os.path.basename(application.resume.name)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    messages.error(request, 'Resume not found')
    return redirect('job_list')


@login_required
def job_recommendations(request):
    """AI-powered job recommendations for job seekers"""
    # Check if user is a job seeker
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'job_seeker':
        messages.warning(request, 'Recommendations are available for job seekers only.')
        return redirect('job_list')

    matchmaker = JobMatchmaker()
    recommendations = matchmaker.generate_recommendations_for_user(request.user, limit=10)

    # Get user's skills for display
    user_skills = request.user.profile.candidate_skills.select_related('skill').all()

    context = {
        'recommendations': recommendations,
        'user_skills': user_skills,
    }
    return render(request, 'jobs/job_recommendations.html', context)


@login_required
def job_candidates_matches(request, job_id):
    """AI-powered candidate matching for employers"""
    job = get_object_or_404(Job, id=job_id)

    # Verify ownership - only employers who posted the job can see matches
    if job.created_by != request.user:
        messages.error(request, 'Access denied. You can only view candidates for your own jobs.')
        return redirect('jobs:my_posted_jobs')

    # Check if user is an employer
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'employer':
        messages.error(request, 'This feature is for employers only.')
        return redirect('jobs:my_posted_jobs')

    matchmaker = JobMatchmaker()
    candidates = matchmaker.find_candidates_for_job(job, limit=20)

    context = {
        'job': job,
        'candidates': candidates,
    }
    return render(request, 'jobs/job_candidates.html', context)


# ============================================================================
# INTERVIEW BOT VIEWS - AI-Driven Interview System
# ============================================================================

@login_required
def start_interview(request, job_id):
    """Start an AI interview session for a job"""
    job = get_object_or_404(Job, id=job_id, status='active')

    # Only job seekers can take interviews
    try:
        if not request.user.profile.is_job_seeker:
            messages.warning(request, 'Interviews are for job seekers only.')
            return redirect('jobs:job_detail', job_id=job.id)
    except UserProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first.')
        return redirect('accounts:profile')

    # Check if user has already applied
    if JobApplication.objects.filter(job=job, email=request.user.email).exists():
        messages.info(request, 'You have already applied for this job.')
        return redirect('jobs:job_detail', job_id=job.id)

    interview_bot = InterviewBot()

    # Create or get existing session
    session = interview_bot.create_interview_session(job, request.user)

    if session.status == 'completed':
        messages.info(request, 'You have already completed this interview.')
        return redirect('jobs:interview_results', session_id=session.id)

    # Generate questions
    questions = interview_bot.generate_interview_questions(job, limit=5)

    context = {
        'job': job,
        'session': session,
        'questions': questions,
        'total_questions': len(questions),
    }
    return render(request, 'jobs/interview_start.html', context)


@login_required
def interview_take(request, session_id):
    """Take an interview session"""
    session = get_object_or_404(InterviewSession, id=session_id)

    # Verify ownership
    if session.candidate != request.user:
        messages.error(request, 'Access denied.')
        return redirect('job_list')

    # Check if already completed
    if session.status == 'completed':
        return redirect('jobs:interview_results', session_id=session.id)

    # Check if expired (time limit)
    time_elapsed = 0
    if session.started_at:
        time_elapsed = (timezone.now() - session.started_at).total_seconds() / 60
        if time_elapsed > session.time_limit_minutes:
            session.status = 'expired'
            session.save()
            messages.error(request, 'Interview time limit has expired.')
            return redirect('jobs:interview_results', session_id=session.id)

    interview_bot = InterviewBot()
    job = session.job

    # Generate questions if not already generated
    questions = interview_bot.generate_interview_questions(job, limit=5)

    # Get already answered questions - convert to list for template usage
    answered_question_ids = list(session.responses.values_list('question_id', flat=True))

    context = {
        'session': session,
        'job': job,
        'questions': questions,
        'answered_question_ids': answered_question_ids,
        'total_questions': len(questions),
        'answered_count': len(answered_question_ids),
        'time_remaining_minutes': max(0, session.time_limit_minutes - int(time_elapsed)),
    }
    return render(request, 'jobs/interview_take.html', context)


@login_required
def interview_submit_response(request, session_id, question_id):
    """Submit answer to an interview question"""
    import time
    start_time = time.time()

    session = get_object_or_404(InterviewSession, id=session_id)

    # Verify ownership
    if session.candidate != request.user:
        return JsonResponse({'error': 'Access denied'}, status=403)

    # Check if session is still active
    if session.status != 'pending' and session.status != 'in_progress':
        return JsonResponse({'error': 'Interview session is not active'}, status=400)

    # Get the question
    question = get_object_or_404(InterviewQuestion, id=question_id)

    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

    answer = request.POST.get('answer', '').strip()
    time_taken = request.POST.get('time_taken')

    if not answer:
        return JsonResponse({'error': 'Answer cannot be empty'}, status=400)

    # Check if already answered
    if InterviewResponse.objects.filter(interview_session=session, question=question).exists():
        return JsonResponse({'error': 'Question already answered'}, status=400)

    # Score the response
    interview_bot = InterviewBot()
    score_data = interview_bot.score_response(question, answer, int(time_taken) if time_taken else None)

    # Save the response
    response = InterviewResponse.objects.create(
        interview_session=session,
        question=question,
        answer=answer,
        score=score_data['score'],
        max_score=score_data['max_score'],
        feedback=score_data['feedback'],
        keywords_found=score_data['keywords_found'],
        time_taken_seconds=int(time_taken) if time_taken else None
    )

    # Update session status
    session.status = 'in_progress'
    session.save()

    elapsed = time.time() - start_time
    print(f"Interview submission took {elapsed:.2f} seconds")  # Debug logging

    return JsonResponse({
        'success': True,
        'score': score_data['score'],
        'max_score': score_data['max_score'],
        'percentage': score_data['percentage'],
        'feedback': score_data['feedback']
    })


@login_required
def interview_complete(request, session_id):
    """Complete an interview session and calculate final score"""
    session = get_object_or_404(InterviewSession, id=session_id)

    # Verify ownership
    if session.candidate != request.user:
        messages.error(request, 'Access denied.')
        return redirect('job_list')

    # Mark as completed
    session.status = 'completed'
    session.completed_at = timezone.now()

    # Calculate final score
    interview_bot = InterviewBot()
    score_data = interview_bot.calculate_interview_score(session)
    session.feedback = score_data['feedback']
    session.save()

    # Create notification for candidate
    Notification.objects.create(
        recipient=request.user,
        notification_type='application_status',
        title=f'Interview Completed for {session.job.title}',
        message=f'Your interview score: {session.percentage}%. {session.score_grade}',
        link=f'/interview/results/{session.id}/'
    )

    messages.success(request, f'Interview completed! Your score: {session.percentage}% ({session.score_grade})')
    return redirect('jobs:interview_results', session_id=session.id)


@login_required
def interview_results(request, session_id):
    """View interview results"""
    session = get_object_or_404(InterviewSession, id=session_id)

    # Verify ownership or job poster
    can_view = (
        session.candidate == request.user or
        session.job.created_by == request.user or
        request.user.is_staff
    )

    if not can_view:
        messages.error(request, 'Access denied.')
        return redirect('job_list')

    interview_bot = InterviewBot()
    report = interview_bot.get_interview_report(session)

    context = {
        'session': session,
        'report': report,
        'is_candidate': session.candidate == request.user,
    }
    return render(request, 'jobs/interview_results.html', context)


@login_required
def interview_list(request):
    """List all interview sessions for the current user"""
    sessions = InterviewSession.objects.filter(
        candidate=request.user
    ).select_related('job').order_by('-started_at')

    context = {
        'sessions': sessions,
    }
    return render(request, 'jobs/interview_list.html', context)


# ============================================================================
# NOTIFICATION VIEWS
# ============================================================================

@login_required
def notifications_list(request):
    """List all notifications for the current user"""
    notifications = request.user.notifications.all().order_by('-created_at')[:50]

    context = {
        'notifications': notifications,
    }
    return render(request, 'jobs/notifications.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)

    if request.method == 'POST':
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    if request.method == 'POST':
        request.user.notifications.filter(is_read=False).update(is_read=True)
        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def unread_notification_count(request):
    """Get count of unread notifications (for AJAX)"""
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'count': count})


# ============================================================================
# ANALYTICS DASHBOARD VIEWS
# ============================================================================

@login_required
def analytics_dashboard(request):
    """Trend Analytics Dashboard - Job Market Insights"""
    # Only employers and staff can view analytics
    if not request.user.is_staff:
        if hasattr(request.user, 'profile') and not request.user.profile.is_employer:
            messages.warning(request, 'Analytics dashboard is for employers only.')
            return redirect('job_list')

    # Get statistics
    from django.db.models import Count, Avg, Q
    from django.db.models.functions import TruncDate, TruncMonth

    # Jobs statistics
    total_jobs = Job.objects.count()
    active_jobs = Job.objects.filter(status='active').count()
    jobs_by_type = dict(Job.objects.values('job_type').annotate(count=Count('id')).values_list('job_type', 'count'))
    jobs_by_level = dict(Job.objects.values('experience_level').annotate(count=Count('id')).values_list('experience_level', 'count'))

    # Applications statistics
    total_applications = JobApplication.objects.count()
    applications_by_status = dict(
        JobApplication.objects.values('status').annotate(count=Count('id')).values_list('status', 'count')
    )

    # Recent activity (last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.now() - timedelta(days=30)

    recent_jobs = Job.objects.filter(created_at__gte=thirty_days_ago).count()
    recent_applications = JobApplication.objects.filter(applied_at__gte=thirty_days_ago).count()

    # Top categories
    top_categories = list(JobCategory.objects.annotate(
        job_count=Count('jobs')
    ).order_by('-job_count')[:10])

    # Skills demand (from job requirements)
    from jobs.services.skills_extractor import SkillsExtractor
    extractor = SkillsExtractor()

    # Get all active job descriptions
    active_jobs = Job.objects.filter(status='active')
    all_skills = []
    for job in active_jobs:
        skills = extractor.extract_from_job_description(job.requirements + ' ' + job.description)
        all_skills.extend(skills)

    from collections import Counter
    skill_demand = Counter(all_skills).most_common(15)

    # Companies with most jobs
    top_companies = list(Job.objects.values('company').annotate(
        job_count=Count('id')
    ).order_by('-job_count')[:10])

    # Application trends by month (last 6 months)
    six_months_ago = datetime.now() - timedelta(days=180)
    monthly_applications = list(
        JobApplication.objects.filter(applied_at__gte=six_months_ago)
        .annotate(month=TruncMonth('applied_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    context = {
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'jobs_by_type': jobs_by_type,
        'jobs_by_level': jobs_by_level,
        'applications_by_status': applications_by_status,
        'recent_jobs': recent_jobs,
        'recent_applications': recent_applications,
        'top_categories': top_categories,
        'skill_demand': skill_demand,
        'top_companies': top_companies,
        'monthly_applications': monthly_applications,
    }
    return render(request, 'jobs/analytics_dashboard.html', context)
