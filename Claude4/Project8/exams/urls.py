"""
URL configuration for Exams App
"""
from django.urls import path
from . import views

urlpatterns = [
    # Public URLs
    path('', views.ExamListView.as_view(), name='exam_list'),
    path('exam/<int:pk>/', views.ExamDetailView.as_view(), name='exam_detail'),

    # Management URLs (staff only)
    path('manage/', views.ManagementDashboardView.as_view(), name='management_dashboard'),

    # Category CRUD
    path('manage/categories/', views.CategoryListView.as_view(), name='category_list'),
    path('manage/categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('manage/categories/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('manage/categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    # Exam CRUD
    path('manage/create/', views.ExamCreateView.as_view(), name='exam_create'),
    path('manage/exam/<int:pk>/update/', views.ExamUpdateView.as_view(), name='exam_update'),
    path('manage/exam/<int:pk>/delete/', views.ExamDeleteView.as_view(), name='exam_delete'),
]
