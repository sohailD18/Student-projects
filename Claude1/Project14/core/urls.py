from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('upload/', views.upload_view, name='upload'),
    path('detail/<int:document_id>/', views.detail_view, name='detail'),
    path('compare/', views.comparison_view, name='compare'),
]
