"""
ProductivityMind - AI-Based Task Prioritization Engine

This module implements a rule-based "AI" system that calculates:
1. Smart Priority Score (0-100)
2. Risk Level prediction
3. Task deadline risk analysis
"""
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Count, Avg, Sum, F
from .models import Task


class TaskPrioritizationEngine:
    """
    AI-powered task prioritization engine using rule-based algorithms.
    Calculates a smart priority score based on multiple factors.
    """

    def __init__(self):
        # Weight factors for priority calculation (total = 100)
        self.weights = {
            'deadline_urgency': 40,      # How close is the deadline?
            'dependency_factor': 25,      # How many tasks are blocked by this?
            'complexity_weight': 15,      # Estimated hours/difficulty
            'priority_level': 10,         # Manual priority setting
            'age_factor': 10,             # How long has it been pending?
        }

        # Risk thresholds (in days)
        self.risk_thresholds = {
            'critical': 1,    # Due within 1 day
            'high': 2,        # Due within 2 days
            'medium': 5,      # Due within 5 days
            'low': 10,        # Due within 10 days
        }

    def calculate_smart_priority_score(self, task):
        """
        Calculate a smart priority score (0-100) for a task.

        Factors considered:
        1. Deadline Urgency (40%): Closer deadline = higher score
        2. Dependency Factor (25%): More blocking tasks = higher score
        3. Complexity Weight (15%): More hours = higher score
        4. Priority Level (10%): Manual priority contributes
        5. Age Factor (10%): Older pending tasks get higher score

        Returns:
            int: Smart priority score (0-100)
        """
        score = 0

        # 1. Deadline Urgency Score (0-40)
        deadline_score = self._calculate_deadline_urgency(task)
        score += deadline_score * (self.weights['deadline_urgency'] / 100)

        # 2. Dependency Factor Score (0-25)
        dependency_score = self._calculate_dependency_factor(task)
        score += dependency_score * (self.weights['dependency_factor'] / 100)

        # 3. Complexity Weight Score (0-15)
        complexity_score = self._calculate_complexity_weight(task)
        score += complexity_score * (self.weights['complexity_weight'] / 100)

        # 4. Priority Level Score (0-10)
        priority_score = self._calculate_priority_level_score(task)
        score += priority_score * (self.weights['priority_level'] / 100)

        # 5. Age Factor Score (0-10)
        age_score = self._calculate_age_factor(task)
        score += age_score * (self.weights['age_factor'] / 100)

        # Boost score if task is blocking others and can be started
        if task.can_start and task.blocking_count > 0:
            score += min(task.blocking_count * 2, 10)  # Max +10 boost

        # Penalty if task cannot start due to dependencies
        if not task.can_start:
            score -= 15

        # Ensure score is within bounds
        return max(0, min(100, int(score)))

    def _calculate_deadline_urgency(self, task):
        """
        Calculate deadline urgency score (0-40).
        Closer deadlines get higher scores.
        """
        if not task.due_date or task.status == 'done':
            return 0

        now = timezone.now()
        days_until_due = (task.due_date - now).days

        # Already overdue
        if days_until_due < 0:
            return 40

        # Due very soon (0-1 days)
        if days_until_due <= 1:
            return 40
        # Due soon (2-3 days)
        elif days_until_due <= 3:
            return 35
        # Due within a week (4-7 days)
        elif days_until_due <= 7:
            return 25
        # Due within two weeks (8-14 days)
        elif days_until_due <= 14:
            return 15
        # Due within a month (15-30 days)
        elif days_until_due <= 30:
            return 10
        # Due later
        else:
            return 5

    def _calculate_dependency_factor(self, task):
        """
        Calculate dependency factor score (0-25).
        More tasks blocked by this task = higher score.
        """
        blocking_count = task.blocking_count

        if blocking_count == 0:
            return 0
        elif blocking_count >= 5:
            return 25
        elif blocking_count >= 3:
            return 20
        elif blocking_count >= 2:
            return 15
        else:
            return 10

    def _calculate_complexity_weight(self, task):
        """
        Calculate complexity weight score (0-15).
        Based on estimated hours.
        """
        if not task.estimated_hours:
            return 5  # Default score for tasks without estimates

        hours = task.estimated_hours

        if hours >= 20:
            return 15
        elif hours >= 10:
            return 12
        elif hours >= 5:
            return 10
        elif hours >= 2:
            return 7
        else:
            return 5

    def _calculate_priority_level_score(self, task):
        """
        Calculate priority level score (0-10).
        Based on manual priority setting.
        """
        priority_scores = {
            'critical': 10,
            'high': 8,
            'medium': 5,
            'low': 2,
        }
        return priority_scores.get(task.priority, 5)

    def _calculate_age_factor(self, task):
        """
        Calculate age factor score (0-10).
        Older pending tasks get higher scores.
        """
        if task.status == 'done':
            return 0

        now = timezone.now()
        days_since_creation = (now - task.created_at).days

        if days_since_creation >= 30:
            return 10
        elif days_since_creation >= 14:
            return 7
        elif days_since_creation >= 7:
            return 5
        elif days_since_creation >= 3:
            return 3
        else:
            return 0

    def update_all_task_scores(self):
        """
        Recalculate and update smart priority scores for all tasks.
        """
        tasks = Task.objects.all()
        updated_count = 0

        for task in tasks:
            old_score = task.smart_priority_score
            new_score = self.calculate_smart_priority_score(task)

            if old_score != new_score:
                task.smart_priority_score = new_score
                task.save(update_fields=['smart_priority_score'])
                updated_count += 1

        return updated_count

    def get_prioritized_tasks(self, user=None, limit=None):
        """
        Get tasks sorted by smart priority score.

        Args:
            user: Filter by assignee (optional)
            limit: Maximum number of tasks to return (optional)

        Returns:
            QuerySet: Prioritized tasks
        """
        tasks = Task.objects.exclude(status='done').exclude(status='cancelled')

        if user:
            tasks = tasks.filter(assignee=user)

        # Sort by smart priority score (descending)
        tasks = tasks.order_by('-smart_priority_score', 'due_date')

        if limit:
            tasks = tasks[:limit]

        return tasks


