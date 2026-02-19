from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    skills = models.TextField(help_text='Enter your skills, separated by commas')
    availability = models.CharField(
        max_length=100,
        choices=[
            ('Weekdays', 'Weekdays'),
            ('Weekends', 'Weekends'),
            ('Evenings', 'Evenings'),
            ('Flexible', 'Flexible'),
        ],
        default='Flexible'
    )
    bio = models.TextField(blank=True, max_length=500)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    time_credits_balance = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_average_rating(self):
        """Calculate average rating from received reviews"""
        from reviews.models import Review
        avg_rating = Review.objects.filter(reviewee=self.user).aggregate(Avg('rating'))['rating__avg']
        return round(avg_rating, 1) if avg_rating else 0

    def get_completed_tasks_count(self):
        """Get count of completed tasks as helper"""
        from tasks.models import Task
        return Task.objects.filter(assigned_to=self.user, status='Completed').count()

    def get_total_hours_earned(self):
        """Get total hours earned from completed tasks"""
        from credits.models import Transaction
        earned = Transaction.objects.filter(receiver=self.user).aggregate(total=models.Sum('amount'))['total']
        return earned if earned else 0
