"""
Database Models for AI-Based Intelligent Examination Performance Analysis System
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json


class User(AbstractUser):
    """
    Custom User Model extending AbstractUser
    Roles: 'Student' and 'Teacher'
    """
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student',
        help_text="User role: Student or Teacher"
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="Contact number"
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True,
        help_text="Date of birth"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Account creation timestamp"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update timestamp"
    )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_student(self):
        """Check if user is a student"""
        return self.role == 'student'

    @property
    def is_teacher(self):
        """Check if user is a teacher"""
        return self.role == 'teacher'


class Subject(models.Model):
    """
    Subject Model: Represents academic subjects (e.g., Math, Science, Physics)
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Subject name (e.g., Mathematics)"
    )

    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Subject code (e.g., MATH101)"
    )

    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed description of the subject"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Topic(models.Model):
    """
    Topic Model: Linked to Subject (e.g., Algebra under Math, Mechanics under Physics)
    This is crucial for "Topic-wise Analysis"
    """
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='topics',
        help_text="Subject this topic belongs to"
    )

    name = models.CharField(
        max_length=100,
        help_text="Topic name (e.g., Algebra, Geometry)"
    )

    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed description of the topic"
    )

    chapter_number = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Chapter or topic order number"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Topic"
        verbose_name_plural = "Topics"
        ordering = ['subject', 'chapter_number']
        unique_together = ['subject', 'name']

    def __str__(self):
        return f"{self.subject.name} - {self.name}"


