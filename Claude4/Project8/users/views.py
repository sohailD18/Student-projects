"""
Views for Users App
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone
from .models import UserProfile
from exams.models import Exam, ExamCategory


# ========== Smart Recommendation Logic ==========

def get_smart_recommendations(user):
    """
    AI/Smart Recommendation Engine
    Returns personalized exam recommendations based on:
    - User's age vs Exam age limits
    - User's qualification vs Exam requirements
    - User's preferred exam types
    - Only upcoming exams
    """
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        return []

    # Get all upcoming exams
    upcoming_exams = Exam.objects.filter(exam_date__gte=timezone.now().date())

    recommended_exams = []

    for exam in upcoming_exams:
        # Check if user is eligible for this exam
        if profile.is_eligible_for_exam(exam):
            # Score the exam based on user preferences
            score = 0

            # Preference matching (higher score for preferred exam types)
            preferred_types = profile.get_preferred_exam_types_list()
            if exam.category and exam.category.code in preferred_types:
                score += 10
            elif exam.exam_type in preferred_types:
                score += 10  # Backward compatibility

            # Age proximity bonus (exams with closer age limits get higher score)
            if profile.age:
                age_diff = min(
                    abs(profile.age - exam.age_limit_min),
                    abs(profile.age - exam.age_limit_max)
                )
                score += max(0, 5 - age_diff)

            # Urgency bonus (sooner application deadlines get higher score)
            days_until_deadline = exam.days_until_application_deadline()
            if 0 <= days_until_deadline <= 30:
                score += 5
            elif 31 <= days_until_deadline <= 60:
                score += 3

            recommended_exams.append((exam, score))

    # Sort by score (descending) and return just the exams
    recommended_exams.sort(key=lambda x: x[1], reverse=True)
    return [exam for exam, score in recommended_exams]


# ========== Views ==========

class SignUpView(CreateView):
    """
    User Registration View
    """
    form_class = UserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            'Account created successfully! Please log in.'
        )
        return response


@login_required
def profile_view(request):
    """
    View and edit user profile
    """
    # Get or create profile if it doesn't exist
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        # Update profile fields
        profile.date_of_birth = request.POST.get('date_of_birth')
        profile.category = request.POST.get('category')
        profile.highest_qualification = request.POST.get('highest_qualification')
        profile.state = request.POST.get('state', '')

        # Handle preferred exam types (checkboxes)
        preferred_types = request.POST.getlist('preferred_exam_types')
        profile.preferred_exam_types = ','.join(preferred_types)

        profile.profile_completed = True
        profile.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('dashboard')

    # Add categories to context
    categories = ExamCategory.objects.filter(is_active=True)

    return render(request, 'users/profile.html', {
        'profile': profile,
        'categories': categories
    })


@login_required
def dashboard_view(request):
    """
    User Dashboard with Smart Recommendations
    """
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    # Get smart recommendations
    recommended_exams = get_smart_recommendations(request.user)

    # Get quick stats
    upcoming_count = Exam.objects.filter(
        exam_date__gte=timezone.now().date()
    ).count()

    application_open_count = Exam.objects.filter(
        application_start_date__lte=timezone.now().date(),
        application_end_date__gte=timezone.now().date()
    ).count()

    context = {
        'profile': profile,
        'recommended_exams': recommended_exams[:6],  # Top 6 recommendations
        'upcoming_count': upcoming_count,
        'application_open_count': application_open_count,
    }

    return render(request, 'users/dashboard.html', context)


@login_required
def my_exams_view(request):
    """
    View all recommended exams for the user
    """
    recommended_exams = get_smart_recommendations(request.user)

    return render(request, 'users/my_exams.html', {
        'recommended_exams': recommended_exams
    })