class RiskPredictionEngine:
    """
    AI-powered risk prediction engine for task deadlines.
    Identifies tasks at risk of missing their deadlines.
    """

    def __init__(self):
        self.risk_thresholds = {
            'critical': 1,    # Due within 1 day
            'high': 2,        # Due within 2 days
            'medium': 5,      # Due within 5 days
            'low': 10,        # Due within 10 days
        }

    def assess_task_risk(self, task):
        """
        Assess the risk level for a task.

        Returns:
            str: Risk level ('none', 'low', 'medium', 'high', 'critical')
        """
        if task.status == 'done':
            return 'none'

        if not task.due_date:
            return 'none'

        now = timezone.now()
        days_until_due = (task.due_date - now).days

        # Already overdue
        if days_until_due < 0:
            return 'critical'

        # Risk based on proximity to deadline
        if days_until_due <= self.risk_thresholds['critical']:
            return 'critical'
        elif days_until_due <= self.risk_thresholds['high']:
            return 'high'
        elif days_until_due <= self.risk_thresholds['medium']:
            return 'medium'
        elif days_until_due <= self.risk_thresholds['low']:
            return 'low'
        else:
            return 'none'

    def update_all_task_risks(self):
        """
        Recalculate and update risk levels for all tasks.
        """
        tasks = Task.objects.exclude(status='done').exclude(status='cancelled')
        updated_count = 0

        for task in tasks:
            old_risk = task.risk_level
            old_at_risk = task.is_at_risk

            new_risk = self.assess_task_risk(task)
            new_at_risk = new_risk in ['high', 'critical']

            task.risk_level = new_risk
            task.is_at_risk = new_at_risk

            if old_risk != new_risk or old_at_risk != new_at_risk:
                task.save(update_fields=['risk_level', 'is_at_risk'])
                updated_count += 1

        return updated_count

    def get_at_risk_tasks(self, min_risk='high'):
        """
        Get all tasks at or above the specified risk level.

        Args:
            min_risk: Minimum risk level ('low', 'medium', 'high', 'critical')

        Returns:
            QuerySet: Tasks at risk
        """
        risk_hierarchy = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        min_level = risk_hierarchy.get(min_risk, 3)

        at_risk_tasks = []
        for risk_level, level in risk_hierarchy.items():
            if level >= min_level:
                at_risk_tasks.append(risk_level)

        return Task.objects.filter(
            risk_level__in=at_risk_tasks
        ).exclude(status='done').exclude(status='cancelled')

    def get_overdue_tasks(self):
        """
        Get all overdue tasks.
        """
        now = timezone.now()
        return Task.objects.filter(
            due_date__lt=now,
            status__in=['todo', 'in_progress']
        )

    def get_upcoming_deadlines(self, days=7):
        """
        Get tasks with deadlines within the specified number of days.
        """
        now = timezone.now()
        end_date = now + timedelta(days=days)

        return Task.objects.filter(
            due_date__gte=now,
            due_date__lte=end_date,
            status__in=['todo', 'in_progress']
        ).order_by('due_date')


