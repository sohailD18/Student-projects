from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import views as auth_views
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q, Count, Sum, F
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.core.paginator import Paginator

from .models import (
    Incident, Comment, UserProfile, IncidentCategory,
    IncidentVerification, Notification, SafetyAlert, CommentLike
)
from .forms import (
    IncidentForm, CommentForm, CustomSignupForm, UserProfileForm,
    IncidentSearchForm, IncidentVerificationForm, IncidentCategoryForm, SafetyAlertForm
)


# ==================== Incident Views ====================

class IncidentListView(ListView):
    model = Incident
    template_name = 'core/incident_list.html'
    context_object_name = 'incidents'
    paginate_by = 12

    def get_queryset(self):
        queryset = Incident.objects.select_related('user', 'category', 'verified_by').prefetch_related('comments')

        # Get search parameters
        search = self.request.GET.get('search')
        category = self.request.GET.get('category')
        status = self.request.GET.get('status')
        severity = self.request.GET.get('severity')
        location = self.request.GET.get('location')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')

        # Apply filters
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location__icontains=search)
            )

        if category:
            queryset = queryset.filter(category_id=category)

        if status:
            queryset = queryset.filter(status=status)

        if severity:
            queryset = queryset.filter(severity=severity)

        if location:
            queryset = queryset.filter(location__icontains=location)

        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)

        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = IncidentSearchForm(self.request.GET)
        context['categories'] = IncidentCategory.objects.all()

        # Get active safety alerts
        context['safety_alerts'] = SafetyAlert.objects.filter(
            is_active=True
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        )

        return context


class CreateIncidentView(LoginRequiredMixin, CreateView):
    model = Incident
    form_class = IncidentForm
    template_name = 'core/create_incident.html'
    success_url = reverse_lazy('incident_list')

    def form_valid(self, form):
        incident = form.save(commit=False)
        incident.user = self.request.user
        incident.save()

        # Create notifications for nearby users
        nearby_users = incident.get_nearby_users(radius_km=10)
        for user in nearby_users:
            if user != self.request.user:
                Notification.objects.create(
                    recipient=user,
                    notification_type='new_incident',
                    title=f'New Incident Nearby: {incident.title}',
                    message=f'A new {incident.get_severity_display()} severity incident has been reported near your location: {incident.location}',
                    incident=incident
                )

        messages.success(self.request, 'Incident reported successfully! Nearby users have been notified.')
        return super().form_valid(form)


class IncidentDetailView(DetailView):
    model = Incident
    template_name = 'core/incident_detail.html'
    context_object_name = 'incident'

    def get_object(self):
        obj = super().get_object()
        # Increment view count
        obj.view_count += 1
        obj.save(update_fields=['view_count'])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        incident = self.object

        # Get comments with replies
        context['comments'] = incident.comments.filter(parent=None).prefetch_related('replies', 'likes')
        context['comment_form'] = CommentForm()

        # Check if user has verified
        if self.request.user.is_authenticated:
            context['user_verification'] = IncidentVerification.objects.filter(
                incident=incident, user=self.request.user
            ).first()
        else:
            context['user_verification'] = None

        # Get verification count
        context['verification_count'] = incident.verifications.count()
        context['confirm_count'] = incident.verifications.filter(is_confirmed=True).count()
        context['false_report_count'] = incident.verifications.filter(is_confirmed=False).count()

        return context


# ==================== Comment Views ====================

class AddCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'core/incident_detail.html'

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.user = self.request.user
        comment.incident_id = self.kwargs['pk']

        # Check if it's a reply
        parent_id = self.request.POST.get('parent_id')
        if parent_id:
            comment.parent_id = parent_id

        comment.save()

        # Notify incident reporter about new comment
        if comment.incident.user != self.request.user:
            Notification.objects.create(
                recipient=comment.incident.user,
                notification_type='new_comment',
                title=f'New Comment on Your Report',
                message=f'{self.request.user.username} commented on your incident: {comment.incident.title}',
                incident=comment.incident
            )

        messages.success(self.request, 'Comment added successfully!')
        return redirect('incident_detail', pk=comment.incident.pk)


