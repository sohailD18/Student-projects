from django.urls import path
from . import views

app_name = 'campaigns'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Email Lists
    path('email-lists/', views.email_list_list, name='email_list_list'),
    path('email-lists/create/', views.email_list_create, name='email_list_create'),
    path('email-lists/<int:pk>/', views.email_list_detail, name='email_list_detail'),
    path('email-lists/<int:pk>/delete/', views.email_list_delete, name='email_list_delete'),

    # Subscribers
    path('subscribers/', views.subscriber_list, name='subscriber_list'),
    path('subscribers/create/', views.subscriber_create, name='subscriber_create'),
    path('subscribers/import/', views.subscriber_import, name='subscriber_import'),
    path('subscribers/<int:pk>/delete/', views.subscriber_delete, name='subscriber_delete'),

    # Email Templates
    path('templates/', views.template_list, name='template_list'),
    path('templates/create/', views.template_create, name='template_create'),
    path('templates/<int:pk>/', views.template_detail, name='template_detail'),
    path('templates/<int:pk>/edit/', views.template_edit, name='template_edit'),
    path('templates/<int:pk>/delete/', views.template_delete, name='template_delete'),

    # Campaigns
    path('campaigns/', views.campaign_list, name='campaign_list'),
    path('campaigns/create/', views.campaign_create, name='campaign_create'),
    path('campaigns/ab-test/create/', views.campaign_ab_test_create, name='campaign_ab_test_create'),
    path('campaigns/<int:pk>/', views.campaign_detail, name='campaign_detail'),
    path('campaigns/<int:pk>/edit/', views.campaign_edit, name='campaign_edit'),
    path('campaigns/<int:pk>/send/', views.campaign_send, name='campaign_send'),
    path('campaigns/<int:pk>/delete/', views.campaign_delete, name='campaign_delete'),
    path('campaigns/<int:pk>/analytics/', views.campaign_analytics, name='campaign_analytics'),

    # A/B Testing
    path('campaigns/<int:pk>/ab-test-winner/', views.ab_test_winner, name='ab_test_winner'),
]
