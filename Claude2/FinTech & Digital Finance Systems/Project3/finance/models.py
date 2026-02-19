"""
Database models for the Finance Intelligence Platform.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Category(models.TextChoices):
    """Pre-defined expense and income categories."""
    FOOD = 'Food', 'Food & Dining'
    TRANSPORT = 'Transport', 'Transportation'
    UTILITIES = 'Utilities', 'Utilities & Bills'
    ENTERTAINMENT = 'Entertainment', 'Entertainment'
    HEALTH = 'Health', 'Health & Wellness'
    SALARY = 'Salary', 'Salary & Income'
    SHOPPING = 'Shopping', 'Shopping'
    EDUCATION = 'Education', 'Education'
    OTHER = 'Other', 'Other'


class Transaction(models.Model):
    """
    Model to track all financial transactions (income and expenses).
    """
    TRANSACTION_TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    date = models.DateField(default=timezone.now)
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPE_CHOICES,
        default='expense'
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER
    )
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'

    def __str__(self):
        return f"{self.transaction_type.title()}: {self.amount} - {self.description}"

    @property
    def is_income(self):
        return self.transaction_type == 'income'

    @property
    def is_expense(self):
        return self.transaction_type == 'expense'


class Budget(models.Model):
    """
    Model to set monthly budget limits per category.
    """
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        unique=True
    )
    limit_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(1)]
    )
    month = models.PositiveIntegerField(default=1)  # 1-12 for January-December
    year = models.PositiveIntegerField(default=2024)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['year', 'month', 'category']
        verbose_name = 'Budget'
        verbose_name_plural = 'Budgets'
        unique_together = ['category', 'month', 'year']

    def __str__(self):
        return f"{self.category}: ${self.limit_amount} ({self.month}/{self.year})"

    @property
    def month_name(self):
        """Return the month name."""
        import calendar
        return calendar.month_name[self.month]

    def get_spent_amount(self):
        """Calculate the total spent for this category in the given month/year."""
        from django.db.models import Sum
        return Transaction.objects.filter(
            category=self.category,
            transaction_type='expense',
            date__year=self.year,
            date__month=self.month
        ).aggregate(total=Sum('amount'))['total'] or 0

    @property
    def spent_amount(self):
        """Property accessor for spent amount."""
        return self.get_spent_amount()

    @property
    def remaining_amount(self):
        """Calculate remaining budget."""
        return self.limit_amount - self.spent_amount

    @property
    def utilization_percentage(self):
        """Calculate budget utilization percentage."""
        if self.limit_amount > 0:
            return (self.spent_amount / self.limit_amount) * 100
        return 0

    @property
    def is_over_budget(self):
        """Check if spending exceeds budget."""
        return self.spent_amount > self.limit_amount

    @property
    def status(self):
        """Return budget status."""
        if self.is_over_budget:
            return 'Over Budget'
        elif self.utilization_percentage > 80:
            return 'Near Limit'
        elif self.utilization_percentage > 50:
            return 'Moderate'
        else:
            return 'On Track'


class FinancialInsight(models.Model):
    """
    Model to store generated financial insights and recommendations.
    """
    INSIGHT_TYPES = [
        ('pattern', 'Spending Pattern'),
        ('alert', 'Budget Alert'),
        ('recommendation', 'Savings Recommendation'),
        ('forecast', 'Spending Forecast'),
    ]

    insight_type = models.CharField(max_length=20, choices=INSIGHT_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    data = models.JSONField(default=dict, blank=True)  # Store related data
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Financial Insight'
        verbose_name_plural = 'Financial Insights'

    def __str__(self):
        return f"{self.title} - {self.created_at.strftime('%Y-%m-%d')}"