class Exam(models.Model):
    """
    Exam Model: Represents an examination created by a teacher
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(
        max_length=200,
        help_text="Exam title"
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='exams',
        help_text="Subject of the exam"
    )

    description = models.TextField(
        blank=True,
        null=True,
        help_text="Exam description or instructions"
    )

    total_marks = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Total marks for the exam"
    )

    duration_minutes = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Duration of exam in minutes"
    )

    passing_marks = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Minimum marks required to pass"
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Exam status"
    )

    start_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When exam becomes available"
    )

    end_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When exam closes"
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_exams',
        limit_choices_to={'role': 'teacher'},
        help_text="Teacher who created the exam"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Exam"
        verbose_name_plural = "Exams"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.subject.name}"

    @property
    def question_count(self):
        """Return the number of questions in this exam"""
        return self.questions.count()

    @property
    def is_active(self):
        """Check if exam is currently active"""
        if self.status != 'published':
            return False
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True


class Question(models.Model):
    """
    Question Model: Linked to Exam and Topic
    Supports multiple choice questions (MCQ)
    """
    QUESTION_TYPE_CHOICES = [
        ('mcq', 'Multiple Choice Question'),
        ('true_false', 'True/False'),
    ]

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='questions',
        help_text="Exam this question belongs to"
    )

    topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        related_name='questions',
        help_text="Topic this question relates to (for analysis)"
    )

    question_type = models.CharField(
        max_length=10,
        choices=QUESTION_TYPE_CHOICES,
        default='mcq',
        help_text="Type of question"
    )

    text = models.TextField(
        help_text="Question text"
    )

    option_a = models.CharField(
        max_length=500,
        blank=True,
        help_text="Option A"
    )

    option_b = models.CharField(
        max_length=500,
        blank=True,
        help_text="Option B"
    )

    option_c = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Option C"
    )

    option_d = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Option D"
    )

    CORRECT_ANSWER_CHOICES = [
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
        ('True', 'True'),
        ('False', 'False'),
    ]

    correct_answer = models.CharField(
        max_length=5,
        choices=CORRECT_ANSWER_CHOICES,
        help_text="Correct answer"
    )

    marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0.5)],
        help_text="Marks for this question"
    )

    question_number = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Question order in exam"
    )

    explanation = models.TextField(
        blank=True,
        null=True,
        help_text="Explanation of the answer"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ['exam', 'question_number']
        unique_together = ['exam', 'question_number']

    def __str__(self):
        return f"Q{self.question_number}: {self.text[:50]}..."


class StudentAnswer(models.Model):
    """
    StudentAnswer Model: Stores student's answer to a question
    """
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='student_answers',
        limit_choices_to={'role': 'student'},
        help_text="Student who answered"
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='student_answers',
        help_text="Question being answered"
    )

    selected_answer = models.CharField(
        max_length=5,
        help_text="Answer selected by student"
    )

    is_correct = models.BooleanField(
        default=False,
        help_text="Whether the answer is correct"
    )

    marks_obtained = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Marks obtained for this question"
    )

    time_taken_seconds = models.IntegerField(
        null=True,
        blank=True,
        help_text="Time taken to answer this question (in seconds)"
    )

    answered_at = models.DateTimeField(
        default=timezone.now,
        help_text="Timestamp when answer was submitted"
    )

    class Meta:
        verbose_name = "Student Answer"
        verbose_name_plural = "Student Answers"
        ordering = ['answered_at']
        unique_together = ['student', 'question']

    def __str__(self):
        return f"{self.student.username} - Q{self.question.question_number} - {self.selected_answer}"

    def save(self, *args, **kwargs):
        """Auto-calculate is_correct and marks_obtained"""
        if self.selected_answer == self.question.correct_answer:
            self.is_correct = True
            self.marks_obtained = self.question.marks
        else:
            self.is_correct = False
            self.marks_obtained = 0
        super().save(*args, **kwargs)


class ExamResult(models.Model):
    """
    ExamResult Model: Stores overall exam results for a student
    """
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='exam_results',
        limit_choices_to={'role': 'student'},
        help_text="Student who took the exam"
    )

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='results',
        help_text="Exam that was taken"
    )

    score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Total marks obtained"
    )

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage score"
    )

    total_questions = models.IntegerField(
        help_text="Total number of questions"
    )

    correct_answers = models.IntegerField(
        help_text="Number of correct answers"
    )

    wrong_answers = models.IntegerField(
        help_text="Number of wrong answers"
    )

    time_taken_minutes = models.IntegerField(
        help_text="Total time taken to complete exam (in minutes)"
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('passed', 'Passed'),
            ('failed', 'Failed'),
        ],
        help_text="Exam result status"
    )

    completed_at = models.DateTimeField(
        default=timezone.now,
        help_text="Timestamp when exam was completed"
    )

    class Meta:
        verbose_name = "Exam Result"
        verbose_name_plural = "Exam Results"
        ordering = ['-completed_at']
        unique_together = ['student', 'exam']

    def __str__(self):
        return f"{self.student.username} - {self.exam.title} - {self.percentage}%"


class PerformanceAnalysis(models.Model):
    """
    PerformanceAnalysis Model: Linked to Student and Subject
    Stores the "AI" analysis output including weak topics, strong topics, and suggestions
    """
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='performance_analyses',
        limit_choices_to={'role': 'student'},
        help_text="Student being analyzed"
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='performance_analyses',
        help_text="Subject being analyzed"
    )

    weak_topics = models.JSONField(
        default=dict,
        help_text="JSON object containing weak topics with accuracy percentages"
    )

    strong_topics = models.JSONField(
        default=dict,
        help_text="JSON object containing strong topics with accuracy percentages"
    )

    overall_accuracy = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Overall accuracy percentage in this subject"
    )

    total_attempts = models.IntegerField(
        default=0,
        help_text="Total number of questions attempted in this subject"
    )

    avg_time_per_question = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Average time taken per question (in seconds)"
    )

    suggestions = models.TextField(
        help_text="AI-generated textual suggestions for improvement"
    )

    detailed_insights = models.JSONField(
        default=dict,
        blank=True,
        help_text="Detailed insights about performance (topic-wise breakdown, trends, etc.)"
    )

    last_updated = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp of last analysis update"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when first analysis was created"
    )

    class Meta:
        verbose_name = "Performance Analysis"
        verbose_name_plural = "Performance Analyses"
        ordering = ['-last_updated']
        unique_together = ['student', 'subject']

    def __str__(self):
        return f"{self.student.username} - {self.subject.name} Analysis"

    def get_weak_topics_list(self):
        """Return weak topics as a list of tuples (topic_name, accuracy)"""
        return [(topic, accuracy) for topic, accuracy in self.weak_topics.items()]

    def get_strong_topics_list(self):
        """Return strong topics as a list of tuples (topic_name, accuracy)"""
        return [(topic, accuracy) for topic, accuracy in self.strong_topics.items()]


class ExamProgress(models.Model):
    """
    ExamProgress Model: Tracks student's progress while taking an exam
    Used for resuming exams and tracking time
    """
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='exam_progress',
        limit_choices_to={'role': 'student'}
    )

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='progress_records'
    )

    started_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When student started the exam"
    )

    last_activity = models.DateTimeField(
        auto_now=True,
        help_text="Last activity timestamp"
    )

    current_question = models.IntegerField(
        default=1,
        help_text="Current question number"
    )

    answers_json = models.JSONField(
        default=dict,
        help_text="Temporary storage of answers before submission"
    )

    is_completed = models.BooleanField(
        default=False,
        help_text="Whether exam has been completed"
    )

    class Meta:
        verbose_name = "Exam Progress"
        verbose_name_plural = "Exam Progress Records"
        ordering = ['-started_at']
        unique_together = ['student', 'exam']

    def __str__(self):
        return f"{self.student.username} - {self.exam.title} - {'Completed' if self.is_completed else 'In Progress'}"
