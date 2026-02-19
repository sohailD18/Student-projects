"""
ProductivityMind - URL Configuration for Tasks App
"""
from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # =============================================================================
    # Authentication
    # =============================================================================
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # =============================================================================
    # Template Views (HTML Pages)
    # =============================================================================
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('tasks/', views.tasks_view, name='tasks'),
    path('tasks/<int:task_id>/', views.task_detail_view, name='task_detail'),
    path('projects/', views.projects_view, name='projects'),
    path('reports/', views.reports_view, name='reports'),
    path('calendar/', views.calendar_view, name='calendar'),

    # =============================================================================
    # API Endpoints - Tasks
    # =============================================================================
    path('api/tasks/', views.api_tasks_list, name='api_tasks_list'),
    path('api/tasks/<int:task_id>/', views.api_task_detail, name='api_task_detail'),
    path('api/tasks/create/', views.api_task_create, name='api_task_create'),
    path('api/tasks/<int:task_id>/update/', views.api_task_update, name='api_task_update'),
    path('api/tasks/<int:task_id>/delete/', views.api_task_delete, name='api_task_delete'),
    path('api/tasks/bulk-status/', views.api_task_bulk_status, name='api_task_bulk_status'),

    # =============================================================================
    # API Endpoints - Projects
    # =============================================================================
    path('api/projects/', views.api_projects_list, name='api_projects_list'),
    path('api/projects/<int:project_id>/', views.api_project_detail, name='api_project_detail'),
    path('api/projects/create/', views.api_project_create, name='api_project_create'),

    # =============================================================================
    # API Endpoints - Categories & Tags
    # =============================================================================
    path('api/categories/', views.api_categories_list, name='api_categories_list'),
    path('api/tags/', views.api_tags_list, name='api_tags_list'),

    # =============================================================================
    # API Endpoints - Dashboard & Analytics
    # =============================================================================
    path('api/dashboard/', views.api_dashboard, name='api_dashboard'),
    path('api/analytics/trends/', views.api_analytics_trends, name='api_analytics_trends'),
    path('api/analytics/user/<int:user_id>/', views.api_user_stats, name='api_user_stats'),
    path('api/analytics/user/me/', views.api_user_stats, name='api_my_stats'),

    # =============================================================================
    # API Endpoints - Reports
    # =============================================================================
    path('api/reports/summary/', views.api_reports_summary, name='api_reports_summary'),

    # =============================================================================
    # API Endpoints - AI Engine
    # =============================================================================
    path('api/ai/recalculate/', views.api_ai_recalculate, name='api_ai_recalculate'),
    path('api/ai/risk-assessment/', views.api_risk_assessment, name='api_risk_assessment'),

    # =============================================================================
    # API Endpoints - Work Logs
    # =============================================================================
    path('api/work-logs/', views.api_work_logs_list, name='api_work_logs_list'),
    path('api/work-logs/create/', views.api_work_log_create, name='api_work_log_create'),

    # =============================================================================
    # API Endpoints - Users
    # =============================================================================
    path('api/users/', views.api_users_list, name='api_users_list'),
]