class ProductivityAnalytics:
    """
    Analytics engine for productivity insights and reporting.
    """

    def get_task_completion_trend(self, days=30):
        """
        Get task completion trend over time.

        Returns:
            list: Daily completion counts
        """
        from django.db.models import Count
        from django.db.models.functions import TruncDate

        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        completed_tasks = Task.objects.filter(
            completed_at__gte=start_date,
            completed_at__lte=end_date,
            status='done'
        ).annotate(
            date=TruncDate('completed_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')

        return list(completed_tasks)

    def get_user_productivity_stats(self, user=None):
        """
        Get productivity statistics for users.

        Args:
            user: Specific user or None for all users

        Returns:
            dict: Productivity statistics
        """
        queryset = Task.objects.filter(status='done')

        if user:
            queryset = queryset.filter(assignee=user)

        stats = queryset.aggregate(
            total_completed=Count('id'),
            total_hours=Sum('actual_hours'),
            avg_completion_time=Avg('estimated_hours')
        )

        return stats

    def get_status_distribution(self, project=None):
        """
        Get task distribution by status.

        Args:
            project: Filter by project (optional)

        Returns:
            dict: Status counts
        """
        queryset = Task.objects.all()

        if project:
            queryset = queryset.filter(project=project)

        distribution = {}
        for status_code, status_label in Task.STATUS_CHOICES:
            count = queryset.filter(status=status_code).count()
            distribution[status_label] = count

        return distribution

    def get_bottleneck_tasks(self, limit=10):
        """
        Identify tasks that are blocking the most other tasks.

        Args:
            limit: Maximum number of tasks to return

        Returns:
            QuerySet: Bottleneck tasks
        """
        return Task.objects.annotate(
            blocking_tasks_count=Count('blocking')
        ).filter(
            blocking_tasks_count__gt=0,
            status__in=['todo', 'in_progress']
        ).order_by('-blocking_tasks_count')[:limit]

    def get_top_performers(self, limit=10, days=30):
        """
        Get top performers based on completed tasks.

        Args:
            limit: Maximum number of users
            days: Lookback period in days

        Returns:
            list: Top performers with stats
        """
        from django.contrib.auth.models import User
        from django.db.models import Value, DecimalField

        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        performers = User.objects.annotate(
            tasks_completed=Count(
                'assigned_tasks',
                filter=Q(
                    assigned_tasks__status='done',
                    assigned_tasks__completed_at__gte=start_date,
                    assigned_tasks__completed_at__lte=end_date
                )
            ),
            hours_logged=Sum(
                'work_logs__hours',
                filter=Q(work_logs__logged_at__gte=start_date),
                output_field=DecimalField()
            )
        ).filter(
            tasks_completed__gt=0
        ).order_by('-tasks_completed')[:limit]

        return performers


def run_ai_analysis():
    """
    Run complete AI analysis on all tasks.
    Updates priority scores and risk assessments.
    """
    priority_engine = TaskPrioritizationEngine()
    risk_engine = RiskPredictionEngine()

    priority_updates = priority_engine.update_all_task_scores()
    risk_updates = risk_engine.update_all_task_risks()

    return {
        'priority_updates': priority_updates,
        'risk_updates': risk_updates
    }
