from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Authentication
    path('signup/', views.signup, name='signup'),

    # Dashboards
    path('dashboards/', views.dashboard_list, name='dashboard_list'),
    path('dashboards/create/', views.dashboard_create, name='dashboard_create'),
    path('dashboards/<int:dashboard_id>/', views.dashboard_detail, name='dashboard_detail'),

    # Metrics
    path('metrics/', views.metric_list, name='metric_list'),
    path('metrics/create/', views.metric_create, name='metric_create'),
    path('metrics/<int:metric_id>/', views.metric_detail, name='metric_detail'),
    path('metrics/<int:metric_id>/add-data/', views.add_metric_data, name='add_metric_data'),

    # Data Sources
    path('data-sources/', views.data_source_list, name='data_source_list'),
    path('data-sources/create/', views.data_source_create, name='data_source_create'),

    # Alerts
    path('alerts/', views.alert_list, name='alert_list'),
    path('alerts/create/', views.alert_create, name='alert_create'),
    path('alerts/logs/', views.alert_logs, name='alert_logs'),
    path('alerts/logs/<int:log_id>/acknowledge/', views.acknowledge_alert, name='acknowledge_alert'),

    # Reports
    path('reports/', views.report_list, name='report_list'),

    # API endpoints
    path('api/widget/<int:widget_id>/data/', views.widget_data_api, name='widget_data_api'),
]
