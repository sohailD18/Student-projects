from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    task = models.OneToOneField(
        'tasks.Task',
        on_delete=models.CASCADE,
        related_name='review'
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='given_reviews'
    )
    reviewee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_reviews'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Rating from 1 to 5'
    )
    comment = models.TextField(blank=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'

    def __str__(self):
        return f"Review for {self.reviewee.username} - {self.rating}/5"

    def clean(self):
        """Validate review constraints"""
        # Ensure task is completed
        if self.task.status != 'Completed':
            raise ValidationError("Can only review completed tasks")

        # Ensure reviewer is either creator or assignee
        if self.reviewer not in [self.task.created_by, self.task.assigned_to]:
            raise ValidationError("Only task participants can leave reviews")

        # Ensure reviewee is the other party
        if self.reviewer == self.task.created_by:
            expected_reviewee = self.task.assigned_to
        else:
            expected_reviewee = self.task.created_by

        if self.reviewee != expected_reviewee:
            raise ValidationError("Invalid reviewee for this task")

        # Check if review already exists
        if Review.objects.filter(
            task=self.task,
            reviewer=self.reviewer
        ).exists() and not self.pk:
            raise ValidationError("You have already reviewed this task")
