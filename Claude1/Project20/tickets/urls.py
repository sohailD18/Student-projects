from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    # Home page - displays welcome and ticket search
    path('', views.home, name='home'),

    # Submit complaint form
    path('submit/', views.submit_complaint, name='submit'),

    # Success page after complaint submission
    path('success/<str:ticket_id>/', views.success, name='success'),

    # Staff dashboard - view and manage tickets
    path('dashboard/', views.dashboard, name='dashboard'),

    # Update ticket status and assignment
    path('ticket/<str:ticket_id>/update/', views.update_ticket, name='update_ticket'),

    # Escalate a ticket
    path('ticket/<str:ticket_id>/escalate/', views.escalate_ticket, name='escalate_ticket'),

    # Submit feedback for a ticket
    path('feedback/', views.feedback, name='feedback'),
    path('feedback/<str:ticket_id>/', views.feedback, name='feedback_with_ticket'),

    # Analytics dashboard
    path('analytics/', views.analytics, name='analytics'),
]
