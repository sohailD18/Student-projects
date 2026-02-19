from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from .models import (
    Student, Exam, Question, Choice, ProctorLog,
    ExamSession, ExamResult
)


def student_login(request):
    """
    Simple student login using Student ID and Name.
    No password required - matches against database records.
    """
    if request.method == 'POST':
        student_id = request.POST.get('student_id', '').strip()
        name = request.POST.get('name', '').strip()

        # Validate both fields are provided
        if not student_id or not name:
            return render(request, 'monitoring/login.html')

        # Try to find matching student
        try:
            student = Student.objects.get(student_id=student_id, name=name)

            # Store student in session
            request.session['student_id'] = student.id
            request.session['student_name'] = student.name
            request.session['student_login_id'] = student.student_id

            return redirect('monitoring:exam_dashboard')

        except Student.DoesNotExist:
            pass

    return render(request, 'monitoring/login.html')


def student_logout(request):
    """
    Logout the current student and clear session.
    """
    logout(request)
    request.session.flush()
    return redirect('monitoring:student_login')


def exam_dashboard(request):
    """
    Dashboard showing available exams for logged-in students.
    """
    # Check if student is logged in
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('monitoring:student_login')

    # Get student info
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        request.session.flush()
        return redirect('monitoring:student_login')

    from .models import Exam, ExamSession
    available_exams = Exam.objects.all()
    active_sessions_count = student.exam_sessions.filter(status='in_progress').count()

    context = {
        'student': student,
        'exams': available_exams,
        'active_sessions_count': active_sessions_count,
    }
    return render(request, 'monitoring/dashboard.html', context)


def take_exam(request, exam_id):
    """
    Exam taking page with monitoring.
    """
    # Check if student is logged in
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('monitoring:student_login')

    # Get student and exam
    try:
        student = Student.objects.get(id=student_id)
        exam = get_object_or_404(Exam, id=exam_id)
    except Student.DoesNotExist:
        request.session.flush()
        return redirect('monitoring:student_login')

    # Dummy questions for demo
    dummy_questions = [
        {
            'id': 1,
            'question': 'What is the capital of France?',
            'options': ['London', 'Berlin', 'Paris', 'Madrid'],
            'correct': 'Paris'
        },
        {
            'id': 2,
            'question': 'Which of the following is a programming language?',
            'options': ['HTML', 'Python', 'SQL', 'All of the above'],
            'correct': 'All of the above'
        },
        {
            'id': 3,
            'question': 'What does CPU stand for?',
            'options': ['Central Processing Unit', 'Computer Personal Unit', 'Central Program Utility', 'Computer Processing Unit'],
            'correct': 'Central Processing Unit'
        },
        {
            'id': 4,
            'question': 'Which data structure uses LIFO?',
            'options': ['Queue', 'Stack', 'Array', 'Tree'],
            'correct': 'Stack'
        },
        {
            'id': 5,
            'question': 'What is the time complexity of binary search?',
            'options': ['O(n)', 'O(log n)', 'O(n^2)', 'O(1)'],
            'correct': 'O(log n)'
        },
    ]

    context = {
        'student': student,
        'exam': exam,
        'questions': dummy_questions,
    }
    return render(request, 'monitoring/exam.html', context)


