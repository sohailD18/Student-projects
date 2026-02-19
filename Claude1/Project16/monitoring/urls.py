from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'monitoring'

urlpatterns = [
    path('', lambda request: redirect('monitoring:student_login'), name='home'),
    path('login/', views.student_login, name='student_login'),
    path('logout/', views.student_logout, name='student_logout'),
    path('dashboard/', views.exam_dashboard, name='exam_dashboard'),
    path('exam/<int:exam_id>/', views.take_exam, name='take_exam'),
    path('exam/<int:exam_id>/submit/', views.submit_exam, name='submit_exam'),
    path('exam/<int:exam_id>/results/', views.exam_results, name='exam_results'),
    path('exam/<int:exam_id>/integrity-report/', views.integrity_report, name='integrity_report'),
    path('api/log-violation/', views.log_violation, name='log_violation'),
    path('api/create-session/', views.create_session, name='create_session'),
    path('api/capture-frame/', views.capture_frame, name='capture_frame'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/exam/create/', views.create_exam, name='create_exam'),
]
