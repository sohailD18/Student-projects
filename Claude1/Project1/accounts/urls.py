from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.custom_login, name='login'),
    path('register/', views.custom_register, name='register'),
    path('logout/', views.custom_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('employer-profile/', views.employer_profile, name='employer_profile'),
    path('job-seeker/', views.job_seeker_dashboard, name='job_seeker_dashboard'),
    path('employer/', views.employer_dashboard, name='employer_dashboard'),
]
