from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('videos/', views.VideoListView.as_view(), name='video_list'),
    path('video/<slug:slug>/', views.VideoDetailView.as_view(), name='video_detail'),
    path('channel/<slug:channel_slug>/', views.ChannelDetailView.as_view(), name='channel_detail'),
    path('playlist/<int:pk>/', views.PlaylistDetailView.as_view(), name='playlist_detail'),
    path('upload/', views.upload_video, name='upload_video'),
    path('video/<int:video_id>/like/', views.like_video, name='like_video'),
    path('video/<int:video_id>/comment/', views.add_comment, name='add_comment'),
    path('channel/<int:channel_id>/subscribe/', views.subscribe_channel, name='subscribe_channel'),
    path('history/', views.view_history, name='view_history'),
    path('search/', views.search_videos, name='search_videos'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
]
