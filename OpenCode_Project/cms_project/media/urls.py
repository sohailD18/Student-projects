from django.urls import path
from . import views

app_name = 'media'

urlpatterns = [
    path('', views.MediaListView.as_view(), name='media_list'),
    path('upload/', views.MediaUploadView.as_view(), name='media_upload'),
    path('folder/<int:pk>/', views.MediaFolderView.as_view(), name='media_folder'),
    path('file/<int:pk>/', views.MediaDetailView.as_view(), name='media_detail'),
    path('edit/<int:pk>/', views.MediaUpdateView.as_view(), name='media_edit'),
    path('delete/<int:pk>/', views.MediaDeleteView.as_view(), name='media_delete'),
    path('collections/', views.MediaCollectionListView.as_view(), name='collection_list'),
    path('collections/create/', views.MediaCollectionCreateView.as_view(), name='collection_create'),
]
