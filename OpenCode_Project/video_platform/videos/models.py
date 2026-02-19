from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Channel(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='channels')
    banner_image = models.ImageField(upload_to='channel_banners/', blank=True, null=True)
    profile_image = models.ImageField(upload_to='channel_profiles/', blank=True, null=True)
    subscriber_count = models.PositiveIntegerField(default=0)
    video_count = models.PositiveIntegerField(default=0)
    total_views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    @property
    def total_videos(self):
        return self.videos.count()

class Video(models.Model):
    STATUS_CHOICES = [
        ('PROCESSING', 'Processing'), ('READY', 'Ready'),
        ('PUBLISHED', 'Published'), ('PRIVATE', 'Private'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='videos')
    video_file = models.FileField(upload_to='videos/')
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PROCESSING')
    duration = models.PositiveIntegerField(help_text='Duration in seconds', default=0)
    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    dislike_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=50, blank=True)
    tags = models.TextField(blank=True, help_text='Comma-separated tags')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def formatted_duration(self):
        hours = self.duration // 3600
        minutes = (self.duration % 3600) // 60
        seconds = self.duration % 60
        
        if hours:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"
    
    def increment_views(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])

class Playlist(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='playlists')
    videos = models.ManyToManyField(Video, related_name='playlists', blank=True)
    thumbnail = models.ImageField(upload_to='playlist_thumbnails/', blank=True, null=True)
    video_count = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.channel.name}"

class Comment(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_comments')
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    like_count = models.PositiveIntegerField(default=0)
    dislike_count = models.PositiveIntegerField(default=0)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.video.title}"

class Like(models.Model):
    LIKE_CHOICES = [
        ('LIKE', 'Like'), ('DISLIKE', 'Dislike'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_likes')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='likes')
    like_type = models.CharField(max_length=10, choices=LIKE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'video']
    
    def __str__(self):
        return f"{self.user.username} {self.like_type}d {self.video.title}"

class Subscription(models.Model):
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='subscribers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['subscriber', 'channel']
    
    def __str__(self):
        return f"{self.subscriber.username} subscribed to {self.channel.name}"

class ViewHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='view_history')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='view_histories')
    watch_duration = models.PositiveIntegerField(default=0, help_text='Seconds watched')
    completed = models.BooleanField(default=False)
    last_watched_at = models.DateTimeField(auto_now=True)
    first_watched_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-last_watched_at']
        unique_together = ['user', 'video']
    
    def __str__(self):
        return f"{self.user.username} watched {self.video.title}"
