from django.contrib import admin
from .models import Channel, Video, Playlist, Comment, Like, Subscription, ViewHistory

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'subscriber_count', 'video_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'owner__username']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'channel', 'status', 'view_count', 'like_count', 'created_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'description', 'tags']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['name', 'channel', 'video_count', 'is_public']
    list_filter = ['is_public', 'channel']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'video', 'content', 'like_count', 'created_at']
    list_filter = ['created_at', 'is_approved']
    search_fields = ['content']

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'video', 'like_type', 'created_at']

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['subscriber', 'channel', 'created_at']

@admin.register(ViewHistory)
class ViewHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'video', 'watch_duration', 'completed', 'last_watched_at']
    list_filter = ['completed', 'last_watched_at']
