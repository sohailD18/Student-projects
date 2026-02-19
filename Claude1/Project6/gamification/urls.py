from django.urls import path
from . import views

urlpatterns = [
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('badges/', views.badges_list, name='badges_list'),
    path('stats/', views.platform_stats, name='platform_stats'),
]