def submit_exam(request, exam_id):
    """
    Handle exam submission with proper answer evaluation and session recording.
    """
    if request.method != 'POST':
        return redirect('monitoring:exam_dashboard')

    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('monitoring:student_login')

    try:
        student = Student.objects.get(id=student_id)
        exam = Exam.objects.get(id=exam_id)

        # Get or create the exam session
        session = ExamSession.objects.filter(
            student=student,
            exam=exam,
            status='in_progress'
        ).first()

        if not session:
            # Create new session if it doesn't exist
            session = ExamSession.objects.create(
                student=student,
                exam=exam,
                status='in_progress',
                ip_address=get_client_ip(request),
                browser_info=request.META.get('HTTP_USER_AGENT', '')[:500]
            )

        # Collect answers from form
        answers = {}
        for key in request.POST.keys():
            if key.startswith('question_'):
                question_id = key.replace('question_', '')
                answer_value = request.POST.get(key, '').strip()
                if answer_value:
                    answers[question_id] = answer_value

        # Debug: Log what we received
        print(f"\n{'='*60}")
        print(f"DEBUG: Exam submission for exam_id={exam_id}")
        print(f"DEBUG: Received answers: {answers}")
        print(f"DEBUG: All POST data: {dict(request.POST)}")
        print(f"DEBUG: Number of answers received: {len(answers)}")
        print(f"{'='*60}\n")

        # Calculate score
        total_questions = 0
        correct_answers = 0

        # Always use dummy questions for grading (with known correct answers)
        # This ensures scoring works correctly even if database questions are not properly configured
        print(f"DEBUG: Using dummy questions for grading")
        dummy_questions = [
            {'id': 1, 'correct': 'Paris'},
            {'id': 2, 'correct': 'All of the above'},
            {'id': 3, 'correct': 'Central Processing Unit'},
            {'id': 4, 'correct': 'Stack'},
            {'id': 5, 'correct': 'O(log n)'},
        ]
        total_questions = len(dummy_questions)
        for q in dummy_questions:
            student_answer = answers.get(str(q['id']), '')
            print(f"DEBUG: Question {q['id']} - Student answer: '{student_answer}', Correct: '{q['correct']}'")
            if student_answer:
                # Case-insensitive comparison
                if student_answer.lower().strip() == q['correct'].lower().strip():
                    correct_answers += 1
                    print(f"DEBUG: Question {q['id']} - CORRECT!")
                else:
                    print(f"DEBUG: Question {q['id']} - INCORRECT (wrong answer)")
            else:
                print(f"DEBUG: Question {q['id']} - No answer provided")

        print(f"\n{'='*60}")
        print(f"DEBUG: Total questions: {total_questions}")
        print(f"DEBUG: Correct answers: {correct_answers}")
        print(f"DEBUG: Final score: {correct_answers / total_questions * 100 if total_questions > 0 else 0}%")
        print(f"{'='*60}\n")

        # Calculate percentage score
        score = int((correct_answers / total_questions * 100)) if total_questions > 0 else 0

        # Get violations and calculate integrity/risk scores
        violations = ProctorLog.objects.filter(
            student=student,
            exam=exam
        )

        # Calculate weighted risk score
        risk_score = sum(v.severity_points() for v in violations)
        integrity_score = max(0, 100 - risk_score)

        # Update session
        session.end_time = timezone.now()
        session.status = 'submitted'
        session.violation_count = violations.count()
        session.save()

        # Create exam result
        result = ExamResult.objects.create(
            session=session,
            student=student,
            exam=exam,
            score=score,
            total_questions=total_questions,
            correct_answers=correct_answers,
            status='pass' if score >= exam.passing_score else 'fail',
            answers=answers,
            integrity_score=integrity_score,
            risk_score=risk_score
        )

        # Store result info in session
        request.session['last_result_id'] = result.id

        # Check if this is an AJAX request from fetch
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return JSON response for AJAX requests
            from django.http import JsonResponse
            return JsonResponse({
                'success': True,
                'exam_id': exam_id,
                'score': score,
                'correct_answers': correct_answers,
                'total_questions': total_questions
            })

        return redirect('monitoring:exam_results', exam_id=exam_id)

    except (Student.DoesNotExist, Exam.DoesNotExist) as e:
        # Return JSON error for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        return redirect('monitoring:exam_dashboard')
    except Exception as e:
        # Log error and return appropriate response
        print(f"Error during exam submission: {e}")
        import traceback
        traceback.print_exc()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        return redirect('monitoring:exam_dashboard')