class ToggleCommentLikeView(LoginRequiredMixin, CreateView):
    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        like, created = CommentLike.objects.get_or_create(
            comment=comment, user=request.user
        )

        if not created:
            # Unlike if already liked
            like.delete()
            comment.likes_count -= 1
            comment.save()
            return JsonResponse({'liked': False, 'likes_count': comment.likes_count})
        else:
            comment.likes_count += 1
            comment.save()

            # Notify comment author about like
            if comment.user != request.user:
                Notification.objects.create(
                    recipient=comment.user,
                    notification_type='comment_reply',
                    title='Your Comment Was Liked',
                    message=f'{request.user.username} liked your comment on {comment.incident.title}',
                    incident=comment.incident
                )

            return JsonResponse({'liked': True, 'likes_count': comment.likes_count})


# ==================== Verification Views ====================

class VerifyIncidentView(LoginRequiredMixin, CreateView):
    model = IncidentVerification
    form_class = IncidentVerificationForm
    template_name = 'core/incident_detail.html'

    def post(self, request, pk):
        incident = get_object_or_404(Incident, pk=pk)

        # Check if user already verified
        existing = IncidentVerification.objects.filter(
            incident=incident, user=request.user
        ).first()

        if existing:
            messages.warning(request, 'You have already verified this incident.')
            return redirect('incident_detail', pk=pk)

        form = self.form_class(request.POST)
        if form.is_valid():
            verification = form.save(commit=False)
            verification.incident = incident
            verification.user = request.user
            verification.save()

            # Update incident verification status
            incident.increment_verification()

            messages.success(request, 'Thank you for verifying this incident!')
        else:
            messages.error(request, 'Error submitting verification. Please try again.')

        return redirect('incident_detail', pk=pk)


# ==================== User Profile Views ====================

class UserProfileView(DetailView):
    model = User
    template_name = 'core/profile.html'
    context_object_name = 'profile_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object

        # Get or create profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        context['user_profile'] = profile

        # Get user's incidents
        context['user_incidents'] = Incident.objects.filter(user=user).select_related('category')[:10]

        # Get user's comments
        context['user_comments'] = Comment.objects.filter(user=user).select_related('incident')[:10]

        # Calculate stats
        context['incident_count'] = Incident.objects.filter(user=user).count()
        context['verified_incident_count'] = Incident.objects.filter(user=user, is_verified=True).count()
        context['comment_count'] = Comment.objects.filter(user=user).count()

        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'core/edit_profile.html'
    success_url = reverse_lazy('my_profile')

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)


class MyProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'core/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user'] = self.request.user

        # Get or create profile
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        context['user_profile'] = profile

        # Get user's incidents
        context['user_incidents'] = Incident.objects.filter(user=self.request.user).select_related('category')[:10]

        # Get user's comments
        context['user_comments'] = Comment.objects.filter(user=self.request.user).select_related('incident')[:10]

        # Calculate stats
        context['incident_count'] = Incident.objects.filter(user=self.request.user).count()
        context['verified_incident_count'] = Incident.objects.filter(user=self.request.user, is_verified=True).count()
        context['comment_count'] = Comment.objects.filter(user=self.request.user).count()

        return context


# ==================== Notification Views ====================

class NotificationListView(LoginRequiredMixin, TemplateView):
    template_name = 'core/notifications.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifications'] = Notification.objects.filter(
            recipient=self.request.user
        ).select_related('incident').order_by('-created_at')

        # Get unread count
        context['unread_count'] = context['notifications'].filter(is_read=False).count()

        return context


class MarkNotificationReadView(LoginRequiredMixin, CreateView):
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.mark_as_read()
        return JsonResponse({'success': True})


