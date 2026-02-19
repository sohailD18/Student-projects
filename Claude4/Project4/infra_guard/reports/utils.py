"""
AI Simulation Utilities for InfraGuard
This module contains keyword-based categorization and risk scoring algorithms
to simulate AI features without external API dependencies.
"""

from datetime import datetime, timedelta
from django.utils import timezone
from django.db import models
from django.db.models import Count, Q
from .models import Incident, Claim


# Keyword mapping for automatic incident type categorization
KEYWORD_MAPPING = {
    'pothole': [
        'pothole', 'hole', 'pit', 'road damage', 'crack', 'broken road',
        'road depression', 'rut', 'bump', 'uneven road', 'surface damage'
    ],
    'drainage': [
        'drainage', 'flood', 'water logging', 'sewer', 'clogged', 'blocked drain',
        'water accumulation', 'standing water', 'overflow', 'water backup',
        'flooding', 'waterlogged', 'drain blockage'
    ],
    'streetlight': [
        'streetlight', 'light', 'lamp', 'dark', 'illumination', 'street light',
        'broken light', 'no light', 'dim light', 'flickering', 'light pole',
        'lamp post', 'lighting', 'night visibility'
    ],
    'footpath': [
        'footpath', 'sidewalk', 'pavement', 'walkway', 'pedestrian',
        'broken pavement', 'uneven sidewalk', 'walkway damage',
        'pedestrian path', 'footpath damage'
    ]
}

# Emergency keywords that increase severity score
EMERGENCY_KEYWORDS = [
    'emergency', 'dangerous', 'hazard', 'life threatening', 'urgent',
    'critical', 'severe', 'accident', 'injury', 'fell', 'tripped',
    'danger', 'risk', 'unsafe', 'major', 'serious'
]


def categorize_incident(description, user_selected_type=None):
    """
    Auto-categorize incident type based on keywords in description.

    Args:
        description: Text description of the incident
        user_selected_type: Type manually selected by user (if any)

    Returns:
        String: The determined incident type
    """
    # If user explicitly selected a type, respect their choice
    if user_selected_type and user_selected_type != 'other':
        return user_selected_type

    # Analyze description for keywords
    description_lower = description.lower()

    # Score each incident type based on keyword matches
    type_scores = {}
    for incident_type, keywords in KEYWORD_MAPPING.items():
        score = 0
        for keyword in keywords:
            if keyword.lower() in description_lower:
                score += 1
        if score > 0:
            type_scores[incident_type] = score

    # Return type with highest score, or 'other' if no matches
    if type_scores:
        return max(type_scores, key=type_scores.get)
    return 'other'


def calculate_risk_score(location, description, has_image, latitude=None, longitude=None):
    """
    Calculate AI-based risk score for an incident.

    Scoring Algorithm:
    - Base score: 30
    - +20 for each prior incident at same location in past 30 days (max +40)
    - +20 if description contains emergency keywords
    - -10 if image is provided (more verifiable)
    - +10 if no image (less verifiable)
    - Cap at 100

    Args:
        location: Location string/coordinates
        description: Incident description
        has_image: Boolean indicating if image was uploaded
        latitude: Optional latitude coordinate
        longitude: Optional longitude coordinate

    Returns:
        Integer: Risk score between 0 and 100
    """
    score = 30  # Base score

    # Check for similar location incidents in past 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)

    # Query for incidents at similar location
    location_matches = Incident.objects.filter(
        location__icontains=location,
        timestamp__gte=thirty_days_ago
    ).count()

    # Add location frequency bonus (capped at +40)
    location_bonus = min(location_matches * 20, 40)
    score += location_bonus

    # Check for emergency keywords
    description_lower = description.lower()
    has_emergency_keywords = any(
        keyword in description_lower
        for keyword in EMERGENCY_KEYWORDS
    )
    if has_emergency_keywords:
        score += 20

    # Adjust based on image availability
    if has_image:
        score -= 10  # More verifiable = lower risk
    else:
        score += 10  # Less verifiable = higher risk

    # Ensure score is within bounds
    return max(0, min(score, 100))


def get_high_risk_zones(limit=10, days=30):
    """
    Identify high-risk zones based on incident frequency.

    Args:
        limit: Maximum number of zones to return
        days: Number of days to look back for incidents

    Returns:
        List of tuples: (location, incident_count, avg_severity)
    """
    cutoff_date = timezone.now() - timedelta(days=days)

    zones = Incident.objects.filter(
        timestamp__gte=cutoff_date
    ).values('location').annotate(
        incident_count=Count('id'),
        avg_severity=models.Avg('severity_score')
    ).filter(
        incident_count__gte=2
    ).order_by('-incident_count', '-avg_severity')[:limit]

    return list(zones)


def get_statistics():
    """
    Calculate overall system statistics for dashboard.

    Returns:
        Dictionary with various statistics
    """
    total_incidents = Incident.objects.count()

    # Status breakdown
    pending_count = Incident.objects.filter(status='pending').count()
    verified_count = Incident.objects.filter(status='verified').count()
    resolved_count = Incident.objects.filter(status='resolved').count()
    rejected_count = Incident.objects.filter(status='rejected').count()

    # Severity breakdown
    high_severity = Incident.objects.filter(severity_score__gt=70).count()
    medium_severity = Incident.objects.filter(
        severity_score__gt=40, severity_score__lte=70
    ).count()
    low_severity = Incident.objects.filter(severity_score__lte=40).count()

    # Recent activity (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    recent_incidents = Incident.objects.filter(timestamp__gte=week_ago).count()

    # Claims statistics
    total_claims = Claim.objects.count() if Claim else 0
    pending_claims = Claim.objects.filter(status='filed').count() if Claim else 0
    approved_claims = Claim.objects.filter(status='approved').count() if Claim else 0

    return {
        'total_incidents': total_incidents,
        'pending_count': pending_count,
        'verified_count': verified_count,
        'resolved_count': resolved_count,
        'rejected_count': rejected_count,
        'high_severity': high_severity,
        'medium_severity': medium_severity,
        'low_severity': low_severity,
        'recent_incidents': recent_incidents,
        'total_claims': total_claims,
        'pending_claims': pending_claims,
        'approved_claims': approved_claims,
    }


def analyze_location_trend(location, days=90):
    """
    Analyze incident trend for a specific location.

    Args:
        location: Location string to analyze
        days: Number of days to look back

    Returns:
        Dictionary with trend analysis
    """
    cutoff_date = timezone.now() - timedelta(days=days)

    incidents = Incident.objects.filter(
        location__icontains=location,
        timestamp__gte=cutoff_date
    ).order_by('timestamp')

    count = incidents.count()
    if count == 0:
        return {'trend': 'no_data', 'count': 0}

    # Calculate trend
    first_half = incidents.filter(timestamp__lte=timezone.now() - timedelta(days=days//2)).count()
    second_half = incidents.filter(timestamp__gt=timezone.now() - timedelta(days=days//2)).count()

    if second_half > first_half * 1.5:
        trend = 'increasing'
    elif second_half < first_half * 0.5:
        trend = 'decreasing'
    else:
        trend = 'stable'

    # Most common incident type
    type_counts = incidents.values('incident_type').annotate(
        count=Count('incident_type')
    ).order_by('-count').first()

    common_type = type_counts['incident_type'] if type_counts else 'unknown'

    return {
        'trend': trend,
        'count': count,
        'common_type': common_type,
        'avg_severity': incidents.aggregate(models.Avg('severity_score'))['severity_score__avg'] or 0
    }