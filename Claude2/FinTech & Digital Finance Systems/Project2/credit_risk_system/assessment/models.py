"""
Models for Credit Risk Assessment System
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Applicant(models.Model):
    """
    Applicant Financial Profile Model
    Stores personal and financial information of loan applicants
    """
    EMPLOYMENT_STATUS_CHOICES = [
        ('employed', 'Employed'),
        ('self_employed', 'Self-Employed'),
        ('unemployed', 'Unemployed'),
        ('retired', 'Retired'),
        ('student', 'Student'),
    ]

    # Primary identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Full Name")
    email = models.EmailField(verbose_name="Email Address")
    phone = models.CharField(max_length=20, verbose_name="Phone Number")

    # Financial Information
    annual_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Annual Income ($)"
    )
    employment_status = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_STATUS_CHOICES,
        verbose_name="Employment Status"
    )
    years_employed = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        verbose_name="Years Employed"
    )
    debt_to_income_ratio = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Debt-to-Income Ratio (%)"
    )

    # Assessment Results (computed fields)
    risk_probability = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name="Risk Probability (0-1)"
    )
    risk_category = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low Risk'),
            ('medium', 'Medium Risk'),
            ('high', 'High Risk'),
        ],
        null=True,
        blank=True,
        verbose_name="Risk Category"
    )
    eligibility_status = models.CharField(
        max_length=20,
        choices=[
            ('approved', 'Approved'),
            ('manual_review', 'Manual Review'),
            ('rejected', 'Rejected'),
        ],
        null=True,
        blank=True,
        verbose_name="Eligibility Status"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Updated")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Applicant"
        verbose_name_plural = "Applicants"

    def __str__(self):
        return f"{self.name} - {self.eligibility_status or 'Pending'}"

    @property
    def approved(self):
        """Check if applicant is approved"""
        return self.eligibility_status == 'approved'


class FinancialData(models.Model):
    """
    Credit History & Income Data Model
    One-to-One relationship with Applicant
    """
    HOME_OWNERSHIP_CHOICES = [
        ('rent', 'Rent'),
        ('mortgage', 'Mortgage'),
        ('own', 'Own Outright'),
        ('other', 'Other'),
    ]

    # One-to-One relationship with Applicant
    applicant = models.OneToOneField(
        Applicant,
        on_delete=models.CASCADE,
        related_name='financial_data',
        verbose_name="Applicant"
    )

    # Credit Information
    credit_score = models.IntegerField(
        validators=[MinValueValidator(300), MaxValueValidator(850)],
        verbose_name="Credit Score (300-850)"
    )
    num_open_loans = models.IntegerField(
        validators=[MinValueValidator(0)],
        default=0,
        verbose_name="Number of Open Loans"
    )
    num_credit_lines = models.IntegerField(
        validators=[MinValueValidator(0)],
        default=0,
        verbose_name="Number of Credit Lines"
    )
    late_payments = models.IntegerField(
        validators=[MinValueValidator(0)],
        default=0,
        verbose_name="Late Payments (Last 2 Years)"
    )
    bankruptcies = models.BooleanField(
        default=False,
        verbose_name="History of Bankruptcy"
    )
    home_ownership_status = models.CharField(
        max_length=20,
        choices=HOME_OWNERSHIP_CHOICES,
        verbose_name="Home Ownership Status"
    )

    # Additional Credit Metrics
    total_credit_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Total Credit Limit ($)"
    )
    credit_utilization = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Credit Utilization (%)"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Updated")

    class Meta:
        verbose_name = "Financial Data"
        verbose_name_plural = "Financial Data Records"

    def __str__(self):
        return f"Financial Data for {self.applicant.name}"

    @property
    def is_high_risk_credit(self):
        """Determine if credit profile indicates high risk"""
        return (
            self.credit_score < 600 or
            self.late_payments > 3 or
            self.bankruptcies or
            (self.credit_utilization and self.credit_utilization > 80)
        )