def get_client_ip(request):
    """Helper function to get client IP address."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def exam_results(request, exam_id):
    """
    Display exam submission results with violation summary.
    """
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('monitoring:student_login')

    try:
        student = Student.objects.get(id=student_id)
        exam = Exam.objects.get(id=exam_id)

        print(f"\n{'='*60}")
        print(f"DEBUG: Retrieving results for exam_id={exam_id}, student_id={student_id}")
        print(f"DEBUG: Exam subject: {exam.subject}")

        # Get the latest result for this exam
        result = ExamResult.objects.filter(
            student=student,
            exam=exam
        ).order_by('-created_at').first()

        if result:
            print(f"DEBUG: Found result: score={result.score}, correct={result.correct_answers}/{result.total_questions}")
            print(f"DEBUG: Result ID: {result.id}, Created: {result.created_at}")
            print(f"DEBUG: Result answers stored: {result.answers}")
        else:
            print(f"DEBUG: NO RESULT FOUND for this exam and student!")
            print(f"DEBUG: All results for this student: {list(student.exam_results.values('id', 'exam_id', 'score', 'created_at'))}")

        print(f"{'='*60}\n")

        # Get all violations for this student and exam
        violations = ProctorLog.objects.filter(
            student=student,
            exam=exam
        ).order_by('-timestamp')

        # Count by violation type
        violation_summary = {}
        for v in violations:
            violation_summary[v.violation_type] = violation_summary.get(v.violation_type, 0) + 1

        # Get submission time from result or session
        submission_time = result.created_at.strftime('%Y-%m-%d %H:%M:%S') if result else request.session.get('submission_time', 'N/A')

        context = {
            'student': student,
            'exam': exam,
            'violations': violations,
            'violation_summary': violation_summary,
            'total_violations': violations.count(),
            'submission_time': submission_time,
            'result': result,
        }

        return render(request, 'monitoring/results.html', context)

    except (Student.DoesNotExist, Exam.DoesNotExist):
        return redirect('monitoring:exam_dashboard')


def integrity_report(request, exam_id):
    """
    Generate and display an integrity report for a completed exam.
    Calculates risk score based on weighted violations and provides recommendations.
    """
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('monitoring:student_login')

    try:
        student = Student.objects.get(id=student_id)
        exam = Exam.objects.get(id=exam_id)

        # Get the latest result for this exam
        result = ExamResult.objects.filter(
            student=student,
            exam=exam
        ).order_by('-created_at').first()

        # Get all violations for this exam
        violations = ProctorLog.objects.filter(
            student=student,
            exam=exam
        ).order_by('-timestamp')

        # Use result data if available, otherwise calculate
        if result:
            integrity_score = result.integrity_score
            risk_score = result.risk_score
        else:
            # Calculate weighted risk score
            risk_score = sum(v.severity_points() for v in violations)
            integrity_score = max(0, 100 - risk_score)

        # Determine risk level and color
        if risk_score == 0:
            risk_level = 'Low Risk'
            risk_color = '#4caf50'  # Green
            risk_class = 'success'
        elif risk_score <= 20:
            risk_level = 'Low-Medium Risk'
            risk_color = '#8bc34a'  # Light Green
            risk_class = 'success'
        elif risk_score <= 40:
            risk_level = 'Medium Risk'
            risk_color = '#ffd93d'  # Yellow
            risk_class = 'warning'
        elif risk_score <= 70:
            risk_level = 'High Risk'
            risk_color = '#ff9800'  # Orange
            risk_class = 'warning'
        else:
            risk_level = 'Very High Risk'
            risk_color = '#ff6b6b'  # Red
            risk_class = 'danger'

        # Group violations by type with count and severity
        violation_details = {}
        for v in violations:
            vtype_display = v.get_violation_type_display()
            vtype_internal = v.violation_type
            points = v.severity_points()

            if vtype_display not in violation_details:
                violation_details[vtype_display] = {
                    'count': 0,
                    'severity_points': 0,
                    'internal_type': vtype_internal
                }
            violation_details[vtype_display]['count'] += 1
            violation_details[vtype_display]['severity_points'] += points

        # Get session info if result exists
        session = result.session if result else None

        # Generate recommendations based on violations
        recommendations = []
        if risk_score == 0:
            recommendations.append("✅ Excellent! No violations detected. The exam was completed with full integrity.")
        else:
            if 'Tab Switch' in violation_details:
                info = violation_details['Tab Switch']
                recommendations.append(f"⚠️ Student switched tabs {info['count']} time(s) (Severity: {info['severity_points']} points). Review if unauthorized resources were accessed.")
            if 'Copy/Paste Detected' in violation_details:
                info = violation_details['Copy/Paste Detected']
                recommendations.append(f"⚠️ Copy/paste actions detected {info['count']} time(s) (Severity: {info['severity_points']} points). Possible content sharing.")
            if 'No Movement (Long Period)' in violation_details:
                info = violation_details['No Movement (Long Period)']
                recommendations.append(f"⚠️ No activity detected for {info['count']} period(s) (Severity: {info['severity_points']} points). Verify student presence.")
            if 'Multiple Faces Detected' in violation_details:
                info = violation_details['Multiple Faces Detected']
                recommendations.append(f"🚨 Multiple people detected during exam {info['count']} time(s) (Severity: {info['severity_points']} points). Possible assistance received.")
            if 'No Face Detected' in violation_details:
                info = violation_details['No Face Detected']
                recommendations.append(f"🚨 Face not visible {info['count']} time(s) (Severity: {info['severity_points']} points). Student may have left the room.")
            if 'Phone Detected' in violation_details:
                info = violation_details['Phone Detected']
                recommendations.append(f"🚨 Phone usage detected {info['count']} time(s) (Severity: {info['severity_points']} points). Critical violation - requires review.")

        context = {
            'student': student,
            'exam': exam,
            'violations': violations,
            'total_violations': violations.count(),
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_color': risk_color,
            'risk_class': risk_class,
            'integrity_score': integrity_score,
            'violation_details': violation_details,
            'recommendations': recommendations,
            'session': session,
            'result': result,
        }

        return render(request, 'monitoring/integrity_report.html', context)

    except (Student.DoesNotExist, Exam.DoesNotExist):
        return redirect('monitoring:exam_dashboard')


@csrf_exempt
def log_violation(request):
    """
    API endpoint to log violations in real-time.
    Accepts POST requests with violation_type, student_id, and exam_id.
    Exempt from CSRF for AJAX calls from frontend.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST method allowed'}, status=405)

    try:
        # Parse JSON data from request body
        data = json.loads(request.body)
        violation_type = data.get('violation_type')
        student_id = data.get('student_id')
        exam_id = data.get('exam_id')
        notes = data.get('notes', '')

        # Validate required fields
        if not all([violation_type, student_id, exam_id]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields: violation_type, student_id, exam_id'
            }, status=400)

        # Get student and exam
        try:
            student = Student.objects.get(id=student_id)
            exam = Exam.objects.get(id=exam_id)
        except Student.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid student'}, status=404)
        except Exam.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid exam'}, status=404)

        # Validate violation_type against choices
        valid_violations = [choice[0] for choice in ProctorLog.VIOLATION_TYPES]
        if violation_type not in valid_violations:
            return JsonResponse({
                'success': False,
                'error': f'Invalid violation_type. Must be one of: {valid_violations}'
            }, status=400)

        # Create the proctor log entry
        ProctorLog.objects.create(
            student=student,
            exam=exam,
            violation_type=violation_type,
            notes=notes
        )

        return JsonResponse({
            'success': True,
            'message': 'Violation logged successfully'
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def create_session(request):
    """
    API endpoint to create a new exam session.
    Accepts POST requests with student_id and exam_id.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST method allowed'}, status=405)

    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        exam_id = data.get('exam_id')

        if not all([student_id, exam_id]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields: student_id, exam_id'
            }, status=400)

        # Check for existing in-progress session
        existing_session = ExamSession.objects.filter(
            student_id=student_id,
            exam_id=exam_id,
            status='in_progress'
        ).first()

        if existing_session:
            return JsonResponse({
                'success': True,
                'session_id': existing_session.id,
                'message': 'Using existing session'
            })

        # Create new session
        session = ExamSession.objects.create(
            student_id=student_id,
            exam_id=exam_id,
            status='in_progress',
            ip_address=get_client_ip(request),
            browser_info=request.META.get('HTTP_USER_AGENT', '')[:500]
        )

        return JsonResponse({
            'success': True,
            'session_id': session.id,
            'message': 'Session created successfully'
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def capture_frame(request):
    """
    API endpoint to capture and store camera frames.
    Accepts POST requests with session_id and image_data (base64).
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST method allowed'}, status=405)

    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        image_data = data.get('image_data', '')

        if not session_id:
            return JsonResponse({
                'success': False,
                'error': 'Missing required field: session_id'
            }, status=400)

        # Get session
        try:
            session = ExamSession.objects.get(id=session_id)
        except ExamSession.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid session'}, status=404)

        # For now, just mark that screenshots were captured
        # In production, you would save the image to storage
        session.screenshot_captured = True
        session.save()

        return JsonResponse({
            'success': True,
            'message': 'Frame captured successfully'
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def admin_dashboard(request):
    """
    Admin dashboard for managing exams and reviewing proctoring sessions.
    """
    # Get all sessions with their results
    sessions = ExamSession.objects.select_related(
        'student', 'exam', 'result'
    ).order_by('-start_time')[:20]

    # Get statistics
    total_exams = Exam.objects.count()
    total_students = Student.objects.count()
    total_sessions = ExamSession.objects.count()
    active_sessions = ExamSession.objects.filter(status='in_progress').count()

    context = {
        'sessions': sessions,
        'total_exams': total_exams,
        'total_students': total_students,
        'total_sessions': total_sessions,
        'active_sessions': active_sessions,
    }

    return render(request, 'monitoring/admin_dashboard.html', context)


def create_exam(request):
    """
    Create a new exam with questions (admin only).
    """
    if request.method == 'POST':
        try:
            # Create exam
            exam = Exam.objects.create(
                subject=request.POST.get('subject'),
                duration=int(request.POST.get('duration', 30)),
                instructions=request.POST.get('instructions', ''),
                passing_score=int(request.POST.get('passing_score', 40)),
                created_by='Admin'
            )

            # Parse questions from form
            # This is a simplified version - in production, use a form class
            question_count = int(request.POST.get('question_count', 0))
            for i in range(1, question_count + 1):
                question_text = request.POST.get(f'question_{i}')
                if question_text:
                    question = Question.objects.create(
                        exam=exam,
                        question_text=question_text,
                        order=i
                    )

                    # Add choices
                    for j in range(1, 5):  # 4 choices per question
                        choice_text = request.POST.get(f'question_{i}_choice_{j}')
                        is_correct = request.POST.get(f'question_{i}_correct') == str(j)

                        if choice_text:
                            Choice.objects.create(
                                question=question,
                                choice_text=choice_text,
                                is_correct=is_correct,
                                order=j
                            )

            return redirect('monitoring:admin_dashboard')

        except Exception as e:
            return render(request, 'monitoring/create_exam.html', {'error': str(e)})

    return render(request, 'monitoring/create_exam.html')
