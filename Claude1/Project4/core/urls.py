from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('log/', views.log_activity, name='log_activity'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('community-stats/', views.community_stats, name='community_stats'),
]
