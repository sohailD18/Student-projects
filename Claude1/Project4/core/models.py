from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ActivityLog(models.Model):
    ACTIVITY_TYPES = [
        ('Travel', 'Travel'),
        ('Energy', 'Energy'),
        ('Diet', 'Diet'),
    ]

    TRAVEL_SUBTYPES = [
        ('car', 'Car'),
        ('bus', 'Bus'),
        ('train', 'Train'),
        ('bike', 'Bicycle'),
        ('walking', 'Walking'),
        ('flight', 'Flight'),
    ]

    DIET_SUBTYPES = [
        ('vegan', 'Vegan'),
        ('vegetarian', 'Vegetarian'),
        ('meat', 'Meat-Based'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    activity_subtype = models.CharField(max_length=20, blank=True, null=True)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    calculated_carbon = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, help_text="Additional notes about this activity")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'

    def calculate_emission(self):
        """
        Calculate carbon emissions based on activity type and subtype.
        Travel: value (km) * emission factor
        Energy: value (kWh) * 0.5
        Diet: value (meals) * emission factor
        """
        if self.activity_type == 'Travel':
            # Different emission factors for travel types (kg CO2 per km)
            travel_factors = {
                'car': 0.21,
                'bus': 0.089,
                'train': 0.041,
                'bike': 0.0,
                'walking': 0.0,
                'flight': 0.255,
            }
            factor = travel_factors.get(self.activity_subtype, 0.2)
        elif self.activity_type == 'Energy':
            factor = 0.5  # kg CO2 per kWh
        elif self.activity_type == 'Diet':
            # Different emission factors per meal (kg CO2)
            diet_factors = {
                'vegan': 1.5,
                'vegetarian': 1.7,
                'meat': 2.5,
            }
            factor = diet_factors.get(self.activity_subtype, 2.0)
        else:
            factor = 0
        return self.value * factor

    def save(self, *args, **kwargs):
        # Auto-calculate carbon emissions before saving
        self.calculated_carbon = self.calculate_emission()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} on {self.date}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    total_points = models.IntegerField(default=0)
    bio = models.TextField(max_length=500, blank=True, help_text="Tell others about your sustainability journey")
    location = models.CharField(max_length=100, blank=True, help_text="Your city or region")
    avatar_url = models.URLField(blank=True, help_text="URL to your profile picture")
    streak_days = models.IntegerField(default=0, help_text="Current streak of consecutive days with activities")
    longest_streak = models.IntegerField(default=0, help_text="Longest streak achieved")
    last_activity_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username}'s Profile - {self.total_points} points"

    def update_streak(self):
        """Update the user's activity streak."""
        today = timezone.now().date()
        if self.last_activity_date == today:
            return  # Already logged today

        if self.last_activity_date == today - timezone.timedelta(days=1):
            # Continuing the streak
            self.streak_days += 1
        elif self.last_activity_date is None or self.last_activity_date < today - timezone.timedelta(days=1):
            # Streak broken or starting new
            self.streak_days = 1

        if self.streak_days > self.longest_streak:
            self.longest_streak = self.streak_days

        self.last_activity_date = today
        self.save()


class Badge(models.Model):
    CATEGORY_CHOICES = [
        ('points', 'Points-Based'),
        ('streak', 'Streak-Based'),
        ('activities', 'Activity-Based'),
        ('special', 'Special Achievement'),
    ]

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    points_required = models.IntegerField(default=0, help_text="Points required to earn this badge")
    streak_required = models.IntegerField(default=0, help_text="Streak days required (0 if not applicable)")
    activities_required = models.IntegerField(default=0, help_text="Number of activities required (0 if not applicable)")
    icon = models.CharField(max_length=50, blank=True, help_text="Icon name or emoji")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='points')
    rarity = models.CharField(max_length=20, choices=[('common', 'Common'), ('rare', 'Rare'), ('epic', 'Epic'), ('legendary', 'Legendary')], default='common')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['points_required', 'streak_required', 'activities_required']
        verbose_name = 'Badge'
        verbose_name_plural = 'Badges'

    def __str__(self):
        return f"{self.name} ({self.get_rarity_display()})"


class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='earned_by')
    date_earned = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_earned']
        verbose_name = 'User Badge'
        verbose_name_plural = 'User Badges'
        unique_together = ['user', 'badge']  # Prevent duplicate badges

    def __str__(self):
        return f"{self.user.username} earned {self.badge.name} on {self.date_earned.strftime('%Y-%m-%d')}"


class Challenge(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('upcoming', 'Upcoming'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    target_points = models.IntegerField(help_text="Points required to complete the challenge")
    reward_points = models.IntegerField(default=0, help_text="Bonus points for completing the challenge")
    badge = models.ForeignKey(Badge, on_delete=models.SET_NULL, null=True, blank=True, related_name='challenges', help_text="Badge awarded upon completion")
    max_participants = models.IntegerField(default=0, help_text="0 for unlimited")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date', '-created_at']
        verbose_name = 'Challenge'
        verbose_name_plural = 'Challenges'

    def __str__(self):
        return f"{self.title} ({self.start_date} to {self.end_date})"

    @property
    def participant_count(self):
        return self.participants.count()

    @property
    def is_active(self):
        today = timezone.now().date()
        return self.status == 'active' and self.start_date <= today <= self.end_date


class ChallengeParticipant(models.Model):
    STATUS_CHOICES = [
        ('joined', 'Joined'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='challenges')
    points_earned = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='joined')
    joined_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-joined_at']
        verbose_name = 'Challenge Participant'
        verbose_name_plural = 'Challenge Participants'
        unique_together = ['challenge', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.challenge.title} ({self.status})"

    @property
    def progress_percentage(self):
        if self.challenge.target_points == 0:
            return 0
        return min(100, int((self.points_earned / self.challenge.target_points) * 100))


class UserGoal(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('achieved', 'Achieved'),
        ('missed', 'Missed'),
        ('cancelled', 'Cancelled'),
    ]

    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    goal_type = models.CharField(max_length=20, choices=[('points', 'Points'), ('activities', 'Number of Activities'), ('carbon', 'Carbon Reduction')], default='points')
    target_value = models.DecimalField(max_digits=10, decimal_places=2)
    current_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='weekly')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Goal'
        verbose_name_plural = 'User Goals'

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    @property
    def progress_percentage(self):
        if self.target_value == 0:
            return 0
        return min(100, int((self.current_value / self.target_value) * 100))

    @property
    def is_achieved(self):
        return self.current_value >= self.target_value

    def check_completion(self):
        """Check if goal is achieved and update status."""
        if self.is_achieved and self.status == 'active':
            self.status = 'achieved'
            self.save()


class Achievement(models.Model):
    """One-time special achievements beyond the badge system."""
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True)
    points_reward = models.IntegerField(default=0)
    is_hidden = models.BooleanField(default=False, help_text="Hidden achievements aren't shown until earned")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'Achievement'
        verbose_name_plural = 'Achievements'

    def __str__(self):
        return f"{self.title} (+{self.points_reward} pts)"


class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='earned_by')
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-earned_at']
        verbose_name = 'User Achievement'
        verbose_name_plural = 'User Achievements'
        unique_together = ['user', 'achievement']

    def __str__(self):
        return f"{self.user.username} - {self.achievement.title}"
