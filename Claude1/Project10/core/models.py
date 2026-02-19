from django.db import models
from django.contrib.auth.models import User


class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('tech', 'Technology'),
        ('art', 'Art & Design'),
        ('language', 'Language'),
        ('music', 'Music'),
        ('cooking', 'Cooking'),
        ('sports', 'Sports & Fitness'),
        ('academic', 'Academic'),
        ('other', 'Other'),
    ]

    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills_teaching')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    hourly_rate_points = models.IntegerField(help_text='Points required per session')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - by {self.teacher.username}"


class Session(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions_learning')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions_teaching')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='sessions')
    scheduled_time = models.DateTimeField(help_text='When the session is scheduled')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.skill.title} - {self.student.username} with {self.teacher.username}"


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]

    session = models.OneToOneField(Session, on_delete=models.CASCADE, related_name='review')
    rating = models.IntegerField(choices=RATING_CHOICES, help_text='Rating from 1 to 5')
    comment = models.TextField(blank=True, help_text='Optional review comment')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review for {self.session.skill.title} - {self.rating}/5"
