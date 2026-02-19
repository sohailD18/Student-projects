from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import json


class Student(models.Model):
    """
    Represents a student who can take exams.
    """
    name = models.CharField(max_length=200, help_text="Full name of the student")
    student_id = models.CharField(max_length=50, unique=True, help_text="Unique student identifier")

    def __str__(self):
        return f"{self.name} ({self.student_id})"

    class Meta:
        ordering = ['name']


class Exam(models.Model):
    """
    Represents an exam that students can take.
    """
    subject = models.CharField(max_length=200, help_text="Subject or title of the exam")
    duration = models.PositiveIntegerField(help_text="Duration of the exam in minutes")
    instructions = models.TextField(blank=True, help_text="Exam instructions for students")
    passing_score = models.PositiveIntegerField(
        default=40,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Minimum passing score percentage"
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when exam was created")
    created_by = models.CharField(
        max_length=100,
        blank=True,
        help_text="Admin/instructor who created the exam"
    )

    def __str__(self):
        return f"{self.subject} ({self.duration} mins)"

    def question_count(self):
        """Return the number of questions in this exam."""
        return self.questions.count()

    class Meta:
        ordering = ['-created_at']


class ProctorLog(models.Model):
    """
    Records monitoring events and violations during exams.
    """
    VIOLATION_TYPES = [
        ('tab_switch', 'Tab Switch'),
        ('copy_paste', 'Copy/Paste Detected'),
        ('no_face', 'No Face Detected'),
        ('multiple_faces', 'Multiple Faces Detected'),
        ('phone_detected', 'Phone Detected'),
        ('suspicious_object', 'Suspicious Object'),
        ('no_movement', 'No Movement (Long Period)'),
        ('other', 'Other Violation'),
    ]

    # Severity levels and their point values
    SEVERITY_LEVELS = {
        'tab_switch': 5,          # Low severity
        'copy_paste': 10,          # Medium severity
        'no_movement': 5,          # Low severity
        'no_face': 15,             # High severity
        'multiple_faces': 25,      # Very high severity
        'phone_detected': 30,      # Critical severity
        'suspicious_object': 20,   # High severity
        'other': 10,               # Default medium severity
    }

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='proctor_logs',
        help_text="Student who committed the violation"
    )
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='proctor_logs',
        help_text="Exam during which the violation occurred"
    )
    timestamp = models.DateTimeField(auto_now_add=True, help_text="When the violation was detected")
    violation_type = models.CharField(
        max_length=50,
        choices=VIOLATION_TYPES,
        help_text="Type of violation detected"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional details about the violation"
    )

    def __str__(self):
        return f"{self.student.name} - {self.get_violation_type_display()} ({self.timestamp})"

    @classmethod
    def get_severity_points(cls, violation_type):
        """Return the severity points for a given violation type."""
        return cls.SEVERITY_LEVELS.get(violation_type, 10)

    def severity_points(self):
        """Return the severity points for this violation."""
        return self.get_severity_points(self.violation_type)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Proctor Log'
        verbose_name_plural = 'Proctor Logs'


class Question(models.Model):
    """
    Represents a question in an exam.
    """
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='questions',
        help_text="Exam this question belongs to"
    )
    question_text = models.TextField(help_text="The question text")
    order = models.PositiveIntegerField(default=1, help_text="Order of question in exam")

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}..."

    def correct_choice(self):
        """Return the correct choice for this question."""
        return self.choices.filter(is_correct=True).first()

    class Meta:
        ordering = ['exam', 'order']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'


class Choice(models.Model):
    """
    Represents a choice option for a question.
    """
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices',
        help_text="Question this choice belongs to"
    )
    choice_text = models.CharField(max_length=500, help_text="The choice text")
    is_correct = models.BooleanField(default=False, help_text="Whether this is the correct answer")
    order = models.PositiveIntegerField(default=1, help_text="Order of choice")

    def __str__(self):
        return f"{self.question.question_text[:30]}... - {self.choice_text}"

    class Meta:
        ordering = ['question', 'order']
        verbose_name = 'Choice'
        verbose_name_plural = 'Choices'


class ExamSession(models.Model):
    """
    Records an exam session for monitoring and recording purposes.
    """
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('terminated', 'Terminated'),
        ('auto_submitted', 'Auto Submitted'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='exam_sessions',
        help_text="Student taking the exam"
    )
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='exam_sessions',
        help_text="Exam being taken"
    )
    start_time = models.DateTimeField(auto_now_add=True, help_text="When the exam session started")
    end_time = models.DateTimeField(null=True, blank=True, help_text="When the exam session ended")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress',
        help_text="Current status of the exam session"
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="IP address of student")
    browser_info = models.TextField(blank=True, help_text="Browser user agent string")
    violation_count = models.PositiveIntegerField(default=0, help_text="Total violations during session")
    screenshot_captured = models.BooleanField(default=False, help_text="Whether screenshots were captured")

    def __str__(self):
        return f"{self.student.name} - {self.exam.subject} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"

    def duration_minutes(self):
        """Calculate actual duration of the exam session."""
        if self.end_time:
            duration = self.end_time - self.start_time
            return int(duration.total_seconds() / 60)
        return None

    class Meta:
        ordering = ['-start_time']
        verbose_name = 'Exam Session'
        verbose_name_plural = 'Exam Sessions'


class ExamResult(models.Model):
    """
    Stores the results of a completed exam.
    """
    STATUS_CHOICES = [
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('pending', 'Pending Review'),
    ]

    session = models.OneToOneField(
        ExamSession,
        on_delete=models.CASCADE,
        related_name='result',
        help_text="The exam session this result belongs to"
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='exam_results',
        help_text="Student who took the exam"
    )
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='results',
        help_text="Exam that was taken"
    )
    score = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Score achieved as percentage"
    )
    total_questions = models.PositiveIntegerField(default=0, help_text="Total number of questions")
    correct_answers = models.PositiveIntegerField(default=0, help_text="Number of correct answers")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        help_text="Pass/Fail status"
    )
    answers = models.JSONField(default=dict, help_text="Student's answers stored as JSON")
    integrity_score = models.PositiveIntegerField(
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Integrity score from proctoring (0-100)"
    )
    risk_score = models.PositiveIntegerField(default=0, help_text="Risk score based on violations")
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the result was generated")

    def __str__(self):
        return f"{self.student.name} - {self.exam.subject}: {self.score}% ({self.get_status_display()})"

    def calculate_status(self):
        """Determine pass/fail status based on score."""
        if self.score >= self.exam.passing_score:
            return 'pass'
        return 'fail'

    def save(self, *args, **kwargs):
        # Auto-calculate status if not set
        if not self.status:
            self.status = self.calculate_status()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Exam Result'
        verbose_name_plural = 'Exam Results'
