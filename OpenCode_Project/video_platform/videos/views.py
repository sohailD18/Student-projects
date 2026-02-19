from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.edit import FormView
from django.http import JsonResponse
from django.db.models import Q, Count
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from .models import Video, Channel, Playlist, Comment, Like, Subscription, ViewHistory
from .forms import VideoUploadForm, ChannelCreateForm, CommentForm

def home(request):
    videos = Video.objects.filter(status='PUBLISHED').select_related('channel').prefetch_related('likes')
    featured_videos = Video.objects.filter(status='PUBLISHED', is_featured=True).select_related('channel')[:4]
    trending_videos = Video.objects.filter(status='PUBLISHED').order_by('-view_count').select_related('channel')[:8]
    channels = Channel.objects.annotate(channel_video_count=Count('videos')).order_by('-subscriber_count')[:6]
    
    return render(request, 'videos/home.html', {
        'videos': videos[:12],
        'featured_videos': featured_videos,
        'trending_videos': trending_videos,
        'channels': channels,
    })

class VideoListView(ListView):
    model = Video
    template_name = 'videos/video_list.html'
    context_object_name = 'videos'
    paginate_by = 20
    
    def get_queryset(self):
        videos = Video.objects.filter(status='PUBLISHED').select_related('channel')
        
        search = self.request.GET.get('q')
        if search:
            videos = videos.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__icontains=search)
            )
        
        category = self.request.GET.get('category')
        if category:
            videos = videos.filter(category__iexact=category)
        
        sort = self.request.GET.get('sort')
        if sort == 'popular':
            videos = videos.order_by('-view_count')
        elif sort == 'new':
            videos = videos.order_by('-created_at')
        
        return videos

class VideoDetailView(DetailView):
    model = Video
    template_name = 'videos/video_detail.html'
    context_object_name = 'video'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if self.request.user.is_authenticated:
            ViewHistory.objects.update_or_create(
                user=self.request.user,
                video=obj,
                defaults={'last_watched_at': timezone.now()}
            )
            obj.increment_views()
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments_query = self.object.comments.filter(
            parent__isnull=True,
            is_approved=True
        ).select_related('user')
        context['comments'] = list(comments_query)[:20]
        suggested_videos_query = Video.objects.filter(
            status='PUBLISHED',
            category=self.object.category
        ).exclude(id=self.object.id)
        context['suggested_videos'] = list(suggested_videos_query)[:8]
        return context

class ChannelDetailView(DetailView):
    model = Channel
    template_name = 'videos/channel_detail.html'
    context_object_name = 'channel'
    slug_url_kwarg = 'channel_slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['videos'] = self.object.videos.filter(status='PUBLISHED')[:12]
        context['playlists'] = self.object.playlists.filter(is_public=True).prefetch_related('videos')
        
        is_subscribed = False
        if self.request.user.is_authenticated:
            is_subscribed = Subscription.objects.filter(
                subscriber=self.request.user,
                channel=self.object
            ).exists()
        context['is_subscribed'] = is_subscribed
        
        return context

class PlaylistDetailView(DetailView):
    model = Playlist
    template_name = 'videos/playlist_detail.html'
    context_object_name = 'playlist'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        videos = self.object.videos.filter(status='PUBLISHED').select_related('channel')
        context['videos'] = videos
        context['actual_video_count'] = videos.count()
        return context

@login_required
def upload_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.channel = request.user.channels.first()
            if not video.channel:
                channel = Channel.objects.create(
                    name=f"{request.user.username}'s Channel",
                    slug=f"{request.user.username}-channel",
                    owner=request.user
                )
                video.channel = channel
            video.save()
            return redirect('video_detail', slug=video.slug)
    else:
        form = VideoUploadForm()
    
    return render(request, 'videos/upload.html', {'form': form})

@login_required
def like_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    like_type = request.POST.get('like_type', 'LIKE')
    
    like, created = Like.objects.get_or_create(
        user=request.user,
        video=video,
        defaults={'like_type': like_type}
    )
    
    if not created:
        like.delete()
        if like_type == 'LIKE':
            video.like_count = max(0, video.like_count - 1)
        else:
            video.dislike_count = max(0, video.dislike_count - 1)
        video.save(update_fields=['like_count', 'dislike_count'])
        return JsonResponse({'liked': False, 'like_count': video.like_count, 'dislike_count': video.dislike_count})
    else:
        if like_type == 'LIKE':
            video.like_count += 1
        else:
            video.dislike_count += 1
        video.save(update_fields=['like_count', 'dislike_count'])
        return JsonResponse({'liked': True, 'like_type': like_type, 'like_count': video.like_count, 'dislike_count': video.dislike_count})

@login_required
def add_comment(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.video = video
            comment.user = request.user
            comment.save()
            video.comment_count += 1
            video.save(update_fields=['comment_count'])
            return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@login_required
def subscribe_channel(request, channel_id):
    channel = get_object_or_404(Channel, id=channel_id)
    subscription, created = Subscription.objects.get_or_create(
        subscriber=request.user,
        channel=channel
    )
    
    if not created:
        subscription.delete()
        channel.subscriber_count -= 1
        return JsonResponse({'subscribed': False, 'subscriber_count': channel.subscriber_count})
    
    channel.subscriber_count += 1
    channel.save(update_fields=['subscriber_count'])
    return JsonResponse({'subscribed': True, 'subscriber_count': channel.subscriber_count})

@login_required
def view_history(request):
    history = ViewHistory.objects.filter(
        user=request.user
    ).select_related('video', 'video__channel')[:50]
    
    return render(request, 'videos/view_history.html', {'history': history})

def search_videos(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category')
    
    videos = Video.objects.filter(status='PUBLISHED').filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(tags__icontains=query)
    )
    
    if category:
        videos = videos.filter(category__iexact=category)
    
    videos = videos.select_related('channel')[:50]
    
    return render(request, 'videos/search.html', {'videos': videos, 'query': query})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    
    return render(request, 'videos/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def register_view(request):
    from django.contrib.auth.models import User
    from .forms import UserCreationForm
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'videos/register.html', {'form': form})
