from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    """Extended user profile with location and preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, help_text="Default location for reports")
    address = models.TextField(blank=True, help_text="Full address")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    bio = models.TextField(blank=True, max_length=500, help_text="Tell us about yourself")
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    notification_enabled = models.BooleanField(default=True, help_text="Receive notifications for nearby incidents")
    email_alerts = models.BooleanField(default=True, help_text="Receive email alerts")
    radius_km = models.IntegerField(default=10, help_text="Alert radius in kilometers")
    reputation_score = models.IntegerField(default=0, help_text="User reputation based on verified reports")
    joined_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def calculate_reputation(self):
        """Calculate reputation based on verified incidents"""
        verified_count = self.user.incidents.filter(is_verified=True).count()
        self.reputation_score = verified_count * 10
        self.save()
        return self.reputation_score


class IncidentCategory(models.Model):
    """Categories for classifying incidents"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='bi-exclamation-triangle', help_text="Bootstrap icon class")
    color = models.CharField(max_length=7, default='#dc3545', help_text="Hex color code")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Incident Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Incident(models.Model):
    """Main incident model with enhanced features"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('investigating', 'Investigating'),
        ('verified', 'Verified'),
        ('resolved', 'Resolved'),
        ('false_report', 'False Report'),
    ]

    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(IncidentCategory, on_delete=models.SET_NULL, null=True, related_name='incidents')
    location = models.CharField(max_length=255)
    address = models.TextField(blank=True, help_text="Detailed address")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    image = models.ImageField(upload_to='incidents/', blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now, help_text="When the incident occurred")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incidents')
    is_verified = models.BooleanField(default=False, help_text="Whether the incident has been verified")
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_incidents')
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_count = models.IntegerField(default=0, help_text="Number of community verifications")
    view_count = models.IntegerField(default=0, help_text="Number of times this incident was viewed")
    is_anonymous = models.BooleanField(default=False, help_text="Hide reporter identity")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['is_verified', '-created_at']),
            models.Index(fields=['severity', '-created_at']),
        ]

    def __str__(self):
        return self.title

    def increment_verification(self):
        """Increment community verification count"""
        self.verification_count += 1
        if self.verification_count >= 3 and not self.is_verified:
            self.is_verified = True
            self.status = 'verified'
        self.save()
        return self.verification_count

    def get_nearby_users(self, radius_km=10):
        """Get users within the specified radius who have notifications enabled"""
        from math import radians, cos, sin, asin, sqrt

        if not self.latitude or not self.longitude:
            return []

        nearby_users = []
        for profile in UserProfile.objects.filter(notification_enabled=True):
            if profile.latitude and profile.longitude:
                # Calculate distance using Haversine formula
                lat1, lon1 = radians(float(self.latitude)), radians(float(self.longitude))
                lat2, lon2 = radians(float(profile.latitude)), radians(float(profile.longitude))

                dlon = lon2 - lon1
                dlat = lat2 - lat1
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                c = 2 * asin(sqrt(a))
                km = 6371 * c  # Earth's radius in km

                if km <= radius_km:
                    nearby_users.append(profile.user)

        return nearby_users


class IncidentVerification(models.Model):
    """Track individual verifications of incidents"""
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='verifications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verifications')
    is_confirmed = models.BooleanField(default=True, help_text="True if confirming, False if reporting as false")
    comments = models.TextField(blank=True, help_text="Additional verification notes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['incident', 'user']
        verbose_name = "Incident Verification"
        verbose_name_plural = "Incident Verifications"

    def __str__(self):
        action = "confirmed" if self.is_confirmed else "reported as false"
        return f"{self.user.username} {action} {self.incident.title}"


class Comment(models.Model):
    """Enhanced comment system with likes and threading"""
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    likes_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.user.username} on {self.incident.title}'


class CommentLike(models.Model):
    """Track likes on comments"""
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['comment', 'user']

    def __str__(self):
        return f'{self.user.username} liked comment on {self.comment.incident.title}'


class Notification(models.Model):
    """Notification system for real-time alerts"""
    NOTIFICATION_TYPES = [
        ('new_incident', 'New Incident Nearby'),
        ('incident_verified', 'Incident Verified'),
        ('incident_updated', 'Incident Status Updated'),
        ('new_comment', 'New Comment on Your Report'),
        ('comment_reply', 'Reply to Your Comment'),
        ('alert', 'Safety Alert'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', '-created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.recipient.username}"

    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save()


class SafetyAlert(models.Model):
    """System-wide safety alerts from administrators"""
    title = models.CharField(max_length=255)
    message = models.TextField()
    severity = models.CharField(max_length=20, choices=Incident.SEVERITY_CHOICES, default='high')
    affected_areas = models.CharField(max_length=500, help_text="Comma-separated locations")
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="When the alert expires")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_alerts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Safety Alert"
        verbose_name_plural = "Safety Alerts"

    def __str__(self):
        return self.title

    def is_active_alert(self):
        """Check if alert is still active"""
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True
