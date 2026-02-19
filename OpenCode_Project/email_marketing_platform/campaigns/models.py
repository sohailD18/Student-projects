from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class EmailList(models.Model):
    """Model to store email lists/subscriber lists"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def subscriber_count(self):
        return self.subscribers.filter(is_active=True).count()


class Subscriber(models.Model):
    """Model to store email subscribers"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('unsubscribed', 'Unsubscribed'),
        ('bounced', 'Bounced'),
        ('pending', 'Pending'),
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email_list = models.ManyToManyField(EmailList, related_name='subscribers')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    # Custom fields for segmentation
    custom_fields = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-subscribed_at']

    def __str__(self):
        return f"{self.email} ({self.get_status_display()})"

    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email


class EmailTemplate(models.Model):
    """Model to store email templates"""
    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=500)
    html_content = models.TextField()
    text_content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def preview(self):
        return self.html_content[:100] + '...' if len(self.html_content) > 100 else self.html_content


class Campaign(models.Model):
    """Model to store email marketing campaigns"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('paused', 'Paused'),
    ]

    name = models.CharField(max_length=200)
    email_template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE, related_name='campaigns')
    email_list = models.ForeignKey(EmailList, on_delete=models.CASCADE, related_name='campaigns')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # A/B Testing fields
    is_ab_test = models.BooleanField(default=False)
    ab_test_variant_a = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name='campaigns_variant_a')
    ab_test_variant_b = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name='campaigns_variant_b')
    ab_test_split_percentage = models.IntegerField(default=50, help_text="Percentage for variant A (0-100)")
    ab_test_winner = models.CharField(max_length=1, choices=[('A', 'Variant A'), ('B', 'Variant B')],
                                      null=True, blank=True)

    # Scheduling
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='campaigns')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    @property
    def total_recipients(self):
        return self.email_list.subscriber_count

    @property
    def total_sent(self):
        return self.logs.filter(status='sent').count()

    @property
    def total_opens(self):
        return self.logs.filter(analytics__opened_at__isnull=False).count()

    @property
    def total_clicks(self):
        return self.logs.filter(analytics__clicked_at__isnull=False).count()

    @property
    def open_rate(self):
        sent = self.total_sent
        if sent > 0:
            return round((self.total_opens / sent) * 100, 2)
        return 0

    @property
    def click_rate(self):
        sent = self.total_sent
        if sent > 0:
            return round((self.total_clicks / sent) * 100, 2)
        return 0


class EmailLog(models.Model):
    """Model to track email sending logs"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='logs')
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name='email_logs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # For A/B testing
    variant = models.CharField(max_length=1, choices=[('A', 'Variant A'), ('B', 'Variant B')],
                               null=True, blank=True)

    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Email to {self.subscriber.email} - {self.get_status_display()}"


class EmailAnalytics(models.Model):
    """Model to track email analytics (opens, clicks, etc.)"""
    email_log = models.OneToOneField(EmailLog, on_delete=models.CASCADE, related_name='analytics')
    opened_at = models.DateTimeField(null=True, blank=True)
    click_count = models.IntegerField(default=0)
    clicked_at = models.DateTimeField(null=True, blank=True)
    clicked_links = models.JSONField(default=list, blank=True)

    # Device and browser info
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-opened_at']

    def __str__(self):
        return f"Analytics for {self.email_log.subscriber.email}"


class Link(models.Model):
    """Model to track links in emails"""
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='links')
    url = models.URLField(max_length=2000)
    total_clicks = models.IntegerField(default=0)
    unique_clicks = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-total_clicks']

    def __str__(self):
        return f"{self.url} ({self.total_clicks} clicks)"
