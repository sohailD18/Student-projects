"""
Database models for Employee Performance Analysis System
"""
from django.db import models
from django.utils import timezone


class Employee(models.Model):
    """
    Employee model representing basic employee information
    """
    PERFORMANCE_CATEGORIES = [
        ('high_potential', 'High Potential'),
        ('needs_training', 'Needs Training'),
        ('stable', 'Stable'),
        ('promotion_candidate', 'Promotion Candidate'),
    ]

    name = models.CharField(max_length=200, verbose_name="Employee Name")
    department = models.CharField(max_length=100, verbose_name="Department")
    role = models.CharField(max_length=100, verbose_name="Role/Position")
    join_date = models.DateField(verbose_name="Join Date")
    email = models.EmailField(max_length=254, blank=True, null=True, verbose_name="Email")
    performance_category = models.CharField(
        max_length=50,
        choices=PERFORMANCE_CATEGORIES,
        default='stable',
        verbose_name="Performance Category"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Employee"
        verbose_name_plural = "Employees"

    def __str__(self):
        return f"{self.name} - {self.role}"

    def get_average_efficiency(self):
        """Calculate average efficiency score across all records"""
        records = self.performancerecord_set.all()
        if records.exists():
            return round(records.aggregate(models.Avg('efficiency'))['efficiency__avg'], 2)
        return 0.0

    def get_average_quality(self):
        """Calculate average quality score across all records"""
        records = self.performancerecord_set.all()
        if records.exists():
            return round(records.aggregate(models.Avg('quality'))['quality__avg'], 2)
        return 0.0

    def get_total_tasks_completed(self):
        """Calculate total tasks completed across all records"""
        records = self.performancerecord_set.all()
        if records.exists():
            return records.aggregate(models.Sum('tasks_completed'))['tasks_completed__sum'] or 0
        return 0

    def get_total_hours_worked(self):
        """Calculate total hours worked across all records"""
        records = self.performancerecord_set.all()
        if records.exists():
            return round(records.aggregate(models.Sum('hours_worked'))['hours_worked__sum'], 2)
        return 0.0

    def get_record_count(self):
        """Get the number of performance records for this employee"""
        return self.performancerecord_set.count()


class PerformanceRecord(models.Model):
    """
    Performance record model tracking employee metrics
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='performancerecord_set',
        verbose_name="Employee"
    )
    date = models.DateField(verbose_name="Record Date", default=timezone.now)
    tasks_completed = models.IntegerField(verbose_name="Tasks Completed", default=0)
    efficiency = models.FloatField(
        verbose_name="Efficiency Score (1-10)",
        help_text="Rate efficiency from 1 (poor) to 10 (excellent)",
        default=5.0
    )
    quality = models.FloatField(
        verbose_name="Quality Rating (1-10)",
        help_text="Rate quality from 1 (poor) to 10 (excellent)",
        default=5.0
    )
    hours_worked = models.FloatField(verbose_name="Hours Worked", default=8.0)
    manager_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Manager Notes",
        help_text="Additional comments or observations"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = "Performance Record"
        verbose_name_plural = "Performance Records"
        indexes = [
            models.Index(fields=['employee', 'date']),
        ]

    def __str__(self):
        return f"{self.employee.name} - {self.date} (Eff: {self.efficiency}, Qual: {self.quality})"

    def get_overall_score(self):
        """Calculate overall performance score (average of efficiency and quality)"""
        return round((self.efficiency + self.quality) / 2, 2)

    def get_productivity_score(self):
        """Calculate productivity score (tasks per hour)"""
        if self.hours_worked > 0:
            return round(self.tasks_completed / self.hours_worked, 2)
        return 0.0
