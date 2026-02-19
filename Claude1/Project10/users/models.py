from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User


class Badge(models.Model):
    """Achievement badges users can earn"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True, help_text='Emoji or icon name')
    points_required = models.IntegerField(default=0, help_text='Points needed to earn this badge')
    sessions_required = models.IntegerField(default=0, help_text='Completed sessions needed to earn this badge')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['points_required', 'sessions_required']

    def __str__(self):
        return f"{self.icon} {self.name}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    skills_to_teach = models.CharField(max_length=500, blank=True, help_text='Comma-separated skills you can teach')
    skills_to_learn = models.CharField(max_length=500, blank=True, help_text='Comma-separated skills you want to learn')
    points_earned = models.IntegerField(default=0)
    badges = models.ManyToManyField(Badge, blank=True, related_name='users')

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def check_and_award_badges(self):
        """Check and award badges based on achievements"""
        from core.models import Session

        # Get completed session count
        completed_sessions = Session.objects.filter(
            Q(teacher=self.user) | Q(student=self.user),
            status='completed'
        ).count()

        # Find eligible badges
        eligible_badges = Badge.objects.filter(
            points_required__lte=self.points_earned,
            sessions_required__lte=completed_sessions
        ).exclude(id__in=self.badges.all())

        # Award new badges
        for badge in eligible_badges:
            self.badges.add(badge)

        return eligible_badges.count()
