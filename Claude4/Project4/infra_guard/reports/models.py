from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class UserProfile(models.Model):
    """Extended user profile with role-based access"""
    ROLE_CHOICES = [
        ('citizen', 'Citizen'),
        ('authority', 'Authority'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='citizen')
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


class Incident(models.Model):
    """Infrastructure accident/incident reports"""
    INCIDENT_TYPE_CHOICES = [
        ('pothole', 'Pothole'),
        ('drainage', 'Drainage'),
        ('streetlight', 'Streetlight'),
        ('footpath', 'Footpath'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]

    location = models.CharField(max_length=255, help_text="Street address or landmark")
    description = models.TextField(help_text="Detailed description of the incident")
    incident_type = models.CharField(
        max_length=20,
        choices=INCIDENT_TYPE_CHOICES,
        default='other',
        help_text="Auto-categorized by AI, can be overridden"
    )
    image = models.ImageField(
        upload_to='incident_images/%Y/%m/',
        blank=True,
        null=True,
        help_text="Supporting image evidence"
    )
    latitude = models.FloatField(blank=True, null=True, help_text="GPS latitude coordinate")
    longitude = models.FloatField(blank=True, null=True, help_text="GPS longitude coordinate")
    severity_score = models.IntegerField(
        default=30,
        help_text="AI-calculated risk score (0-100)",
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reported_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reported_incidents'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(blank=True, null=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    authority_notes = models.TextField(blank=True, null=True, help_text="Notes from authority review")

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Incident"
        verbose_name_plural = "Incidents"
        indexes = [
            models.Index(fields=['status', '-timestamp']),
            models.Index(fields=['location']),
            models.Index(fields=['severity_score']),
        ]

    def __str__(self):
        return f"{self.get_incident_type_display()} at {self.location} ({self.status})"

    def get_severity_level(self):
        """Returns severity classification based on score"""
        if self.severity_score <= 40:
            return 'Low'
        elif self.severity_score <= 70:
            return 'Medium'
        else:
            return 'High'

    def get_severity_color(self):
        """Returns CSS color class for severity"""
        if self.severity_score <= 40:
            return 'severity-low'
        elif self.severity_score <= 70:
            return 'severity-medium'
        else:
            return 'severity-high'


class Claim(models.Model):
    """Compensation claims filed for verified incidents"""
    CLAIM_STATUS_CHOICES = [
        ('filed', 'Filed'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='claims',
        limit_choices_to={'status': 'verified'}
    )
    victim_name = models.CharField(max_length=255, help_text="Name of the victim/claimant")
    claim_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Claim amount in local currency"
    )
    status = models.CharField(max_length=20, choices=CLAIM_STATUS_CHOICES, default='filed')
    evidence_description = models.TextField(
        help_text="Detailed evidence and justification for the claim"
    )
    filed_date = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='reviewed_claims',
        help_text="Authority user who reviewed the claim"
    )
    review_notes = models.TextField(blank=True, null=True, help_text="Authority review notes")
    approved_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Final approved amount if different from claimed"
    )
    reviewed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-filed_date']
        verbose_name = "Claim"
        verbose_name_plural = "Claims"

    def __str__(self):
        return f"Claim by {self.victim_name} - {self.get_status_display()} ({self.claim_amount})"

    def get_status_color(self):
        """Returns CSS color class for status"""
        colors = {
            'filed': 'status-info',
            'under_review': 'status-warning',
            'approved': 'status-success',
            'rejected': 'status-danger'
        }
        return colors.get(self.status, 'status-info')
