from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('signup/', views.SignupUserView.as_view(), name='signup'),
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('logout/', views.LogoutUserView.as_view(), name='logout'),

    # Incidents
    path('', views.IncidentListView.as_view(), name='incident_list'),
    path('report/', views.CreateIncidentView.as_view(), name='create_incident'),
    path('incident/<int:pk>/', views.IncidentDetailView.as_view(), name='incident_detail'),
    path('incident/<int:pk>/comment/', views.AddCommentView.as_view(), name='add_comment'),
    path('incident/<int:pk>/verify/', views.VerifyIncidentView.as_view(), name='verify_incident'),

    # Comments
    path('comment/<int:pk>/like/', views.ToggleCommentLikeView.as_view(), name='toggle_comment_like'),

    # User Profiles
    path('profile/', views.MyProfileView.as_view(), name='my_profile'),
    path('profile/edit/', views.EditProfileView.as_view(), name='edit_profile'),
    path('user/<int:pk>/', views.UserProfileView.as_view(), name='user_profile'),

    # Notifications
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notification/<int:pk>/read/', views.MarkNotificationReadView.as_view(), name='mark_notification_read'),
    path('notifications/read-all/', views.MarkAllNotificationsReadView.as_view(), name='mark_all_read'),

    # Admin Dashboard
    path('dashboard/admin/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('dashboard/admin/incidents/', views.AdminIncidentListView.as_view(), name='admin_incidents'),
    path('dashboard/admin/incident/<int:pk>/status/', views.UpdateIncidentStatusView.as_view(), name='update_incident_status'),

    # Safety Alerts
    path('alerts/', views.SafetyAlertListView.as_view(), name='safety_alerts'),
    path('alerts/create/', views.CreateSafetyAlertView.as_view(), name='create_safety_alert'),
]
