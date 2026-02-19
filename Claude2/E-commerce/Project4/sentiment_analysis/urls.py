from django.urls import path
from . import views

app_name = 'sentiment_analysis'

urlpatterns = [
    # Authentication routes
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Page routes
    path('', views.dashboard, name='dashboard'),
    path('submit/', views.index, name='index'),

    # API routes
    path('api/submit-review/', views.submit_review, name='submit_review'),
    path('api/dashboard-data/', views.dashboard_api, name='dashboard_api'),
    path('api/recent-reviews/', views.recent_reviews, name='recent_reviews'),
]
