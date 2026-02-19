"""
Django Models for FinRisk AI
Module 1: Financial Behavior Data Collection
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class UserProfile(models.Model):
    """
    UserProfile Model - Stores user demographic and financial information
    Module 1: Financial Behavior Data Collection
    """
    EMPLOYMENT_STATUS_CHOICES = [
        ('employed', 'Employed'),
        ('self_employed', 'Self-Employed'),
        ('unemployed', 'Unemployed'),
        ('retired', 'Retired'),
        ('student', 'Student'),
    ]

    INCOME_STABILITY_CHOICES = [
        ('very_stable', 'Very Stable - Government/Large Corporate'),
        ('stable', 'Stable - Regular Employment'),
        ('somewhat_stable', 'Somewhat Stable - Commission Based'),
        ('unstable', 'Unstable - Freelance/Gig Economy'),
    ]

    # Personal Information
    name = models.CharField(max_length=200, default='User')
    age = models.IntegerField(validators=[MinValueValidator(18)], help_text="Age in years (minimum 18)")

    # Financial Information
    annual_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Annual income in USD"
    )

    employment_status = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_STATUS_CHOICES,
        default='employed'
    )

    income_stability = models.CharField(
        max_length=20,
        choices=INCOME_STABILITY_CHOICES,
        default='stable'
    )

    dependents = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of financial dependents"
    )

    # Investment Experience
    investment_experience_years = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Years of investment experience"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - Age: {self.age}, Income: ${self.annual_income:,.2f}"

    @property
    def monthly_income(self):
        """Calculate monthly income"""
        return self.annual_income / Decimal('12')


class Transaction(models.Model):
    """
    Transaction Model - Stores individual financial transactions
    Module 1: Financial Behavior Data Collection
    """
    TRANSACTION_TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    CATEGORY_CHOICES = [
        # Income Categories
        ('salary', 'Salary'),
        ('freelance', 'Freelance Income'),
        ('investment', 'Investment Returns'),
        ('business', 'Business Income'),
        ('other_income', 'Other Income'),
        # Expense Categories - Essential
        ('housing', 'Housing - Rent/Mortgage'),
        ('food', 'Food & Groceries'),
        ('utilities', 'Utilities - Electricity, Water, Gas'),
        ('healthcare', 'Healthcare & Insurance'),
        ('transportation', 'Transportation'),
        ('education', 'Education'),
        # Expense Categories - Discretionary
        ('dining', 'Dining Out'),
        ('entertainment', 'Entertainment'),
        ('shopping', 'Shopping'),
        ('travel', 'Travel'),
        ('subscriptions', 'Subscriptions'),
        # Other
        ('other_expense', 'Other Expense'),
    ]

    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='transactions'
    )

    date = models.DateField(help_text="Transaction date")

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )

    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPE_CHOICES
    )

    description = models.TextField(blank=True, help_text="Optional transaction description")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'

    def __str__(self):
        return f"{self.transaction_type.title()}: ${self.amount:,.2f} - {self.get_category_display()} ({self.date})"

    @property
    def is_essential_expense(self):
        """Determine if this is an essential expense"""
        essential_categories = [
            'housing', 'food', 'utilities', 'healthcare',
            'transportation', 'education'
        ]
        return self.transaction_type == 'expense' and self.category in essential_categories

    @property
    def is_discretionary_expense(self):
        """Determine if this is a discretionary expense"""
        discretionary_categories = [
            'dining', 'entertainment', 'shopping', 'travel', 'subscriptions'
        ]
        return self.transaction_type == 'expense' and self.category in discretionary_categories


class RiskProfile(models.Model):
    """
    RiskProfile Model - Stores calculated risk profiles for users
    Module 3 & 4: AI-Based Risk Profiling Engine and Classification System
    """
    RISK_CLASSIFICATION_CHOICES = [
        ('conservative', 'Conservative - Low Risk'),
        ('moderate', 'Moderate - Balanced Risk'),
        ('aggressive', 'Aggressive - High Risk'),
    ]

    user_profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='risk_profile'
    )

    # Risk Score (0-100)
    risk_score = models.IntegerField(
        help_text="Risk tolerance score from 0 (very conservative) to 100 (very aggressive)"
    )

    # Classification
    classification = models.CharField(
        max_length=20,
        choices=RISK_CLASSIFICATION_CHOICES
    )

    # Component Scores (for transparency)
    age_factor_score = models.IntegerField(help_text="Score based on age (0-100)")
    savings_rate_score = models.IntegerField(help_text="Score based on savings rate (0-100)")
    income_stability_score = models.IntegerField(help_text="Score based on income stability (0-100)")
    experience_score = models.IntegerField(help_text="Score based on investment experience (0-100)")

    # Analysis Data
    savings_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Savings rate as percentage"
    )

    total_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    essential_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discretionary_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    spending_pattern = models.CharField(
        max_length=50,
        help_text="Categorized spending pattern"
    )

    # Generated Insights
    insights = models.TextField(help_text="AI-generated financial insights")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Risk Profile'
        verbose_name_plural = 'Risk Profiles'

    def __str__(self):
        return f"{self.user_profile.name} - {self.get_classification_display()} (Score: {self.risk_score})"
