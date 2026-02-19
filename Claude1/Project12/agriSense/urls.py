from django.urls import path
from . import views

app_name = 'agriSense'

urlpatterns = [
    # Main Pages
    path('', views.dashboard_home, name='dashboard'),
    path('planner/', views.crop_planner, name='crop_planner'),
    path('yield/', views.yield_predictor, name='yield_predictor'),
    path('reports/', views.analytics_reports, name='reports'),

    # API Endpoints
    path('api/yield-prediction/', views.yield_prediction, name='yield_prediction'),
    path('api/recommendations/', views.crop_recommendations, name='crop_recommendations'),
    path('api/yield-analysis/', views.yield_analysis, name='yield_analysis'),
    path('api/top-crops/', views.top_crops, name='top_crops'),
    path('api/pest-risk/', views.pest_risk_assessment, name='pest_risk_assessment'),
    path('api/fertilizer-recommendation/', views.fertilizer_recommendation, name='fertilizer_recommendation'),
    path('api/yield-chart-data/', views.yield_chart_data, name='yield_chart_data'),
]
