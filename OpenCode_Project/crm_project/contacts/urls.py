"""
URL configuration for contacts app
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    path('contacts/', views.ContactListView.as_view(), name='contact_list'),
    path('contacts/new/', views.ContactCreateView.as_view(), name='contact_create'),
    path('contacts/<int:pk>/', views.ContactDetailView.as_view(), name='contact_detail'),
    path('contacts/<int:pk>/edit/', views.ContactUpdateView.as_view(), name='contact_update'),
    path('contacts/<int:pk>/delete/', views.ContactDeleteView.as_view(), name='contact_delete'),
    path('contacts/<int:contact_id>/update-last-contacted/', views.update_last_contacted, name='update_last_contacted'),
    
    path('companies/', views.CompanyListView.as_view(), name='company_list'),
    path('companies/new/', views.CompanyCreateView.as_view(), name='company_create'),
    path('companies/<int:pk>/', views.CompanyDetailView.as_view(), name='company_detail'),
    path('companies/<int:pk>/edit/', views.CompanyUpdateView.as_view(), name='company_update'),
    path('companies/<int:pk>/delete/', views.CompanyDeleteView.as_view(), name='company_delete'),
]
