"""
URL configuration for the documents app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    index_view, CategoryViewSet, DocumentViewSet, SearchViewSet,
    DashboardAPIView, AnalyticsAPIView, ReportAPIView
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'search', SearchViewSet, basename='search')

urlpatterns = [
    # Serve the main frontend application
    path('', index_view, name='index'),

    # API endpoints from ViewSets
    path('api/', include(router.urls)),

    # Additional API endpoints
    path('api/dashboard/', DashboardAPIView.as_view(), name='dashboard'),
    path('api/analytics/', AnalyticsAPIView.as_view(), name='analytics'),
    path('api/reports/', ReportAPIView.as_view(), name='reports'),
]
