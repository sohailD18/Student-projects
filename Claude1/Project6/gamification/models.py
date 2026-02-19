from django.db import models
from django.contrib.auth.models import User

class Badge(models.Model):
    BADGE_TYPES = [
        ('tasks_completed', 'Tasks Completed'),
        ('hours_earned', 'Hours Earned'),
        ('reviews_given', 'Reviews Given'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    badge_type = models.CharField(max_length=20, choices=BADGE_TYPES)
    requirement_value = models.IntegerField(
        help_text='Value required to earn this badge'
    )
    icon_name = models.CharField(
        max_length=50,
        default='fa-award',
        help_text='FontAwesome icon class'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['badge_type', 'requirement_value']

    def __str__(self):
        return self.name

class UserBadge(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='badges'
    )
    badge = models.ForeignKey(
        Badge,
        on_delete=models.CASCADE,
        related_name='awarded_to'
    )
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-earned_at']
        unique_together = ['user', 'badge']

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"


# Helper function to check and award badges
def check_and_award_badges(user):
    """Check if user qualifies for any badges and award them"""
    from users.models import Profile
    from reviews.models import Review

    profile = user.profile

    # Get all badges
    all_badges = Badge.objects.all()

    for badge in all_badges:
        # Skip if user already has this badge
        if UserBadge.objects.filter(user=user, badge=badge).exists():
            continue

        earned = False

        if badge.badge_type == 'tasks_completed':
            completed_tasks = profile.get_completed_tasks_count()
            if completed_tasks >= badge.requirement_value:
                earned = True

        elif badge.badge_type == 'hours_earned':
            total_hours = profile.get_total_hours_earned()
            if total_hours >= badge.requirement_value:
                earned = True

        elif badge.badge_type == 'reviews_given':
            review_count = Review.objects.filter(reviewer=user).count()
            if review_count >= badge.requirement_value:
                earned = True

        if earned:
            UserBadge.objects.create(user=user, badge=badge)
