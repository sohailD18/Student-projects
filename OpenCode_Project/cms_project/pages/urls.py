from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.PageListView.as_view(), name='page_list'),
    path('page/<slug:slug>/', views.PageDetailView.as_view(), name='page_detail'),
    path('create/', views.PageCreateView.as_view(), name='page_create'),
    path('update/<slug:slug>/', views.PageUpdateView.as_view(), name='page_update'),
    path('delete/<slug:slug>/', views.PageDeleteView.as_view(), name='page_delete'),
    path('builder/<slug:slug>/', views.page_builder, name='page_builder'),
    path('revisions/<slug:slug>/', views.page_revisions, name='page_revisions'),
]
