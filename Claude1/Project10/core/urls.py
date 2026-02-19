from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # ==================== PUBLIC PAGES (Accessible to All) ====================
    path('', views.home, name='home'),
    path('skills/', views.skill_list, name='skill_list'),
    path('skills/<int:skill_id>/', views.skill_detail, name='skill_detail'),

    # ==================== TEACHER ONLY PAGES ====================
    # Teacher: Create and manage skills
    path('teachers/skills/create/', views.create_skill, name='create_skill'),
    path('teachers/skills/<int:skill_id>/update/', views.update_skill, name='update_skill'),

    # Teacher: Manage teaching sessions
    path('teachers/sessions/', views.teacher_sessions, name='teacher_sessions'),
    path('teachers/sessions/<int:session_id>/', views.session_detail, name='session_detail'),
    path('teachers/sessions/<int:session_id>/accept/', views.accept_session, name='accept_session'),
    path('teachers/sessions/<int:session_id>/complete/', views.complete_session, name='complete_session'),
    path('teachers/sessions/<int:session_id>/cancel/', views.update_session_status, name='cancel_session'),

    # ==================== STUDENT ONLY PAGES ====================
    # Student: Book and manage learning sessions
    path('students/sessions/', views.student_sessions, name='student_sessions'),
    path('students/sessions/<int:session_id>/', views.session_detail, name='session_detail'),
    path('students/skills/<int:skill_id>/book/', views.book_session, name='book_session'),
    path('students/sessions/<int:session_id>/cancel/', views.update_session_status, name='cancel_session'),

    # ==================== ADMIN ONLY PAGES ====================
    path('admin/analytics/', views.admin_analytics, name='admin_analytics'),
]
