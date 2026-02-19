"""
URL Configuration for Examination App
"""
from django.urls import path
from . import views

app_name = 'examination_app'

urlpatterns = [
    # Authentication URLs
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Dashboard URLs
    path('', views.dashboard, name='dashboard'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),

    # Subject & Topic Management (Teacher)
    path('manage-subjects/', views.manage_subjects, name='manage_subjects'),
    path('create-topic/', views.create_topic, name='create_topic'),

    # Exam Management (Teacher)
    path('create-exam/', views.create_exam, name='create_exam'),
    path('exam/<int:exam_id>/manage/', views.manage_exam, name='manage_exam'),
    path('exam/<int:exam_id>/update/', views.update_exam, name='update_exam'),
    path('exam/<int:exam_id>/delete/', views.delete_exam, name='delete_exam'),
    path('question/<int:question_id>/delete/', views.delete_question, name='delete_question'),

    # Exam Taking (Student)
    path('exam/<int:exam_id>/take/', views.take_exam, name='take_exam'),
    path('exam/<int:exam_id>/result/', views.exam_result, name='exam_result'),

    # Performance Analysis
    path('performance-report/', views.performance_report, name='performance_report'),
    path('performance-report/subject/<int:subject_id>/', views.performance_report, name='performance_report_subject'),
    path('trigger-analysis/', views.trigger_analysis, name='trigger_analysis'),

    # Profile
    path('profile/', views.profile, name='profile'),
]
