"""
Views for InfraGuard Application
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta

from .models import Incident, Claim, UserProfile
from .forms import (
    UserRegistrationForm, IncidentReportForm, ClaimForm,
    IncidentVerificationForm, ClaimReviewForm
)
from .utils import (
    categorize_incident, calculate_risk_score, get_high_risk_zones,
    get_statistics, analyze_location_trend
)


# ==================== Authentication Views ====================

def register(request):
    """Handle user registration"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Create user profile
            UserProfile.objects.create(
                user=user,
                role=form.cleaned_data['role'],
                phone=form.cleaned_data.get('phone', '')
            )

            messages.success(request, 'Registration successful! Please login.')
            return redirect('reports:login')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('reports:home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')

            # Redirect based on role
            try:
                profile = user.profile
                if profile.role == 'authority':
                    return redirect('reports:admin_dashboard')
                else:
                    return redirect('reports:citizen_dashboard')
            except UserProfile.DoesNotExist:
                return redirect('reports:home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('reports:home')


# ==================== Public Views ====================

def home(request):
    """Home page with statistics and recent incidents"""
    stats = get_statistics()

    # Get recent incidents for ticker
    recent_incidents = Incident.objects.select_related('reported_by').order_by('-timestamp')[:5]

    # High-risk zones for display
    high_risk_zones = get_high_risk_zones(limit=5)

    context = {
        'stats': stats,
        'recent_incidents': recent_incidents,
        'high_risk_zones': high_risk_zones,
    }
    return render(request, 'index.html', context)


# ==================== Incident Reporting ====================

@login_required
def report_incident(request):
    """Form for citizens to report incidents"""
    if request.method == 'POST':
        form = IncidentReportForm(request.POST, request.FILES)
        if form.is_valid():
            # Get form data
            location = form.cleaned_data['location']
            description = form.cleaned_data['description']
            incident_type = form.cleaned_data['incident_type']
            image = form.cleaned_data.get('image')
            latitude = form.cleaned_data.get('latitude')
            longitude = form.cleaned_data.get('longitude')

            # AI Processing
            # 1. Auto-categorize if user didn't override
            auto_type = categorize_incident(description, incident_type if incident_type != 'other' else None)

            # 2. Calculate risk score
            severity_score = calculate_risk_score(
                location, description, bool(image), latitude, longitude
            )

            # Create incident
            incident = Incident.objects.create(
                location=location,
                description=description,
                incident_type=auto_type,
                image=image,
                latitude=latitude,
                longitude=longitude,
                severity_score=severity_score,
                reported_by=request.user
            )

            messages.success(
                request,
                f'Incident reported successfully! '
                f'AI categorized it as "{incident.get_incident_type_display()}" '
                f'with severity score {severity_score}.'
            )
            return redirect('reports:citizen_dashboard')
    else:
        form = IncidentReportForm()

    return render(request, 'report_form.html', {'form': form})


# ==================== Citizen Dashboard ====================

@login_required
def citizen_dashboard(request):
    """Dashboard for citizens to view their reports and claims"""
    # Check if user is a citizen
    try:
        profile = request.user.profile
        if profile.role == 'authority':
            messages.info(request, 'Redirecting to authority dashboard...')
            return redirect('reports:admin_dashboard')
    except UserProfile.DoesNotExist:
        pass

    # Get user's incidents
    incidents = Incident.objects.filter(reported_by=request.user).order_by('-timestamp')

    # Get user's claims
    user_claims = Claim.objects.filter(
        incident__reported_by=request.user
    ).select_related('incident').order_by('-filed_date')

    context = {
        'incidents': incidents,
        'user_claims': user_claims,
        'total_incidents': incidents.count(),
        'verified_count': incidents.filter(status='verified').count(),
    }
    return render(request, 'dashboard.html', context)


# ==================== Authority Dashboard ====================

@login_required
def admin_dashboard(request):
    """Dashboard for authorities to manage incidents and claims"""
    # Check if user is an authority
    try:
        profile = request.user.profile
        if profile.role != 'authority':
            messages.error(request, 'Access denied. Authority only.')
            return redirect('reports:home')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('reports:home')

    stats = get_statistics()

    # Pending incidents for verification
    pending_incidents = Incident.objects.filter(
        status='pending'
    ).select_related('reported_by').order_by('-severity_score', '-timestamp')

    # High-risk zones
    high_risk_zones = get_high_risk_zones(limit=10)

    # Pending claims
    pending_claims = Claim.objects.filter(
        status__in=['filed', 'under_review']
    ).select_related('incident', 'reviewed_by').order_by('-filed_date')

    context = {
        'stats': stats,
        'pending_incidents': pending_incidents,
        'high_risk_zones': high_risk_zones,
        'pending_claims': pending_claims,
    }
    return render(request, 'admin_dashboard.html', context)


@login_required
def verify_incident(request, incident_id):
    """Verify or reject an incident (authority only)"""
    incident = get_object_or_404(Incident, id=incident_id)

    # Check authority permission
    try:
        if request.user.profile.role != 'authority':
            messages.error(request, 'Access denied.')
            return redirect('reports:home')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('reports:home')

    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')

        if action == 'verify':
            incident.status = 'verified'
            incident.verified_at = timezone.now()
            incident.authority_notes = notes
            incident.save()
            messages.success(request, f'Incident #{incident.id} verified successfully.')

        elif action == 'reject':
            incident.status = 'rejected'
            incident.authority_notes = notes
            incident.save()
            messages.warning(request, f'Incident #{incident.id} rejected.')

        elif action == 'resolve':
            incident.status = 'resolved'
            incident.resolved_at = timezone.now()
            incident.authority_notes = notes
            incident.save()
            messages.success(request, f'Incident #{incident.id} marked as resolved.')

        return redirect('reports:admin_dashboard')

    # GET request - show verification form
    form = IncidentVerificationForm()
    context = {'incident': incident, 'form': form}
    return render(request, 'verify_incident.html', context)


# ==================== Claims Management ====================

@login_required
def file_claim(request, incident_id):
    """File a compensation claim for a verified incident"""
    incident = get_object_or_404(Incident, id=incident_id)

    # Only allow claims for verified incidents by the reporter
    if incident.status != 'verified':
        messages.error(request, 'Claims can only be filed for verified incidents.')
        return redirect('reports:citizen_dashboard')

    if incident.reported_by != request.user:
        messages.error(request, 'You can only file claims for your own incidents.')
        return redirect('reports:citizen_dashboard')

    # Check if claim already exists
    if incident.claims.exists():
        messages.info(request, 'A claim has already been filed for this incident.')
        return redirect('reports:citizen_dashboard')

    if request.method == 'POST':
        form = ClaimForm(request.POST)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.incident = incident
            claim.save()
            messages.success(request, 'Claim filed successfully!')
            return redirect('reports:citizen_dashboard')
    else:
        form = ClaimForm()

    context = {'incident': incident, 'form': form}
    return render(request, 'file_claim.html', context)


@login_required
def manage_claims(request):
    """View for authorities to manage all claims"""
    # Check authority permission
    try:
        if request.user.profile.role != 'authority':
            messages.error(request, 'Access denied.')
            return redirect('reports:home')
    except UserProfile.DoesNotExist:
        return redirect('reports:home')

    claims = Claim.objects.select_related(
        'incident', 'incident__reported_by', 'reviewed_by'
    ).order_by('-filed_date')

    context = {'claims': claims}
    return render(request, 'manage_claims.html', context)


@login_required
def update_claim_status(request, claim_id):
    """Update claim status (approve/reject) - Authority only"""
    claim = get_object_or_404(Claim, id=claim_id)

    # Check authority permission
    try:
        if request.user.profile.role != 'authority':
            messages.error(request, 'Access denied.')
            return redirect('reports:home')
    except UserProfile.DoesNotExist:
        return redirect('reports:home')

    if request.method == 'POST':
        action = request.POST.get('action')
        approved_amount = request.POST.get('approved_amount')
        review_notes = request.POST.get('review_notes', '')

        if action == 'approve':
            claim.status = 'approved'
            claim.approved_amount = approved_amount or claim.claim_amount
            claim.review_notes = review_notes
            claim.reviewed_by = request.user
            claim.reviewed_at = timezone.now()
            claim.save()
            messages.success(request, f'Claim approved for {claim.victim_name}.')

        elif action == 'under_review':
            claim.status = 'under_review'
            claim.review_notes = review_notes
            claim.reviewed_by = request.user
            claim.reviewed_at = timezone.now()
            claim.save()
            messages.info(request, f'Claim marked as under review.')

        elif action == 'reject':
            claim.status = 'rejected'
            claim.review_notes = review_notes
            claim.reviewed_by = request.user
            claim.reviewed_at = timezone.now()
            claim.save()
            messages.warning(request, f'Claim rejected for {claim.victim_name}.')

        return redirect('reports:manage_claims')

    # GET request - show review form
    form = ClaimReviewForm()
    context = {'claim': claim, 'form': form}
    return render(request, 'review_claim.html', context)


# ==================== API Endpoints ====================

def get_location(request):
    """API endpoint to return location data (placeholder for actual geocoding)"""
    # This would integrate with a geocoding service in production
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')

    if lat and lng:
        return JsonResponse({
            'success': True,
            'latitude': float(lat),
            'longitude': float(lng),
            'address': f'Location at {lat}, {lng}'
        })

    return JsonResponse({'success': False, 'error': 'Missing coordinates'})


def incident_detail(request, incident_id):
    """View details of a specific incident"""
    incident = get_object_or_404(Incident, id=incident_id)

    # Get location trend analysis
    trend = analyze_location_trend(incident.location)

    context = {
        'incident': incident,
        'trend': trend,
    }
    return render(request, 'incident_detail.html', context)
