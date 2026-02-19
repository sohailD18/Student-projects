"""
Admin Configuration for Examination App
"""
from django.contrib import admin
from .models import (
    User, Subject, Topic, Exam, Question,
    StudentAnswer, ExamResult, PerformanceAnalysis, ExamProgress
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin interface for User model"""
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """Admin interface for Subject model"""
    list_display = ['name', 'code', 'created_at']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    """Admin interface for Topic model"""
    list_display = ['name', 'subject', 'chapter_number', 'created_at']
    list_filter = ['subject', 'created_at']
    search_fields = ['name', 'subject__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    """Admin interface for Exam model"""
    list_display = ['title', 'subject', 'total_marks', 'duration_minutes', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'subject', 'created_at']
    search_fields = ['title', 'subject__name', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin interface for Question model"""
    list_display = ['__str__', 'exam', 'topic', 'question_type', 'marks', 'question_number']
    list_filter = ['question_type', 'exam__subject', 'topic']
    search_fields = ['text', 'exam__title']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    """Admin interface for StudentAnswer model"""
    list_display = ['student', 'question', 'selected_answer', 'is_correct', 'marks_obtained', 'answered_at']
    list_filter = ['is_correct', 'answered_at', 'question__exam__subject']
    search_fields = ['student__username', 'question__text']
    readonly_fields = ['answered_at']


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    """Admin interface for ExamResult model"""
    list_display = ['student', 'exam', 'score', 'percentage', 'status', 'completed_at']
    list_filter = ['status', 'completed_at', 'exam__subject']
    search_fields = ['student__username', 'exam__title']
    readonly_fields = ['completed_at']


@admin.register(PerformanceAnalysis)
class PerformanceAnalysisAdmin(admin.ModelAdmin):
    """Admin interface for PerformanceAnalysis model"""
    list_display = ['student', 'subject', 'overall_accuracy', 'total_attempts', 'last_updated']
    list_filter = ['subject', 'last_updated', 'created_at']
    search_fields = ['student__username', 'subject__name']
    readonly_fields = ['created_at', 'last_updated']

    def weak_topics_display(self, obj):
        """Display weak topics in list view"""
        return ', '.join(obj.weak_topics.keys())
    weak_topics_display.short_description = 'Weak Topics'


@admin.register(ExamProgress)
class ExamProgressAdmin(admin.ModelAdmin):
    """Admin interface for ExamProgress model"""
    list_display = ['student', 'exam', 'current_question', 'is_completed', 'started_at', 'last_activity']
    list_filter = ['is_completed', 'started_at']
    search_fields = ['student__username', 'exam__title']
    readonly_fields = ['started_at', 'last_activity']
