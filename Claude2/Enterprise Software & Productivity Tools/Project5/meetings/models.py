"""
Database models for the Meeting Analyzer application.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Meeting(models.Model):
    """
    Model representing a meeting.
    """
    title = models.CharField(max_length=255)
    date = models.DateTimeField()
    duration = models.PositiveIntegerField(help_text='Duration in minutes')
    participants = models.TextField(help_text='Comma-separated list of participants')
    transcript = models.TextField(blank=True, help_text='Meeting transcript or notes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Meeting'
        verbose_name_plural = 'Meetings'

    def __str__(self):
        return self.title

    def get_participants_list(self):
        """Return participants as a list."""
        return [p.strip() for p in self.participants.split(',') if p.strip()]

    def get_action_items_count(self):
        """Return the count of action items for this meeting."""
        return self.action_items.count()

    def get_completed_action_items_count(self):
        """Return the count of completed action items."""
        return self.action_items.filter(status='Done').count()


class ActionItem(models.Model):
    """
    Model representing an action item extracted from a meeting.
    """
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Done', 'Done'),
    ]

    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='action_items'
    )
    description = models.TextField()
    assignee = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Action Item'
        verbose_name_plural = 'Action Items'

    def __str__(self):
        return f"{self.description[:50]}..."


class AnalysisResult(models.Model):
    """
    Model storing AI analysis results for a meeting.
    """
    meeting = models.OneToOneField(
        Meeting,
        on_delete=models.CASCADE,
        related_name='analysis_result'
    )
    summary = models.TextField()
    sentiment = models.CharField(max_length=20, help_text='Positive, Neutral, or Negative')
    sentiment_score = models.FloatField(
        help_text='Score from -1 (negative) to 1 (positive)'
    )
    productivity_score = models.FloatField(
        help_text='Score from 0 to 100'
    )
    word_count = models.PositiveIntegerField(default=0)
    action_items_extracted = models.PositiveIntegerField(default=0)
    keywords = models.TextField(help_text='Comma-separated keywords')
    follow_up_recommendations = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Analysis Result'
        verbose_name_plural = 'Analysis Results'

    def __str__(self):
        return f"Analysis for {self.meeting.title}"

    def get_keywords_list(self):
        """Return keywords as a list."""
        return [k.strip() for k in self.keywords.split(',') if k.strip()]


class MeetingReport(models.Model):
    """
    Model for storing generated meeting reports.
    """
    title = models.CharField(max_length=255)
    content = models.TextField()
    generated_at = models.DateTimeField(auto_now_add=True)
    meetings_covered = models.ManyToManyField(Meeting)

    class Meta:
        ordering = ['-generated_at']
        verbose_name = 'Meeting Report'
        verbose_name_plural = 'Meeting Reports'

    def __str__(self):
        return self.title
