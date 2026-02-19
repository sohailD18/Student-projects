"""
URL configuration for performance app
"""
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),

    # Employee management
    path('employees/', views.employee_list_view, name='employee_list'),
    path('employees/add/', views.add_employee_view, name='add_employee'),
    path('employees/<int:employee_id>/', views.employee_detail_view, name='employee_detail'),
    path('employees/<int:employee_id>/report/', views.print_report_view, name='print_report'),

    # Performance records
    path('records/add/', views.add_record_view, name='add_record'),
    path('records/<int:record_id>/edit/', views.edit_record_view, name='edit_record'),
    path('records/<int:record_id>/delete/', views.delete_record_view, name='delete_record'),
]
