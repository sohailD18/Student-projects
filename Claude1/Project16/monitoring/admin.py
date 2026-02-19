from django.contrib import admin
from .models import (
    Student, Exam, Question, Choice,
    ProctorLog, ExamSession, ExamResult
)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'student_id', 'exam_count', 'result_count')
    search_fields = ('name', 'student_id')
    list_per_page = 25
    ordering = ('name',)

    def exam_count(self, obj):
        return obj.exam_results.count()
    exam_count.short_description = 'Exams Taken'

    def result_count(self, obj):
        passed = obj.exam_results.filter(status='pass').count()
        total = obj.exam_results.count()
        return f'{passed}/{total}'
    result_count.short_description = 'Pass/Total'


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
    fields = ('choice_text', 'is_correct', 'order')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'exam', 'order', 'choice_count')
    list_filter = ('exam',)
    search_fields = ('question_text', 'exam__subject')
    list_per_page = 25
    inlines = [ChoiceInline]
    ordering = ('exam', 'order')

    def choice_count(self, obj):
        return obj.choices.count()
    choice_count.short_description = 'Choices'


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('subject', 'duration', 'passing_score', 'question_count', 'created_at')
    list_filter = ('created_at', 'duration', 'passing_score')
    search_fields = ('subject', 'instructions')
    list_per_page = 25
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('subject', 'duration', 'passing_score')
        }),
        ('Additional Details', {
            'fields': ('instructions', 'created_by', 'created_at')
        }),
    )


@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'start_time', 'end_time', 'duration', 'status', 'violation_count')
    list_filter = ('status', 'start_time', 'exam')
    search_fields = ('student__name', 'student__student_id', 'exam__subject')
    list_per_page = 25
    readonly_fields = ('start_time', 'ip_address', 'browser_info')
    ordering = ('-start_time',)

    def duration(self, obj):
        if obj.duration_minutes():
            return f'{obj.duration_minutes()} min'
        return 'In Progress'
    duration.short_description = 'Duration'

    fieldsets = (
        ('Session Information', {
            'fields': ('student', 'exam', 'status')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time')
        }),
        ('Monitoring Data', {
            'fields': ('ip_address', 'browser_info', 'violation_count', 'screenshot_captured')
        }),
    )


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'score_badge', 'status_badge', 'integrity_badge', 'created_at')
    list_filter = ('status', 'created_at', 'exam')
    search_fields = ('student__name', 'student__student_id', 'exam__subject')
    list_per_page = 25
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    def score_badge(self, obj):
        color = 'green' if obj.score >= 70 else 'orange' if obj.score >= 50 else 'red'
        return f'<span style="color: {color}; font-weight: bold;">{obj.score}%</span>'
    score_badge.short_description = 'Score'
    score_badge.allow_tags = True

    def status_badge(self, obj):
        color = 'green' if obj.status == 'pass' else 'red'
        return f'<span style="color: {color}; font-weight: bold;">{obj.get_status_display()}</span>'
    status_badge.short_description = 'Status'
    status_badge.allow_tags = True

    def integrity_badge(self, obj):
        color = 'green' if obj.integrity_score >= 80 else 'orange' if obj.integrity_score >= 50 else 'red'
        return f'<span style="color: {color}; font-weight: bold;">{obj.integrity_score}%</span>'
    integrity_badge.short_description = 'Integrity'
    integrity_badge.allow_tags = True

    fieldsets = (
        ('Result Information', {
            'fields': ('student', 'exam', 'status')
        }),
        ('Performance', {
            'fields': ('score', 'total_questions', 'correct_answers')
        }),
        ('Integrity Metrics', {
            'fields': ('integrity_score', 'risk_score')
        }),
        ('Additional Data', {
            'fields': ('answers', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProctorLog)
class ProctorLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'student', 'exam', 'violation_type_badge', 'severity_badge', 'notes_preview')
    list_filter = ('violation_type', 'timestamp', 'exam')
    search_fields = ('student__name', 'student__student_id', 'exam__subject', 'notes')
    list_per_page = 50
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)

    def violation_type_badge(self, obj):
        colors = {
            'tab_switch': 'blue',
            'copy_paste': 'orange',
            'no_face': 'red',
            'multiple_faces': 'darkred',
            'phone_detected': 'purple',
            'suspicious_object': 'brown',
            'no_movement': 'gray',
            'other': 'black',
        }
        color = colors.get(obj.violation_type, 'black')
        return f'<span style="background-color: {color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">{obj.get_violation_type_display()}</span>'
    violation_type_badge.short_description = 'Violation'
    violation_type_badge.allow_tags = True

    def severity_badge(self, obj):
        points = obj.severity_points()
        color = 'green' if points <= 5 else 'orange' if points <= 15 else 'red'
        level = 'Low' if points <= 5 else 'Medium' if points <= 15 else 'High'
        return f'<span style="color: {color}; font-weight: bold;">{level} ({points} pts)</span>'
    severity_badge.short_description = 'Severity'
    severity_badge.allow_tags = True

    def notes_preview(self, obj):
        if obj.notes:
            return obj.notes[:50] + '...' if len(obj.notes) > 50 else obj.notes
        return '-'
    notes_preview.short_description = 'Notes'

    def has_add_permission(self, request):
        # Logs are created automatically by the monitoring system
        return False

    def has_change_permission(self, request, obj=None):
        # Logs should not be modified once created
        return False

    fieldsets = (
        ('Violation Information', {
            'fields': ('student', 'exam', 'violation_type')
        }),
        ('Details', {
            'fields': ('timestamp', 'notes')
        }),
    )
