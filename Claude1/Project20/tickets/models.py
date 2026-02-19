from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Complaint(models.Model):
    """Stores customer complaint details before creating a ticket."""

    CATEGORY_CHOICES = [
        ('technical', 'Technical Issue'),
        ('billing', 'Billing & Payment'),
        ('feature', 'Feature Request'),
        ('bug', 'Bug Report'),
        ('other', 'Other'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Complaint'
        verbose_name_plural = 'Complaints'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.get_category_display()}"


class Ticket(models.Model):
    """Represents a support ticket generated from a complaint."""

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('escalated', 'Escalated'),
        ('closed', 'Closed'),
    ]

    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='tickets')
    unique_ticket_id = models.CharField(max_length=20, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    assigned_staff = models.CharField(max_length=100, blank=True, null=True)
    is_escalated = models.BooleanField(default=False, help_text='Whether this ticket has been escalated')
    escalated_at = models.DateTimeField(blank=True, null=True, help_text='When the ticket was escalated')
    escalated_by = models.CharField(max_length=100, blank=True, null=True, help_text='Who escalated this ticket')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['-created_at']

    def __str__(self):
        return f"Ticket #{self.unique_ticket_id} - {self.complaint.name}"

    def save(self, *args, **kwargs):
        """Auto-generate unique ticket ID if not exists."""
        from django.utils import timezone

        # Auto-generate ticket ID
        if not self.unique_ticket_id:
            from django.db.models import Max
            last_ticket = Ticket.objects.aggregate(Max('id'))
            last_id = last_ticket['id__max'] or 0
            new_number = last_id + 1
            self.unique_ticket_id = f"HDP-{new_number:03d}"

        # Track escalation automatically
        if self.status == 'escalated' and not self.is_escalated:
            self.is_escalated = True
            if not self.escalated_at:
                self.escalated_at = timezone.now()
        elif self.status != 'escalated' and self.is_escalated:
            # Keep escalation flag true even if status changes
            pass

        super().save(*args, **kwargs)

    def escalate(self, escalated_by='System'):
        """Mark this ticket as escalated.

        Args:
            escalated_by: Name of the person escalating the ticket

        Returns:
            The updated ticket instance
        """
        from django.utils import timezone

        self.status = 'escalated'
        self.is_escalated = True
        self.escalated_at = timezone.now()
        self.escalated_by = escalated_by
        self.save()
        return self


class Feedback(models.Model):
    """Customer feedback for a closed ticket."""

    RATING_CHOICES = [
        (1, '⭐ Poor'),
        (2, '⭐⭐ Fair'),
        (3, '⭐⭐⭐ Good'),
        (4, '⭐⭐⭐⭐ Very Good'),
        (5, '⭐⭐⭐⭐⭐ Excellent'),
    ]

    ticket = models.OneToOneField(
        Ticket,
        on_delete=models.CASCADE,
        related_name='feedback',
        verbose_name='Ticket'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Rating from 1 to 5'
    )
    comments = models.TextField(
        blank=True,
        help_text='Additional comments about the support experience'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedback'
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback for {self.ticket.unique_ticket_id} - {self.get_rating_display()}"

    def get_stars(self):
        """Return star representation of rating."""
        return '⭐' * self.rating
