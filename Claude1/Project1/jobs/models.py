from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import UserProfile


class JobCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Job Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
    ]

    EXPERIENCE_LEVEL_CHOICES = [
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('executive', 'Executive'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, related_name='jobs')
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, default='mid')
    description = models.TextField()
    requirements = models.TextField()
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_salary_visible = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    application_deadline = models.DateField(null=True, blank=True)
    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Jobs'

    def __str__(self):
        return f"{self.title} at {self.company}"

    @property
    def application_count(self):
        return self.applications.count()


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('interviewed', 'Interviewed'),
        ('offered', 'Offered'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    cover_letter = models.TextField()
    resume = models.FileField(upload_to='resumes/%Y/%m/')
    linkedin_profile = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    expected_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, help_text='Internal notes about the application')

    class Meta:
        ordering = ['-applied_at']
        verbose_name_plural = 'Job Applications'
        unique_together = ['job', 'email']

    def __str__(self):
        return f"{self.applicant_name} - {self.job.title}"


class SavedJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'job']
        verbose_name_plural = 'Saved Jobs'

    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"


class Skill(models.Model):
    """Database of skills for matching"""
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(JobCategory, on_delete=models.CASCADE, related_name='skills', null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Skills'

    def __str__(self):
        return self.name


class CandidateSkill(models.Model):
    """Skills possessed by job seekers"""
    SKILL_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]

    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='candidate_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='candidates')
    level = models.CharField(max_length=20, choices=SKILL_LEVEL_CHOICES, default='intermediate')
    years_of_experience = models.IntegerField(default=0)
    verified = models.BooleanField(default=False, help_text='If skill is verified via resume/project')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user_profile', 'skill']
        verbose_name_plural = 'Candidate Skills'

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.skill.name} ({self.level})"


class WorkExperience(models.Model):
    """Work experience for job seekers"""
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='work_experiences')
    company_name = models.CharField(max_length=200)
    job_title = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name_plural = 'Work Experiences'

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"


class Education(models.Model):
    """Education for job seekers"""
    DEGREE_TYPE_CHOICES = [
        ('certificate', 'Certificate'),
        ('diploma', 'Diploma'),
        ('bachelor', 'Bachelor\'s'),
        ('master', 'Master\'s'),
        ('phd', 'PhD'),
    ]

    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='educations')
    institution = models.CharField(max_length=200)
    degree_type = models.CharField(max_length=20, choices=DEGREE_TYPE_CHOICES)
    field_of_study = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name_plural = 'Education'

    def __str__(self):
        return f"{self.degree_type} in {self.field_of_study} from {self.institution}"


class JobMatch(models.Model):
    """AI-generated job-candidate matches"""
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='matches')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_matches')
    match_score = models.IntegerField(help_text='Match score from 0-100')
    match_reasons = models.TextField(help_text='JSON string explaining match reasons')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['job', 'candidate']
        verbose_name_plural = 'Job Matches'

    def __str__(self):
        return f"{self.candidate.username} matched with {self.job.title} ({self.match_score}%)"


class CandidateRecommendation(models.Model):
    """AI-generated job recommendations for candidates"""
    STATUS_CHOICES = [
        ('new', 'New'),
        ('viewed', 'Viewed'),
        ('applied', 'Applied'),
        ('dismissed', 'Dismissed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='recommended_to')
    score = models.IntegerField(help_text='Recommendation score from 0-100')
    reason = models.TextField(help_text='Explanation of why this job is recommended')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'job']
        verbose_name_plural = 'Candidate Recommendations'

    def __str__(self):
        return f"{self.job.title} recommended to {self.user.username} ({self.score}%)"


class Notification(models.Model):
    """User notifications"""
    NOTIFICATION_TYPES = [
        ('job_application', 'New Job Application'),
        ('job_recommendation', 'Job Recommendation'),
        ('application_status', 'Application Status Update'),
        ('interview_invitation', 'Interview Invitation'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"{self.title} for {self.recipient.username}"


# ============================================================================
# INTERVIEW BOT MODULE - ML-Driven Questioning + Scoring
# ============================================================================

class InterviewQuestion(models.Model):
    """Question bank for AI interviews"""
    QUESTION_TYPES = [
        ('technical', 'Technical Question'),
        ('behavioral', 'Behavioral Question'),
        ('situational', 'Situational Question'),
        ('experience', 'Experience-Based Question'),
        ('mcq', 'Multiple Choice Question'),
    ]

    DIFFICULTY_LEVELS = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    category = models.ForeignKey(JobCategory, on_delete=models.CASCADE, related_name='interview_questions', null=True, blank=True)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='technical')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='medium')
    question = models.TextField()
    expected_keywords = models.JSONField(default=list, help_text='List of keywords expected in the answer')
    sample_answer = models.TextField(blank=True, help_text='Sample ideal answer for reference')
    skills_tested = models.ManyToManyField(Skill, related_name='interview_questions', blank=True)
    max_score = models.IntegerField(default=10, help_text='Maximum score for this question')
    is_active = models.BooleanField(default=True)

    # MCQ specific fields
    choices = models.JSONField(default=list, blank=True, help_text='List of choices for MCQ (e.g., ["A", "B", "C", "D"])')
    correct_answer = models.CharField(max_length=200, blank=True, help_text='Correct answer for MCQ')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'difficulty', 'question_type']
        verbose_name_plural = 'Interview Questions'

    def __str__(self):
        return f"{self.get_question_type_display()} - {self.question[:50]}..."


class InterviewSession(models.Model):
    """Interview session for a candidate-job pair"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='interview_sessions')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interview_sessions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_score = models.IntegerField(default=0, help_text='Total interview score out of 100')
    max_score = models.IntegerField(default=100, help_text='Maximum possible score')
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    feedback = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_limit_minutes = models.IntegerField(default=30, help_text='Time limit for the interview')

    class Meta:
        unique_together = ['job', 'candidate']
        ordering = ['-started_at']
        verbose_name_plural = 'Interview Sessions'

    def __str__(self):
        return f"Interview: {self.candidate.username} for {self.job.title}"

    @property
    def is_completed(self):
        return self.status == 'completed'

    @property
    def score_grade(self):
        """Get letter grade based on percentage"""
        if self.percentage >= 90:
            return 'A+ (Excellent)'
        elif self.percentage >= 80:
            return 'A (Very Good)'
        elif self.percentage >= 70:
            return 'B (Good)'
        elif self.percentage >= 60:
            return 'C (Average)'
        elif self.percentage >= 50:
            return 'D (Below Average)'
        else:
            return 'F (Poor)'


class InterviewResponse(models.Model):
    """Candidate's response to an interview question"""
    interview_session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(InterviewQuestion, on_delete=models.CASCADE, related_name='responses')
    answer = models.TextField()
    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=10)
    feedback = models.TextField(blank=True, help_text='AI-generated feedback on the response')
    keywords_found = models.JSONField(default=list, help_text='Keywords found in the answer')
    created_at = models.DateTimeField(auto_now_add=True)
    time_taken_seconds = models.IntegerField(null=True, blank=True, help_text='Time taken to answer in seconds')

    class Meta:
        unique_together = ['interview_session', 'question']
        ordering = ['interview_session', 'created_at']
        verbose_name_plural = 'Interview Responses'

    def __str__(self):
        return f"Response by {self.interview_session.candidate.username} for Q: {self.question.question[:30]}..."
