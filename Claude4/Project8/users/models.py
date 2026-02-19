"""
User Profile Model for Aspirants
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date


def calculate_age(date_of_birth):
    """Calculate age from date of birth"""
    today = date.today()
    return today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))


class UserProfile(models.Model):
    """
    Extended profile for aspirants
    """
    CATEGORY_CHOICES = [
        ('GEN', 'General'),
        ('OBC', 'Other Backward Classes'),
        ('SC', 'Scheduled Castes'),
        ('ST', 'Scheduled Tribes'),
        ('EWS', 'Economically Weaker Section'),
        ('PWD', 'Persons with Disabilities'),
    ]

    QUALIFICATION_CHOICES = [
        ('10TH', '10th / Matriculation'),
        ('12TH', '12th / Intermediate'),
        ('DIPLOMA', 'Diploma'),
        ('GRADUATE', 'Graduate'),
        ('POST_GRADUATE', 'Post Graduate'),
        ('PHD', 'Doctorate (PhD)'),
        ('OTHER', 'Other'),
    ]

    # Link to Django User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # Personal Details
    date_of_birth = models.DateField(blank=True, null=True, help_text="Date of Birth")
    category = models.CharField(max_length=5, choices=CATEGORY_CHOICES, default='GEN')

    # Educational Details
    highest_qualification = models.CharField(
        max_length=20,
        choices=QUALIFICATION_CHOICES,
        default='GRADUATE',
        help_text="Highest educational qualification"
    )

    # Location
    state = models.CharField(max_length=100, blank=True, null=True, help_text="State of residence")

    # Preferences
    preferred_exam_types = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Comma separated exam types (UPSC, SSC, BANKING, etc.)"
    )

    # Profile Completion
    profile_completed = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def age(self):
        """Calculate and return user's current age"""
        if self.date_of_birth:
            return calculate_age(self.date_of_birth)
        return None

    def get_preferred_exam_types_list(self):
        """Return list of preferred exam types"""
        if self.preferred_exam_types:
            return [et.strip().upper() for et in self.preferred_exam_types.split(',')]
        return []

    def is_eligible_for_exam(self, exam):
        """
        Check if user is eligible for a given exam based on:
        - Age limit
        - Educational qualification
        """
        if not self.age:
            return False

        # Check age limit
        if not (exam.age_limit_min <= self.age <= exam.age_limit_max):
            return False

        # Check educational qualification
        # Map qualifications to levels for comparison
        qualification_levels = {
            '10TH': 1,
            '12TH': 2,
            'DIPLOMA': 2,
            'GRADUATE': 3,
            'POST_GRADUATE': 4,
            'PHD': 5,
            'OTHER': 0,
        }

        user_qual_level = qualification_levels.get(self.highest_qualification, 0)

        # Parse exam qualification and get minimum required level
        exam_qual = exam.educational_qualification.upper()

        # Simple matching - exam qualification contains user's qualification or higher
        # This is a basic implementation - can be enhanced
        if 'GRADUATE' in exam_qual or 'DEGREE' in exam_qual:
            required_level = 3
        elif '12TH' in exam_qual or 'INTERMEDIATE' in exam_qual:
            required_level = 2
        elif '10TH' in exam_qual or 'MATRIC' in exam_qual:
            required_level = 1
        else:
            required_level = 0

        return user_qual_level >= required_level
