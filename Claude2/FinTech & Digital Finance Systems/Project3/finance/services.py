"""
Financial Analysis Services - AI-Driven Logic Engine

This module contains all the core logic for:
1. Category Classification
2. Expense Pattern Analysis
3. Budget Forecasting
4. Behavior Insights
5. Savings Optimization
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from .models import Transaction, Budget, FinancialInsight, Category


# ============================================================================
# MODULE 2: Spending Category Classification
# ============================================================================

class CategoryClassifier:
    """
    Automatic category classification based on transaction description.
    Uses keyword matching to suggest appropriate categories.
    """

    CATEGORY_KEYWORDS = {
        Category.FOOD: [
            'restaurant', 'pizza', 'burger', 'sushi', 'coffee', 'cafe', 'starbucks',
            'grocery', 'supermarket', 'walmart', 'target', 'food', 'dining',
            'lunch', 'dinner', 'breakfast', 'mcdonald', 'subway', 'doordash',
            'uber eats', 'grubhub', 'meal', 'snack'
        ],
        Category.TRANSPORT: [
            'uber', 'lyft', 'taxi', 'gas', 'shell', 'chevron', 'bp', 'exxon',
            'metro', 'bus', 'train', 'subway', 'parking', 'toll', 'car',
            'auto', 'transport', 'commute', 'flight', 'airline', 'uber',
            'lyft'
        ],
        Category.UTILITIES: [
            'electric', 'water', 'gas bill', 'internet', 'wifi', 'phone',
            'utility', 'bill', 'verizon', 'at&t', 'comcast', 'power',
            'heating', 'rent', 'insurance'
        ],
        Category.ENTERTAINMENT: [
            'netflix', 'spotify', 'hulu', 'disney', 'movie', 'cinema',
            'concert', 'game', 'playstation', 'xbox', 'steam', 'entertainment',
            'youtube premium', 'amazon prime', 'theater', 'sports'
        ],
        Category.HEALTH: [
            'pharmacy', 'doctor', 'hospital', 'medical', 'health', 'gym',
            'fitness', 'prescription', 'walgreens', 'cvs', 'dentist',
            'wellness', 'insurance'
        ],
        Category.SHOPPING: [
            'amazon', 'ebay', 'etsy', 'walmart', 'target', 'best buy',
            'clothing', 'shoes', 'apparel', 'mall', 'shopping', 'store',
            'retail'
        ],
        Category.EDUCATION: [
            'course', 'udemy', 'coursera', 'education', 'school', 'university',
            'college', 'tuition', 'book', 'learning', 'training'
        ],
    }

    @classmethod
    def suggest_category(cls, description):
        """
        Suggest a category based on the description text.

        Args:
            description (str): Transaction description

        Returns:
            str: Suggested category
        """
        if not description:
            return Category.OTHER

        description_lower = description.lower()

        # Check each category's keywords
        for category, keywords in cls.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category

        # If no match found, return OTHER
        return Category.OTHER

    @classmethod
    def get_category_suggestions(cls, description, top_n=3):
        """
        Get multiple category suggestions with confidence scores.

        Args:
            description (str): Transaction description
            top_n (int): Number of suggestions to return

        Returns:
            list: List of tuples (category, confidence_score)
        """
        if not description:
            return [(Category.OTHER, 100)]

        description_lower = description.lower()
        scores = {}

        # Calculate matches for each category
        for category, keywords in cls.CATEGORY_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in description_lower)
            if matches > 0:
                scores[category] = matches * 10  # Base score

        # Sort by score and return top N
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        if not sorted_scores:
            return [(Category.OTHER, 100)]

        return sorted_scores[:top_n]


# ============================================================================
# MODULE 3: AI-Based Expense Pattern Analysis
# ============================================================================

class ExpensePatternAnalyzer:
    """
    Analyze spending patterns using Pandas for data manipulation.
    """

    @staticmethod
    def get_transactions_dataframe():
        """
        Fetch all transactions as a Pandas DataFrame.

        Returns:
            pd.DataFrame: Transactions data
        """
        transactions = Transaction.objects.all().values(
            'id', 'amount', 'date', 'transaction_type', 'category', 'description'
        )
        df = pd.DataFrame(transactions)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df['day_of_week'] = df['date'].dt.day_name()
            df['month'] = df['date'].dt.month
            df['year'] = df['date'].dt.year
            df['week'] = df['date'].dt.isocalendar().week
        return df

    @classmethod
    def analyze_spending_by_day_of_week(cls):
        """
        Calculate average spending per day of the week.

        Returns:
            dict: Day of week -> average spending
        """
        df = cls.get_transactions_dataframe()
        if df.empty:
            return {}

        # Filter only expenses
        expenses = df[df['transaction_type'] == 'expense']

        # Group by day of week and calculate mean
        result = expenses.groupby('day_of_week')['amount'].mean().to_dict()

        # Order by day of week
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        ordered_result = {day: result.get(day, 0) for day in day_order}

        return ordered_result

    @classmethod
    def get_highest_spending_categories(cls, limit=5):
        """
        Identify highest spending categories.

        Args:
            limit (int): Number of top categories to return

        Returns:
            list: List of tuples (category, total_amount)
        """
        df = cls.get_transactions_dataframe()
        if df.empty:
            return []

        expenses = df[df['transaction_type'] == 'expense']
        result = expenses.groupby('category')['amount'].sum().sort_values(ascending=False)

        return [(cat, float(amount)) for cat, amount in result.head(limit).items()]

    @classmethod
    def detect_recurring_expenses(cls, min_occurrences=3):
        """
        Detect recurring expenses (subscriptions, regular bills).

        Args:
            min_occurrences (int): Minimum number of occurrences to consider recurring

        Returns:
            list: List of dicts with recurring expense details
        """
        df = cls.get_transactions_dataframe()
        if df.empty:
            return []

        expenses = df[df['transaction_type'] == 'expense']

        # Group by description and count occurrences
        recurring = expenses.groupby('description').agg({
            'amount': ['mean', 'count'],
            'category': 'first'
        }).round(2)

        recurring.columns = ['avg_amount', 'occurrences', 'category']
        recurring = recurring[recurring['occurrences'] >= min_occurrences]
        recurring = recurring.sort_values('occurrences', ascending=False)

        result = []
        for desc, row in recurring.iterrows():
            result.append({
                'description': desc,
                'category': row['category'],
                'avg_amount': float(row['avg_amount']),
                'occurrences': int(row['occurrences']),
                'estimated_monthly': float(row['avg_amount'] * 4)  # Rough estimate
            })

        return result

    @classmethod
    def get_spending_trend(cls, months=6):
        """
        Get spending trend over the last N months.

        Args:
            months (int): Number of months to analyze

        Returns:
            dict: Monthly spending data
        """
        df = cls.get_transactions_dataframe()
        if df.empty:
            return {}

        # Filter last N months
        cutoff_date = timezone.now().date() - timedelta(days=30 * months)
        df = df[df['date'] >= pd.Timestamp(cutoff_date)]

        expenses = df[df['transaction_type'] == 'expense']
        income = df[df['transaction_type'] == 'income']

        # Group by month
        expenses_by_month = expenses.groupby([expenses['date'].dt.year, expenses['date'].dt.month])['amount'].sum()
        income_by_month = income.groupby([income['date'].dt.year, income['date'].dt.month])['amount'].sum()

        result = {
            'months': [],
            'expenses': [],
            'income': []
        }

        for (year, month), expense_amount in expenses_by_month.items():
            month_name = datetime(year, month, 1).strftime('%b %Y')
            result['months'].append(month_name)
            result['expenses'].append(float(expense_amount))
            result['income'].append(float(income_by_month.get((year, month), 0)))

        return result


# ============================================================================
# MODULE 4: Budget Forecasting and Overspending Prediction
# ============================================================================

class BudgetForecaster:
    """
    Forecast future expenses and predict overspending.
    """

    @classmethod
    def get_monthly_spending_history(cls, months=3):
        """
        Get spending history for the last N months.

        Args:
            months (int): Number of months of history

        Returns:
            list: List of monthly totals
        """
        df = ExpensePatternAnalyzer.get_transactions_dataframe()
        if df.empty:
            return [0] * months

        cutoff_date = timezone.now().date() - timedelta(days=30 * months)
        df = df[df['date'] >= pd.Timestamp(cutoff_date)]

        expenses = df[df['transaction_type'] == 'expense']
        monthly_spending = expenses.groupby([expenses['date'].dt.year, expenses['date'].dt.month])['amount'].sum()

        return [float(amount) for amount in monthly_spending.values[-months:]]

    @classmethod
    def forecast_next_month_spending(cls, months_to_average=3):
        """
        Forecast next month's spending using simple moving average.

        Args:
            months_to_average (int): Number of months to average

        Returns:
            float: Forecasted spending
        """
        history = cls.get_monthly_spending_history(months_to_average)

        if not history:
            return 0

        # Simple moving average
        forecast = sum(history) / len(history)
        return round(forecast, 2)

    @classmethod
    def check_budget_projection(cls, budget):
        """
        Check if current spending pace will exceed budget.

        Args:
            budget (Budget): Budget instance to check

        Returns:
            dict: Projection details
        """
        from django.db.models import Sum
        from datetime import datetime
        import calendar

        # Get current month/year
        today = timezone.now().date()
        current_month = today.month
        current_year = today.year

        # Only check if budget is for current month
        if budget.month != current_month or budget.year != current_year:
            return {
                'is_current_month': False,
                'projected_spending': 0,
                'will_exceed': False,
                'days_remaining': 0
            }

        # Calculate days passed and remaining
        days_in_month = calendar.monthrange(current_year, current_month)[1]
        day_of_month = today.day
        days_passed = day_of_month
        days_remaining = days_in_month - day_of_month

        # Get spending so far
        spent = budget.get_spent_amount()

        if days_passed == 0:
            return {
                'is_current_month': True,
                'projected_spending': spent,
                'will_exceed': False,
                'days_remaining': days_remaining,
                'daily_average': 0
            }

        # Calculate daily average
        daily_average = spent / days_passed

        # Project total spending
        projected_spending = spent + (daily_average * days_remaining)

        return {
            'is_current_month': True,
            'spent': float(spent),
            'daily_average': float(daily_average),
            'projected_spending': float(projected_spending),
            'budget_limit': float(budget.limit_amount),
            'will_exceed': projected_spending > budget.limit_amount,
            'excess_amount': float(max(0, projected_spending - budget.limit_amount)),
            'days_remaining': days_remaining,
            'days_passed': days_passed
        }

    @classmethod
    def generate_budget_alerts(cls):
        """
        Generate alerts for budgets that are at risk.

        Returns:
            list: List of alert dicts
        """
        today = timezone.now().date()
        current_budgets = Budget.objects.filter(month=today.month, year=today.year)

        alerts = []

        for budget in current_budgets:
            projection = cls.check_budget_projection(budget)

            if not projection['is_current_month']:
                continue

            # Check if over budget
            if budget.is_over_budget:
                alerts.append({
                    'type': 'critical',
                    'category': budget.category,
                    'message': f'You have exceeded your {budget.category} budget by ${budget.spent_amount - budget.limit_amount:.2f}',
                    'data': {
                        'spent': float(budget.spent_amount),
                        'limit': float(budget.limit_amount),
                        'over_by': float(budget.spent_amount - budget.limit_amount)
                    }
                })

            # Check if projected to exceed
            elif projection['will_exceed']:
                alerts.append({
                    'type': 'warning',
                    'category': budget.category,
                    'message': f'At your current spending pace, you will exceed your {budget.category} budget by ${projection["excess_amount"]:.2f}',
                    'data': projection
                })

            # Check if near limit (>80%)
            elif budget.utilization_percentage > 80:
                alerts.append({
                    'type': 'caution',
                    'category': budget.category,
                    'message': f'You have used {budget.utilization_percentage:.1f}% of your {budget.category} budget',
                    'data': {
                        'spent': float(budget.spent_amount),
                        'limit': float(budget.limit_amount),
                        'utilization': float(budget.utilization_percentage)
                    }
                })

        return alerts


# ============================================================================
# MODULE 5: Financial Behavior Insight Generation
# ============================================================================

class InsightGenerator:
    """
    Generate dynamic text insights based on spending data.
    """

    @classmethod
    def generate_insights(cls):
        """
        Generate all available insights.

        Returns:
            list: List of insight dicts
        """
        insights = []

        # Add pattern insights
        insights.extend(cls._generate_pattern_insights())

        # Add budget alerts
        alerts = BudgetForecaster.generate_budget_alerts()
        for alert in alerts:
            insights.append({
                'type': 'alert',
                'severity': alert['type'],
                'title': f'{alert["type"].title()}: {alert["category"]}',
                'description': alert['message'],
                'data': alert['data']
            })

        # Add recommendation insights
        insights.extend(cls._generate_recommendation_insights())

        # Save insights to database
        for insight in insights:
            FinancialInsight.objects.get_or_create(
                title=insight['title'],
                insight_type=insight.get('type', 'pattern'),
                defaults={
                    'description': insight['description'],
                    'data': insight.get('data', {})
                }
            )

        return insights

    @classmethod
    def _generate_pattern_insights(cls):
        """
        Generate insights based on spending patterns.

        Returns:
            list: List of pattern insights
        """
        insights = []
        df = ExpensePatternAnalyzer.get_transactions_dataframe()

        if df.empty:
            return insights

        expenses = df[df['transaction_type'] == 'expense']

        # Compare this week to average
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        this_week = expenses[expenses['date'] >= pd.Timestamp(week_ago)]

        if not this_week.empty:
            this_week_total = this_week['amount'].sum()
            this_week_by_category = this_week.groupby('category')['amount'].sum()

            # Get historical average for comparison
            historical_avg = expenses['amount'].mean() * 7  # Rough weekly average

            if this_week_total > historical_avg * 1.2:
                insights.append({
                    'type': 'pattern',
                    'title': 'High Spending This Week',
                    'description': f'You spent ${this_week_total:.2f} this week, which is {((this_week_total / historical_avg - 1) * 100):.0f}% above your average.',
                    'data': {
                        'this_week': float(this_week_total),
                        'average': float(historical_avg)
                    }
                })

            # Top category this week
            if not this_week_by_category.empty:
                top_category = this_week_by_category.idxmax()
                top_amount = this_week_by_category.max()

                insights.append({
                    'type': 'pattern',
                    'title': f'Top Spending: {top_category}',
                    'description': f'Your highest spending category this week was {top_category} at ${top_amount:.2f}.',
                    'data': {
                        'category': top_category,
                        'amount': float(top_amount)
                    }
                })

        return insights

    @classmethod
    def _generate_recommendation_insights(cls):
        """
        Generate recommendation insights.

        Returns:
            list: List of recommendation insights
        """
        insights = []

        # Get highest spending category
        top_categories = ExpensePatternAnalyzer.get_highest_spending_categories(limit=3)

        if top_categories:
            category, amount = top_categories[0]

            # Suggest reduction if it's a non-essential category
            non_essential = [Category.ENTERTAINMENT, Category.SHOPPING, Category.FOOD]

            if category in non_essential:
                suggested_reduction = min(amount * 0.2, 50)  # Suggest 20% reduction or $50

                insights.append({
                    'type': 'recommendation',
                    'title': f'Optimize {category} Spending',
                    'description': f'If you reduce your {category} spending by ${suggested_reduction:.2f}, you could save ${suggested_reduction * 12:.2f} annually.',
                    'data': {
                        'category': category,
                        'current_spending': float(amount),
                        'suggested_reduction': float(suggested_reduction),
                        'annual_savings': float(suggested_reduction * 12)
                    }
                })

        # Check for recurring expenses
        recurring = ExpensePatternAnalyzer.detect_recurring_expenses()

        if recurring:
            total_recurring = sum(r['estimated_monthly'] for r in recurring)

            insights.append({
                'type': 'recommendation',
                'title': 'Review Recurring Expenses',
                'description': f'You have {len(recurring)} recurring expenses totaling approximately ${total_recurring:.2f}/month. Review for any services you no longer use.',
                'data': {
                    'count': len(recurring),
                    'total_monthly': float(total_recurring),
                    'expenses': recurring[:5]  # Top 5
                }
            })

        return insights


# ============================================================================
# MODULE 6: Savings and Optimization Recommendation Engine
# ============================================================================

class SavingsOptimizer:
    """
    Identify unnecessary spending and suggest optimizations.
    """

    NON_ESSENTIAL_CATEGORIES = [
        Category.ENTERTAINMENT,
        Category.SHOPPING,
        Category.FOOD
    ]

    @classmethod
    def identify_optimization_opportunities(cls):
        """
        Identify opportunities to save money.

        Returns:
            list: List of optimization suggestions
        """
        df = ExpensePatternAnalyzer.get_transactions_dataframe()

        if df.empty:
            return []

        opportunities = []
        expenses = df[df['transaction_type'] == 'expense']

        # Analyze non-essential categories
        for category in cls.NON_ESSENTIAL_CATEGORIES:
            category_spending = expenses[expenses['category'] == category]

            if category_spending.empty:
                continue

            total = category_spending['amount'].sum()
            avg_monthly = total / max(1, (expenses['date'].max().month - expenses['date'].min().month + 1))

            # Suggest 10-20% reduction
            suggested_reduction = avg_monthly * 0.15

            if suggested_reduction > 10:  # Only if savings > $10
                opportunities.append({
                    'category': category,
                    'current_monthly_avg': float(avg_monthly),
                    'suggested_reduction': float(suggested_reduction),
                    'potential_annual_savings': float(suggested_reduction * 12),
                    'suggestion': f'Reduce {category} spending by 15%'
                })

        # Check for duplicate-like transactions
        opportunities.extend(cls._check_duplicate_transactions(expenses))

        return opportunities

    @classmethod
    def _check_duplicate_transactions(cls, expenses):
        """
        Check for potential duplicate transactions.

        Returns:
            list: List of duplicate alerts
        """
        duplicates = []

        # Group by amount and date
        grouped = expenses.groupby(['amount', expenses['date'].dt.date]).size()
        potential_dupes = grouped[grouped > 1]

        for (amount, date), count in potential_dupes.items():
            duplicates.append({
                'category': 'duplicate_check',
                'current_monthly_avg': 0,
                'suggested_reduction': float(amount),
                'potential_annual_savings': float(amount * 12),
                'suggestion': f'Review {count} transactions of ${amount:.2f} on {date} - possible duplicates'
            })

        return duplicates

    @classmethod
    def generate_savings_report(cls):
        """
        Generate a comprehensive savings report.

        Returns:
            dict: Savings report data
        """
        opportunities = cls.identify_optimization_opportunities()

        total_potential_monthly = sum(op['suggested_reduction'] for op in opportunities)
        total_potential_annual = sum(op['potential_annual_savings'] for op in opportunities)

        return {
            'opportunities': opportunities,
            'total_monthly_savings': float(total_potential_monthly),
            'total_annual_savings': float(total_potential_annual),
            'opportunity_count': len(opportunities)
        }


# ============================================================================
# MODULE 8: Monthly Financial Summary
# ============================================================================

class MonthlyReportGenerator:
    """
    Generate monthly financial summaries and reports.
    """

    @classmethod
    def generate_monthly_report(cls, year, month):
        """
        Generate a comprehensive monthly report.

        Args:
            year (int): Year
            month (int): Month (1-12)

        Returns:
            dict: Monthly report data
        """
        # Get transactions for the month
        transactions = Transaction.objects.filter(date__year=year, date__month=month)

        # Calculate totals
        total_income = transactions.filter(transaction_type='income').aggregate(
            total=Sum('amount')
        )['total'] or 0

        total_expense = transactions.filter(transaction_type='expense').aggregate(
            total=Sum('amount')
        )['total'] or 0

        net_savings = total_income - total_expense

        # Get top expense categories
        df = ExpensePatternAnalyzer.get_transactions_dataframe()
        if not df.empty:
            month_df = df[
                (df['date'].dt.year == year) &
                (df['date'].dt.month == month) &
                (df['transaction_type'] == 'expense')
            ]

            if not month_df.empty:
                top_categories = month_df.groupby('category')['amount'].sum().sort_values(ascending=False).head(3)
                top_expenses = [(cat, float(amount)) for cat, amount in top_categories.items()]
            else:
                top_expenses = []
        else:
            top_expenses = []

        # Get all transactions for the period
        all_transactions = list(transactions.values(
            'date', 'description', 'amount', 'transaction_type', 'category'
        ))

        # Get budget performance
        budgets = Budget.objects.filter(year=year, month=month)
        budget_performance = []
        for budget in budgets:
            budget_performance.append({
                'category': budget.category,
                'budget': float(budget.limit_amount),
                'spent': float(budget.spent_amount),
                'remaining': float(budget.remaining_amount),
                'status': budget.status,
                'utilization': float(budget.utilization_percentage)
            })

        return {
            'year': year,
            'month': month,
            'month_name': datetime(year, month, 1).strftime('%B %Y'),
            'total_income': float(total_income),
            'total_expense': float(total_expense),
            'net_savings': float(net_savings),
            'savings_rate': float((net_savings / total_income * 100) if total_income > 0 else 0),
            'top_expense_categories': top_expenses,
            'transaction_count': transactions.count(),
            'transactions': all_transactions,
            'budget_performance': budget_performance,
            'income_count': transactions.filter(transaction_type='income').count(),
            'expense_count': transactions.filter(transaction_type='expense').count()
        }


# ============================================================================
# API Data Preparation Functions
# ============================================================================

def get_dashboard_data():
    """
    Prepare all data needed for the dashboard.

    Returns:
        dict: Dashboard data
    """
    # Generate insights
    insights = InsightGenerator.generate_insights()

    # Get spending by category
    df = ExpensePatternAnalyzer.get_transactions_dataframe()
    if not df.empty:
        expenses = df[df['transaction_type'] == 'expense']
        category_breakdown = expenses.groupby('category')['amount'].sum().to_dict()
        category_breakdown = {k: float(v) for k, v in category_breakdown.items()}
    else:
        category_breakdown = {}

    # Get spending trend
    spending_trend = ExpensePatternAnalyzer.get_spending_trend(months=6)

    # Get budget vs actual
    today = timezone.now().date()
    budgets = Budget.objects.filter(month=today.month, year=today.year)
    budget_vs_actual = []
    for budget in budgets:
        budget_vs_actual.append({
            'category': budget.category,
            'budget': float(budget.limit_amount),
            'actual': float(budget.spent_amount)
        })

    # Get savings opportunities
    savings_report = SavingsOptimizer.generate_savings_report()

    return {
        'insights': insights[:10],  # Top 10 insights
        'category_breakdown': category_breakdown,
        'spending_trend': spending_trend,
        'budget_vs_actual': budget_vs_actual,
        'savings_opportunities': savings_report['opportunities'][:5],
        'total_potential_savings': savings_report['total_monthly_savings']
    }
