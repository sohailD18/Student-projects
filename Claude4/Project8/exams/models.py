"""
Exam Model for Government Examinations
"""
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class ExamCategory(models.Model):
    """
    Dynamic categorization for examinations
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, help_text="Short code for category (e.g., UPSC, SSC)")
    description = models.TextField(blank=True, null=True)
    icon_class = models.CharField(max_length=50, blank=True, null=True, help_text="Bootstrap icon class (e.g., bi-mortarboard)")
    is_active = models.BooleanField(default=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Exam Category'
        verbose_name_plural = 'Exam Categories'

    def __str__(self):
        return self.name

    @property
    def exam_count(self):
        """Return number of exams in this category"""
        return self.exams.count()


class Exam(models.Model):
    """
    Model representing a Government Examination
    """
    EXAM_TYPES = [
        ('UPSC', 'Union Public Service Commission'),
        ('SSC', 'Staff Selection Commission'),
        ('BANKING', 'Banking Exams'),
        ('RAILWAYS', 'Indian Railways'),
        ('STATE_PSC', 'State Public Service Commission'),
        ('DEFENCE', 'Defence Services'),
    ]

    # Basic Information
    title = models.CharField(max_length=255)
    category = models.ForeignKey(
        'ExamCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exams',
        help_text="Dynamic exam category"
    )
    exam_type = models.CharField(
        max_length=20,
        choices=EXAM_TYPES,
        default='STATE_PSC',
        editable=False  # Auto-synced from category.code
    )
    official_link = models.URLField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    # Eligibility Criteria
    eligibility_criteria = models.TextField(blank=True, null=True, help_text="Detailed eligibility requirements")
    age_limit_min = models.IntegerField(
        validators=[MinValueValidator(16), MaxValueValidator(60)],
        help_text="Minimum age limit in years"
    )
    age_limit_max = models.IntegerField(
        validators=[MinValueValidator(16), MaxValueValidator(65)],
        help_text="Maximum age limit in years"
    )
    educational_qualification = models.CharField(
        max_length=255,
        help_text="Required educational qualification (e.g., 10th, 12th, Graduate)"
    )

    # Syllabus and Details
    syllabus_text = models.TextField(blank=True, null=True, help_text="Exam syllabus in detail")

    # Important Dates
    application_start_date = models.DateField(help_text="Application form start date")
    application_end_date = models.DateField(help_text="Application form end date")
    exam_date = models.DateField(help_text="Scheduled examination date")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-application_start_date']
        verbose_name = 'Government Exam'
        verbose_name_plural = 'Government Exams'

    def __str__(self):
        if self.category:
            return f"{self.title} ({self.category.name})"
        return f"{self.title} ({self.get_exam_type_display()})"

    def save(self, *args, **kwargs):
        """Auto-sync exam_type from category.code for backward compatibility"""
        if self.category:
            self.exam_type = self.category.code
        super().save(*args, **kwargs)

    def is_upcoming(self):
        """Check if the exam is upcoming (application or exam date is in future)"""
        today = timezone.now().date()
        return self.exam_date >= today

    def is_application_open(self):
        """Check if application window is currently open"""
        today = timezone.now().date()
        return self.application_start_date <= today <= self.application_end_date

    def is_expired(self):
        """Check if the exam is expired (exam date has passed)"""
        today = timezone.now().date()
        return self.exam_date < today

    def days_until_application_deadline(self):
        """Returns number of days until application deadline"""
        today = timezone.now().date()
        if self.application_end_date >= today:
            return (self.application_end_date - today).days
        return 0

    def days_until_exam(self):
        """Returns number of days until exam date"""
        today = timezone.now().date()
        if self.exam_date >= today:
            return (self.exam_date - today).days
        return 0