class MarkAllNotificationsReadView(LoginRequiredMixin, TemplateView):
    def post(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
        return redirect('notifications')


# ==================== Admin Dashboard Views ====================

class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'core/admin_dashboard.html'

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get statistics
        context['total_incidents'] = Incident.objects.count()
        context['pending_incidents'] = Incident.objects.filter(status='pending').count()
        context['verified_incidents'] = Incident.objects.filter(is_verified=True).count()
        context['resolved_incidents'] = Incident.objects.filter(status='resolved').count()

        # Get severity breakdown
        context['critical_incidents'] = Incident.objects.filter(severity='critical').count()
        context['high_incidents'] = Incident.objects.filter(severity='high').count()
        context['medium_incidents'] = Incident.objects.filter(severity='medium').count()
        context['low_incidents'] = Incident.objects.filter(severity='low').count()

        # Get user stats
        context['total_users'] = UserProfile.objects.count()
        context['active_users_today'] = UserProfile.objects.filter(
            last_activity__date=timezone.now().date()
        ).count()

        # Get recent incidents
        context['recent_incidents'] = Incident.objects.select_related('user', 'category').order_by('-created_at')[:10]

        # Get top contributors
        context['top_contributors'] = UserProfile.objects.annotate(
            incident_count=Count('user__incidents')
        ).order_by('-incident_count')[:10]

        # Get incidents by category
        context['categories'] = IncidentCategory.objects.annotate(
            incident_count=Count('incidents')
        ).order_by('-incident_count')

        # Get unread notifications count
        context['unread_notifications'] = Notification.objects.filter(
            recipient=self.request.user, is_read=False
        ).count()

        return context


class AdminIncidentListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Incident
    template_name = 'core/admin_incidents.html'
    context_object_name = 'incidents'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_queryset(self):
        return Incident.objects.select_related('user', 'category').order_by('-created_at')


class UpdateIncidentStatusView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Incident
    fields = ['status']
    template_name = 'core/update_incident_status.html'
    success_url = reverse_lazy('admin_incidents')

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def form_valid(self, form):
        incident = form.save(commit=False)
        old_status = Incident.objects.get(pk=incident.pk).status
        incident.save()

        # Notify incident reporter about status update
        if old_status != incident.status:
            Notification.objects.create(
                recipient=incident.user,
                notification_type='incident_updated',
                title='Incident Status Updated',
                message=f'Your incident "{incident.title}" status has been updated to {incident.get_status_display()}',
                incident=incident
            )

        messages.success(self.request, f'Incident status updated to {incident.get_status_display()}')
        return super().form_valid(form)


# ==================== Safety Alert Views ====================

class SafetyAlertListView(ListView):
    model = SafetyAlert
    template_name = 'core/safety_alerts.html'
    context_object_name = 'alerts'

    def get_queryset(self):
        return SafetyAlert.objects.filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now()),
            is_active=True
        ).select_related('created_by').order_by('-created_at')


class CreateSafetyAlertView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = SafetyAlert
    form_class = SafetyAlertForm
    template_name = 'core/create_safety_alert.html'
    success_url = reverse_lazy('safety_alerts')

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def form_valid(self, form):
        alert = form.save(commit=False)
        alert.created_by = self.request.user
        alert.save()

        # Create notifications for all users with notifications enabled
        users_to_notify = UserProfile.objects.filter(notification_enabled=True)
        for profile in users_to_notify:
            Notification.objects.create(
                recipient=profile.user,
                notification_type='alert',
                title=alert.title,
                message=alert.message
            )

        messages.success(self.request, 'Safety alert created and notifications sent!')
        return super().form_valid(form)


# ==================== Authentication Views ====================

class SignupUserView(CreateView):
    form_class = CustomSignupForm
    template_name = 'core/signup.html'
    success_url = reverse_lazy('incident_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Account created successfully! Welcome to UrbanSafe.')
        return response


class LoginUserView(auth_views.LoginView):
    template_name = 'core/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        # Call parent first to actually log the user in
        response = super().form_valid(form)

        user = form.get_user()
        messages.success(self.request, f'Welcome back, {user.username}!')

        # Redirect admin/superuser to Django admin panel
        if user.is_staff or user.is_superuser:
            from django.shortcuts import redirect
            return redirect('/admin/')

        return response


class LogoutUserView(auth_views.LogoutView):
    next_page = 'incident_list'

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'Goodbye! See you again soon. Stay safe! 👋')
        response = super().dispatch(request, *args, **kwargs)
        return response
