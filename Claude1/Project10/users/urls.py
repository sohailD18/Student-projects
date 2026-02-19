from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Role-specific Dashboards
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),

    # Profile
    path('profile/update/', views.profile_update, name='profile_update'),
    path('profile/<str:username>/', views.profile_view, name='profile_view'),

    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
]
