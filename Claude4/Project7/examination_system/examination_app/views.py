"""
Views for AI-Based Intelligent Examination Performance Analysis System
Includes all logic: Authentication, CRUD, Exam taking, and AI Analysis Algorithm
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Q, Sum, F
from django.db import IntegrityError
from django.utils import timezone
from django.http import JsonResponse, HttpResponseBadRequest
from datetime import datetime, timedelta
import json

from .models import (
    User, Subject, Topic, Exam, Question,
    StudentAnswer, ExamResult, PerformanceAnalysis, ExamProgress
)
from .forms import (
    CustomUserCreationForm, LoginForm, SubjectForm, TopicForm,
    ExamForm, QuestionForm, TakeExamForm
)


# ============================
# AUTHENTICATION VIEWS
# ============================

def user_register(request):
    """
    User Registration View
    Allows both Students and Teachers to register
    """
    if request.user.is_authenticated:
        return redirect('examination_app:dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now login.')
            return redirect('examination_app:login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'examination_app/register.html', {'form': form})


def user_login(request):
    """
    User Login View
    Authenticates and logs in users
    """
    if request.user.is_authenticated:
        return redirect('examination_app:dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect('examination_app:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'examination_app/login.html', {'form': form})


def user_logout(request):
    """
    User Logout View
    """
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('examination_app:login')


# ============================
# DASHBOARD VIEWS
# ============================

@login_required
def dashboard(request):
    """
    Main Dashboard View
    Redirects to appropriate dashboard based on user role
    """
    if request.user.is_teacher:
        return teacher_dashboard(request)
    elif request.user.is_student:
        return student_dashboard(request)
    else:
        return redirect('examination_app:login')


@login_required
def teacher_dashboard(request):
    """
    Teacher Dashboard
    Shows created exams, allows exam creation, view student results
    """
    # Only teachers can access
    if not request.user.is_teacher:
        messages.error(request, 'Access denied. Teachers only.')
        return redirect('examination_app:dashboard')

    # Get exams created by this teacher
    created_exams = Exam.objects.filter(created_by=request.user).order_by('-created_at')

    # Get statistics
    total_exams = created_exams.count()
    published_exams = created_exams.filter(status='published').count()
    total_students = User.objects.filter(role='student').count()

    # Get recent results from teacher's exams
    recent_results = ExamResult.objects.filter(
        exam__created_by=request.user
    ).select_related('student', 'exam').order_by('-completed_at')[:10]

    context = {
        'created_exams': created_exams[:5],
        'total_exams': total_exams,
        'published_exams': published_exams,
        'total_students': total_students,
        'recent_results': recent_results,
    }

    return render(request, 'examination_app/teacher_dashboard.html', context)


@login_required
def student_dashboard(request):
    """
    Student Dashboard
    Shows available exams, completed exams, and performance overview
    """
    # Only students can access
    if not request.user.is_student:
        messages.error(request, 'Access denied. Students only.')
        return redirect('examination_app:dashboard')

    # Get available exams (published, not taken yet, within date range)
    taken_exam_ids = ExamResult.objects.filter(
        student=request.user
    ).values_list('exam_id', flat=True)

    now = timezone.now()
    available_exams = Exam.objects.filter(
        status='published'
    ).exclude(
        id__in=taken_exam_ids
    ).filter(
        Q(start_date__isnull=True) | Q(start_date__lte=now)
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=now)
    ).select_related('subject', 'created_by').order_by('-start_date')

    # Get completed exams with results
    completed_exams = ExamResult.objects.filter(
        student=request.user
    ).select_related('exam', 'exam__subject').order_by('-completed_at')

    # Get performance analyses
    performance_analyses = PerformanceAnalysis.objects.filter(
        student=request.user
    ).select_related('subject').order_by('-last_updated')

    context = {
        'available_exams': available_exams,
        'completed_exams': completed_exams,
        'performance_analyses': performance_analyses,
    }

    return render(request, 'examination_app/student_dashboard.html', context)


# ============================
# EXAM MANAGEMENT VIEWS (TEACHER)
# ============================

@login_required
def create_exam(request):
    """
    Create a new exam
    """
    if not request.user.is_teacher:
        messages.error(request, 'Access denied.')
        return redirect('examination_app:dashboard')

    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.created_by = request.user
            exam.save()
            messages.success(request, f'Exam "{exam.title}" created successfully!')
            return redirect('examination_app:manage_exam', exam_id=exam.id)
    else:
        form = ExamForm()

    return render(request, 'examination_app/create_exam.html', {'form': form})


@login_required
def manage_exam(request, exam_id):
    """
    Manage an exam: View questions, add questions, edit exam
    """
    if not request.user.is_teacher:
        messages.error(request, 'Access denied.')
        return redirect('examination_app:dashboard')

    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    questions = exam.questions.all().order_by('question_number')

    # Initialize form for GET or re-render invalid POST
    if request.method != 'POST':
        form = QuestionForm(initial={'exam': exam})
    else:
        # POST request - validate and process
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.exam = exam
            # For True/False questions, clear option fields
            if question.question_type == 'true_false':
                question.option_a = ''
                question.option_b = ''
                question.option_c = None
                question.option_d = None
            try:
                question.save()
                messages.success(request, f'Question added successfully!')
                return redirect('examination_app:manage_exam', exam_id=exam.id)
            except IntegrityError:
                # Duplicate question number
                messages.error(request, f'Question number {question.question_number} already exists in this exam. Please use a different number.')
        # If form is invalid, it will be re-rendered with errors below

    context = {
        'exam': exam,
        'questions': questions,
        'form': form,
    }

    return render(request, 'examination_app/manage_exam.html', context)


@login_required
def update_exam(request, exam_id):
    """
    Update exam details
    """
    if not request.user.is_teacher:
        messages.error(request, 'Access denied.')
        return redirect('examination_app:dashboard')

    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)

    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, f'Exam updated successfully!')
            return redirect('examination_app:manage_exam', exam_id=exam.id)
    else:
        form = ExamForm(instance=exam)

    return render(request, 'examination_app/update_exam.html', {'form': form, 'exam': exam})


@login_required
def delete_exam(request, exam_id):
    """
    Delete an exam
    """
    if not request.user.is_teacher:
        messages.error(request, 'Access denied.')
        return redirect('examination_app:dashboard')

    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)

    if request.method == 'POST':
        exam.delete()
        messages.success(request, f'Exam deleted successfully!')
        return redirect('examination_app:teacher_dashboard')

    return render(request, 'examination_app/delete_exam.html', {'exam': exam})


@login_required
def delete_question(request, question_id):
    """
    Delete a question from an exam
    """
    if not request.user.is_teacher:
        return JsonResponse({'success': False, 'error': 'Access denied'})

    question = get_object_or_404(Question, id=question_id, exam__created_by=request.user)
    exam_id = question.exam.id

    if request.method == 'POST':
        question.delete()
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


# ============================
# EXAM TAKING VIEWS (STUDENT)
# ============================

@login_required
def take_exam(request, exam_id):
    """
    Take an exam - Display questions and submit answers
    """
    if not request.user.is_student:
        messages.error(request, 'Access denied.')
        return redirect('examination_app:dashboard')

    exam = get_object_or_404(Exam, id=exam_id, status='published')

    # Check if student already took this exam
    if ExamResult.objects.filter(student=request.user, exam=exam).exists():
        messages.warning(request, 'You have already taken this exam.')
        return redirect('examination_app:exam_result', exam_id=exam.id)

    # Check if exam is active
    if not exam.is_active:
        messages.error(request, 'This exam is not currently available.')
        return redirect('examination_app:student_dashboard')

    # Get or create exam progress
    progress, created = ExamProgress.objects.get_or_create(
        student=request.user,
        exam=exam,
        defaults={'current_question': 1, 'is_completed': False}
    )

    # Check if time is up
    if progress.started_at:
        elapsed = timezone.now() - progress.started_at
        elapsed_minutes = elapsed.total_seconds() / 60
        if elapsed_minutes >= exam.duration_minutes:
            messages.error(request, 'Time limit exceeded for this exam.')
            return redirect('examination_app:student_dashboard')

    questions = exam.questions.all().order_by('question_number')

    if request.method == 'POST':
        # Process exam submission
        total_questions = questions.count()
        correct_count = 0
        wrong_count = 0
        total_score = 0

        # Calculate time taken
        time_taken_minutes = int((timezone.now() - progress.started_at).total_seconds() / 60)

        # Delete any previous answers for this exam
        StudentAnswer.objects.filter(
            student=request.user,
            question__exam=exam
        ).delete()

        # Process each question
        for question in questions:
            field_name = f'question_{question.id}'
            selected_answer = request.POST.get(field_name, '')

            if selected_answer:
                student_answer = StudentAnswer.objects.create(
                    student=request.user,
                    question=question,
                    selected_answer=selected_answer
                )

                total_score += student_answer.marks_obtained
                if student_answer.is_correct:
                    correct_count += 1
                else:
                    wrong_count += 1

        # Calculate percentage
        percentage = (total_score / exam.total_marks) * 100 if exam.total_marks > 0 else 0

        # Determine pass/fail
        status = 'passed' if total_score >= exam.passing_marks else 'failed'

        # Create exam result
        result = ExamResult.objects.create(
            student=request.user,
            exam=exam,
            score=total_score,
            percentage=percentage,
            total_questions=total_questions,
            correct_answers=correct_count,
            wrong_answers=wrong_count,
            time_taken_minutes=time_taken_minutes,
            status=status
        )

        # Mark progress as completed
        progress.is_completed = True
        progress.save()

        # Trigger AI Performance Analysis
        analyze_performance(request.user, exam.subject)

        messages.success(request, 'Exam submitted successfully!')
        return redirect('examination_app:exam_result', exam_id=exam.id)

    # Initialize time if first time viewing
    if created:
        progress.started_at = timezone.now()
        progress.save()

    context = {
        'exam': exam,
        'questions': questions,
        'progress': progress,
        'time_remaining': exam.duration_minutes * 60,  # in seconds
    }

    return render(request, 'examination_app/take_exam.html', context)


@login_required
def exam_result(request, exam_id):
    """
    View exam results with detailed breakdown
    """
    if not request.user.is_student:
        messages.error(request, 'Access denied.')
        return redirect('examination_app:dashboard')

    exam = get_object_or_404(Exam, id=exam_id)
    result = get_object_or_404(ExamResult, student=request.user, exam=exam)

    # Get all answers for this exam
    answers = StudentAnswer.objects.filter(
        student=request.user,
        question__exam=exam
    ).select_related('question', 'question__topic').order_by('question__question_number')

    # Get subject-wise performance
    subject_performance = PerformanceAnalysis.objects.filter(
        student=request.user,
        subject=exam.subject
    ).first()

    context = {
        'exam': exam,
        'result': result,
        'answers': answers,
        'subject_performance': subject_performance,
    }

    return render(request, 'examination_app/exam_result.html', context)


# ============================
# AI PERFORMANCE ANALYSIS
# ============================

def analyze_performance(student, subject):
    """
    AI-BASED PERFORMANCE ANALYSIS FUNCTION

    This is the core "AI" logic that analyzes student performance and generates insights.

    Algorithm:
    1. Iterate through all StudentAnswers for the student in this subject
    2. Calculate accuracy per Topic (e.g., if Algebra accuracy < 50%, mark as "Weak")
    3. Calculate average time taken per question
    4. Generate textual suggestions based on performance
    5. Save this data to the PerformanceAnalysis model

    Args:
        student: User object (student)
        subject: Subject object

    Returns:
        PerformanceAnalysis object with insights
    """
    print(f"🔍 Running AI Analysis for {student.username} in {subject.name}...")

    # Get all exam results for this student in this subject
    exam_ids = Exam.objects.filter(subject=subject).values_list('id', flat=True)

    if not exam_ids:
        print(f"No exams found for {subject.name}")
        return None

    # Get all student answers for this subject
    student_answers = StudentAnswer.objects.filter(
        student=student,
        question__exam__in=exam_ids
    ).select_related('question', 'question__topic')

    if not student_answers.exists():
        print(f"No answers found for analysis")
        return None

    # Calculate overall statistics
    total_attempts = student_answers.count()
    correct_attempts = student_answers.filter(is_correct=True).count()
    overall_accuracy = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0

    # Calculate average time per question
    avg_time = student_answers.aggregate(
        avg_time=Avg('time_taken_seconds')
    )['avg_time'] or 0

    # Topic-wise analysis
    topic_stats = {}
    topics_in_subject = Topic.objects.filter(subject=subject)

    for topic in topics_in_subject:
        topic_answers = student_answers.filter(question__topic=topic)
        if topic_answers.exists():
            topic_correct = topic_answers.filter(is_correct=True).count()
            topic_total = topic_answers.count()
            topic_accuracy = (topic_correct / topic_total * 100) if topic_total > 0 else 0

            topic_stats[topic.name] = {
                'accuracy': round(topic_accuracy, 2),
                'attempts': topic_total,
                'correct': topic_correct
            }

    # Classify topics as weak or strong
    weak_topics = {}
    strong_topics = {}

    for topic_name, stats in topic_stats.items():
        if stats['accuracy'] < 50:
            weak_topics[topic_name] = stats['accuracy']
        elif stats['accuracy'] >= 70:
            strong_topics[topic_name] = stats['accuracy']

    # Generate AI-powered suggestions
    suggestions = generate_suggestions(
        overall_accuracy,
        weak_topics,
        strong_topics,
        avg_time
    )

    # Prepare detailed insights
    detailed_insights = {
        'topic_breakdown': topic_stats,
        'total_questions_attempted': total_attempts,
        'total_correct': correct_attempts,
        'total_wrong': total_attempts - correct_attempts,
        'accuracy_by_difficulty': calculate_accuracy_by_difficulty(student_answers),
        'improvement_trends': calculate_improvement_trends(student, subject)
    }

    # Create or update PerformanceAnalysis
    analysis, created = PerformanceAnalysis.objects.update_or_create(
        student=student,
        subject=subject,
        defaults={
            'weak_topics': weak_topics,
            'strong_topics': strong_topics,
            'overall_accuracy': round(overall_accuracy, 2),
            'total_attempts': total_attempts,
            'avg_time_per_question': round(avg_time, 2) if avg_time else None,
            'suggestions': suggestions,
            'detailed_insights': detailed_insights,
        }
    )

    print(f"✅ Analysis complete! Overall accuracy: {overall_accuracy:.2f}%")
    print(f"Weak topics: {list(weak_topics.keys())}")
    print(f"Strong topics: {list(strong_topics.keys())}")

    return analysis


def generate_suggestions(overall_accuracy, weak_topics, strong_topics, avg_time):
    """
    Generate textual suggestions based on performance analysis

    AI Logic for generating personalized feedback
    """
    suggestions = []

    # Overall performance feedback
    if overall_accuracy >= 90:
        suggestions.append("🌟 Excellent performance! You have mastered most concepts in this subject.")
    elif overall_accuracy >= 75:
        suggestions.append("👍 Good work! You have a strong understanding of this subject.")
    elif overall_accuracy >= 60:
        suggestions.append("📚 Satisfactory performance. There's room for improvement.")
    elif overall_accuracy >= 40:
        suggestions.append("⚠️ You need to focus more on this subject. Consider revisiting core concepts.")
    else:
        suggestions.append("🔴 Critical attention required. Please seek help from teachers and practice more.")

    # Weak topic suggestions
    if weak_topics:
        suggestions.append("\n📉 Areas Requiring Immediate Attention:")
        for topic, accuracy in weak_topics.items():
            if accuracy < 30:
                suggestions.append(f"  • {topic}: Very low accuracy ({accuracy}%). Start from basics and practice fundamentals.")
            elif accuracy < 50:
                suggestions.append(f"  • {topic}: Needs improvement ({accuracy}%). Review theory and solve more problems.")

    # Strong topic suggestions
    if strong_topics:
        suggestions.append("\n📈 Your Strengths:")
        for topic, accuracy in strong_topics.items():
            suggestions.append(f"  • {topic}: Strong performance ({accuracy}%)")

    # Time management suggestions
    if avg_time:
        if avg_time > 120:  # More than 2 minutes per question
            suggestions.append(f"\n⏱️ Time Management: You're averaging {avg_time:.0f} seconds per question. Try to improve your speed by practicing more.")
        elif avg_time < 30:  # Less than 30 seconds
            suggestions.append(f"\n⏱️ Time Management: You're answering quickly ({avg_time:.0f} seconds/question). Ensure you're reading questions carefully.")
        else:
            suggestions.append(f"\n⏱️ Time Management: Good pace at {avg_time:.0f} seconds per question.")

    # Specific actionable recommendations
    if weak_topics:
        suggestions.append("\n💡 Recommended Actions:")
        suggestions.append("  1. Focus on weak topics with consistent daily practice")
        suggestions.append("  2. Review incorrect answers to understand mistakes")
        suggestions.append("  3. Take practice tests specifically for weak areas")
        suggestions.append("  4. Consider forming study groups for difficult topics")

    return "\n".join(suggestions)


def calculate_accuracy_by_difficulty(student_answers):
    """
    Calculate accuracy based on question marks (proxy for difficulty)
    Higher marks = Higher difficulty
    """
    difficulty_stats = {
        'easy': {'correct': 0, 'total': 0},      # 1 mark questions
        'medium': {'correct': 0, 'total': 0},    # 2-3 mark questions
        'hard': {'correct': 0, 'total': 0},      # 4+ mark questions
    }

    for answer in student_answers:
        marks = answer.question.marks

        if marks <= 1:
            difficulty = 'easy'
        elif marks <= 3:
            difficulty = 'medium'
        else:
            difficulty = 'hard'

        difficulty_stats[difficulty]['total'] += 1
        if answer.is_correct:
            difficulty_stats[difficulty]['correct'] += 1

    # Calculate percentages
    result = {}
    for difficulty, stats in difficulty_stats.items():
        if stats['total'] > 0:
            result[difficulty] = round(
                (stats['correct'] / stats['total']) * 100, 2
            )

    return result


def calculate_improvement_trends(student, subject):
    """
    Calculate improvement trends by comparing recent vs older performance
    """
    # Get exam results in chronological order
    exam_ids = list(Exam.objects.filter(subject=subject).values_list('id', flat=True))
    results = ExamResult.objects.filter(
        student=student,
        exam__in=exam_ids
    ).order_by('completed_at')

    if results.count() < 2:
        return {'trend': 'insufficient_data'}

    # Split into first half and second half
    mid_point = results.count() // 2
    early_results = results[:mid_point]
    recent_results = results[mid_point:]

    early_avg = early_results.aggregate(Avg('percentage'))['percentage__avg'] or 0
    recent_avg = recent_results.aggregate(Avg('percentage'))['percentage__avg'] or 0

    improvement = recent_avg - early_avg

    if improvement > 10:
        trend = 'improving'
    elif improvement < -10:
        trend = 'declining'
    else:
        trend = 'stable'

    return {
        'trend': trend,
        'improvement_percentage': round(improvement, 2),
        'early_average': round(early_avg, 2),
        'recent_average': round(recent_avg, 2)
    }


# ============================
# PERFORMANCE ANALYSIS VIEWS
# ============================

@login_required
def performance_report(request, subject_id=None):
    """
    View detailed performance report with charts
    """
    if not request.user.is_student:
        messages.error(request, 'Access denied.')
        return redirect('examination_app:dashboard')

    student = request.user

    # Get all subjects in which student has attempted exams
    exam_ids = ExamResult.objects.filter(student=student).values_list('exam_id', flat=True)
    subjects = Subject.objects.filter(exams__in=exam_ids).distinct()

    # If subject_id provided, filter by subject
    if subject_id:
        selected_subject = get_object_or_404(Subject, id=subject_id)
        analyses = [PerformanceAnalysis.objects.filter(
            student=student,
            subject=selected_subject
        ).first()]
    else:
        selected_subject = None
        analyses = PerformanceAnalysis.objects.filter(student=student).select_related('subject')

    # Prepare chart data
    chart_data = prepare_chart_data(analyses, student)

    context = {
        'subjects': subjects,
        'selected_subject': selected_subject,
        'analyses': analyses,
        'chart_data': chart_data,
    }

    return render(request, 'examination_app/performance_report.html', context)


def prepare_chart_data(analyses, student):
    """
    Prepare data for Chart.js visualizations
    """
    chart_data = {
        'radar_chart': {
            'labels': [],
            'datasets': []
        },
        'bar_chart': {
            'labels': [],
            'weak_topics': [],
            'strong_topics': []
        },
        'line_chart': {
            'labels': [],
            'accuracy': []
        }
    }

    for analysis in analyses:
        if not analysis:
            continue

        subject_name = analysis.subject.name

        # Radar chart data - subject-wise performance
        if subject_name not in chart_data['radar_chart']['labels']:
            chart_data['radar_chart']['labels'].append(subject_name)
            chart_data['radar_chart']['datasets'].append(
                round(analysis.overall_accuracy, 2)
            )

    # Line chart - exam performance over time
    results = ExamResult.objects.filter(student=student).select_related('exam__subject').order_by('completed_at')

    for result in results:
        chart_data['line_chart']['labels'].append(
            result.completed_at.strftime('%Y-%m-%d')
        )
        chart_data['line_chart']['accuracy'].append(
            round(result.percentage, 2)
        )

    # Bar chart - topic breakdown for first analysis
    if analyses:
        first_analysis = analyses[0]
        if first_analysis:
            chart_data['bar_chart']['labels'] = list(first_analysis.detailed_insights.get('topic_breakdown', {}).keys())

            for topic in chart_data['bar_chart']['labels']:
                if topic in first_analysis.weak_topics:
                    chart_data['bar_chart']['weak_topics'].append(
                        first_analysis.weak_topics[topic]
                    )
                else:
                    chart_data['bar_chart']['weak_topics'].append(0)

                if topic in first_analysis.strong_topics:
                    chart_data['bar_chart']['strong_topics'].append(
                        first_analysis.strong_topics[topic]
                    )
                else:
                    chart_data['bar_chart']['strong_topics'].append(0)

    return chart_data


@login_required
def trigger_analysis(request):
    """
    Manually trigger performance analysis for all subjects
    """
    if not request.user.is_student:
        messages.error(request, 'Access denied.')
        return redirect('examination_app:dashboard')

    student = request.user

    # Get all subjects the student has exams in
    exam_ids = ExamResult.objects.filter(student=student).values_list('exam_id', flat=True)
    subjects = Subject.objects.filter(exams__in=exam_ids).distinct()

    analyzed_count = 0
    for subject in subjects:
        result = analyze_performance(student, subject)
        if result:
            analyzed_count += 1

    messages.success(request, f'Analysis completed for {analyzed_count} subject(s)!')
    return redirect('examination_app:performance_report')


# ============================
# SUBJECT & TOPIC MANAGEMENT (TEACHER)
# ============================

@login_required
def manage_subjects(request):
    """
    View and manage subjects
    """
    if not request.user.is_teacher:
        messages.error(request, 'Access denied.')
        return redirect('examination_app:dashboard')

    subjects = Subject.objects.all().prefetch_related('topics')

    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject created successfully!')
            return redirect('examination_app:manage_subjects')
    else:
        form = SubjectForm()

    context = {
        'subjects': subjects,
        'form': form,
    }

    return render(request, 'examination_app/manage_subjects.html', context)


@login_required
def create_topic(request):
    """
    Create a new topic
    """
    if not request.user.is_teacher:
        messages.error(request, 'Access denied.')
        return redirect('examination_app:dashboard')

    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Topic created successfully!')
            return redirect('examination_app:manage_subjects')

    form = TopicForm()
    return render(request, 'examination_app/create_topic.html', {'form': form})


# ============================
# UTILITY VIEWS
# ============================

@login_required
def profile(request):
    """
    User profile view
    """
    user = request.user

    # Get user statistics
    if user.is_student:
        total_exams_taken = ExamResult.objects.filter(student=user).count()
        total_exams_created = 0
        total_questions_created = 0
    else:
        total_exams_created = Exam.objects.filter(created_by=user).count()
        total_exams_taken = 0
        # Calculate total questions created by this teacher
        from django.db.models import Count
        questions_data = Exam.objects.filter(created_by=user).aggregate(count=Count('questions'))
        total_questions_created = questions_data['count'] or 0

    context = {
        'user': user,
        'total_exams_taken': total_exams_taken,
        'total_exams_created': total_exams_created,
        'total_questions_created': total_questions_created,
    }

    return render(request, 'examination_app/profile.html', context)
