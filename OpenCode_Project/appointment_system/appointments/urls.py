from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('services/', views.ServiceListView.as_view(), name='service_list'),
    path('providers/', views.ProviderListView.as_view(), name='provider_list'),
    path('provider/<int:pk>/', views.ProviderDetailView.as_view(), name='provider_detail'),
    path('provider/<int:provider_id>/slots/<str:date>/', views.get_available_slots, name='available_slots'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('appointment/<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('booking/<int:booking_id>/confirmation/', views.booking_confirmation, name='booking_confirmation'),
    path('provider/dashboard/', views.provider_dashboard, name='provider_dashboard'),
    path('appointment/<int:appointment_id>/update/', views.update_appointment_status, name='update_appointment'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
]
