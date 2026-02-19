from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.db.models import Sum, Count, Avg
from django.urls import path
from django.shortcuts import render
from django.http import HttpResponseRedirect

from .models import (
    ActivityLog, UserProfile, Badge, UserBadge,
    Challenge, ChallengeParticipant, UserGoal, Achievement, UserAchievement
)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'activity_subtype', 'value', 'calculated_carbon', 'date', 'created_at']
    list_filter = ['activity_type', 'activity_subtype', 'date', 'created_at']
    search_fields = ['user__username', 'notes']
    readonly_fields = ['calculated_carbon', 'created_at']
    date_hierarchy = 'date'

    fieldsets = (
        ('Activity Information', {
            'fields': ('user', 'activity_type', 'activity_subtype', 'value', 'date')
        }),
        ('Calculated Data', {
            'fields': ('calculated_carbon', 'notes'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_points', 'streak_days', 'longest_streak', 'location', 'last_activity_date']
    list_filter = ['streak_days', 'location', 'created_at']
    search_fields = ['user__username', 'bio', 'location']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'bio', 'location', 'avatar_url')
        }),
        ('Statistics', {
            'fields': ('total_points', 'streak_days', 'longest_streak', 'last_activity_date')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ['total_points', 'streak_days', 'longest_streak', 'bio', 'location']


class UserBadgeInline(admin.TabularInline):
    model = UserBadge
    extra = 0
    readonly_fields = ['date_earned']
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline, UserBadgeInline]
    list_display = ['username', 'email', 'get_points', 'get_streak', 'is_staff', 'date_joined']
    list_filter = BaseUserAdmin.list_filter + ('profile__streak_days',)

    def get_points(self, obj):
        return obj.profile.total_points
    get_points.short_description = 'Points'
    get_points.admin_order_field = 'profile__total_points'

    def get_streak(self, obj):
        return obj.profile.streak_days
    get_streak.short_description = 'Streak'
    get_streak.admin_order_field = 'profile__streak_days'


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'category', 'rarity', 'points_required', 'streak_required', 'activities_required', 'times_earned']
    list_filter = ['category', 'rarity']
    search_fields = ['name', 'description']
    readonly_fields = ['times_earned', 'created_at']

    fieldsets = (
        ('Badge Information', {
            'fields': ('name', 'description', 'icon', 'category', 'rarity')
        }),
        ('Requirements', {
            'fields': ('points_required', 'streak_required', 'activities_required')
        }),
        ('Statistics', {
            'fields': ('times_earned',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def times_earned(self, obj):
        return obj.earned_by.count()
    times_earned.short_description = 'Times Earned'


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge', 'date_earned', 'badge_rarity']
    list_filter = ['badge__category', 'badge__rarity', 'date_earned']
    search_fields = ['user__username', 'badge__name']
    readonly_fields = ['date_earned']

    def badge_rarity(self, obj):
        colors = {
            'common': '#6c757d',
            'rare': '#3498db',
            'epic': '#9b59b6',
            'legendary': '#f39c12'
        }
        color = colors.get(obj.badge.rarity, '#6c757d')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.badge.get_rarity_display())
    badge_rarity.short_description = 'Rarity'


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date', 'target_points', 'reward_points', 'status', 'participant_count', 'completion_rate']
    list_filter = ['status', 'start_date', 'end_date']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Challenge Information', {
            'fields': ('title', 'description', 'status')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Requirements & Rewards', {
            'fields': ('target_points', 'reward_points', 'badge', 'max_participants')
        }),
        ('Statistics', {
            'fields': ('participant_count', 'completion_rate'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def participant_count(self, obj):
        return obj.participant_count
    participant_count.short_description = 'Participants'

    def completion_rate(self, obj):
        total = obj.participant_count
        if total == 0:
            return "0%"
        completed = obj.participants.filter(status='completed').count()
        rate = (completed / total) * 100
        return f"{rate:.1f}%"
    completion_rate.short_description = 'Completion Rate'


@admin.register(ChallengeParticipant)
class ChallengeParticipantAdmin(admin.ModelAdmin):
    list_display = ['user', 'challenge', 'points_earned', 'progress_display', 'status', 'joined_at']
    list_filter = ['status', 'joined_at', 'challenge']
    search_fields = ['user__username', 'challenge__title']
    readonly_fields = ['joined_at', 'completed_at', 'progress_bar']

    def progress_display(self, obj):
        percentage = obj.progress_percentage
        color = '#28a745' if percentage == 100 else '#ffc107' if percentage >= 50 else '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color, percentage
        )
    progress_display.short_description = 'Progress'

    def progress_bar(self, obj):
        percentage = obj.progress_percentage
        color = '#28a745' if percentage == 100 else '#ffc107' if percentage >= 50 else '#dc3545'
        bar_html = f'''
        <div style="width: 100%; background: #e9ecef; border-radius: 10px; overflow: hidden; height: 25px;">
            <div style="width: {percentage}%; background: {color}; height: 100%; display: flex; align-items: center; justify-content: center; color: white; font-size: 12px; font-weight: bold;">
                {obj.points_earned:.0f} / {obj.challenge.target_points}
            </div>
        </div>
        '''
        return format_html(bar_html)
    progress_bar.short_description = 'Progress Bar'


@admin.register(UserGoal)
class UserGoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'goal_type', 'progress_display', 'status', 'start_date', 'end_date']
    list_filter = ['goal_type', 'status', 'period', 'start_date']
    search_fields = ['user__username', 'title', 'description']
    readonly_fields = ['created_at', 'updated_at', 'progress_bar']

    def progress_display(self, obj):
        percentage = obj.progress_percentage
        color = '#28a745' if percentage == 100 else '#ffc107' if percentage >= 50 else '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color, percentage
        )
    progress_display.short_description = 'Progress'

    def progress_bar(self, obj):
        percentage = obj.progress_percentage
        color = '#28a745' if percentage == 100 else '#ffc107' if percentage >= 50 else '#dc3545'
        bar_html = f'''
        <div style="width: 100%; background: #e9ecef; border-radius: 10px; overflow: hidden; height: 25px;">
            <div style="width: {percentage}%; background: {color}; height: 100%; display: flex; align-items: center; justify-content: center; color: white; font-size: 12px; font-weight: bold;">
                {obj.current_value:.1f} / {obj.target_value:.1f}
            </div>
        </div>
        '''
        return format_html(bar_html)
    progress_bar.short_description = 'Progress'


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['title', 'icon', 'points_reward', 'times_earned', 'is_hidden']
    list_filter = ['is_hidden', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['times_earned', 'created_at']

    def times_earned(self, obj):
        return obj.earned_by.count()
    times_earned.short_description = 'Times Earned'


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'achievement', 'earned_at']
    list_filter = ['earned_at', 'achievement__is_hidden']
    search_fields = ['user__username', 'achievement__title']
    readonly_fields = ['earned_at']


# Unregister default User admin and register custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# Customize default admin site
admin.site.site_header = '🌱 EcoTrack Administration'
admin.site.site_title = 'EcoTrack Admin'
admin.site.index_title = 'Welcome to EcoTrack Admin Panel'


# Custom dashboard view for default admin site
from django.urls import path
from django.http import HttpResponseRedirect

def get_admin_urls(urls):
    from django.contrib.admin import site
    custom_urls = [
        path('custom-dashboard/', site.admin_view(custom_dashboard_view), name='custom_dashboard'),
    ]
    return custom_urls + urls


def custom_dashboard_view(request):
    """Custom admin dashboard with enhanced statistics"""
    from django.contrib.admin import site

    # Get statistics
    total_users = User.objects.filter(is_active=True).count()
    total_activities = ActivityLog.objects.count()
    total_carbon = ActivityLog.objects.aggregate(Sum('calculated_carbon'))['calculated_carbon__sum'] or 0
    total_points = UserProfile.objects.aggregate(Sum('total_points'))['total_points__sum'] or 0
    avg_points = UserProfile.objects.aggregate(Avg('total_points'))['total_points__avg'] or 0

    # Recent activities
    recent_activities = ActivityLog.objects.select_related('user').order_by('-created_at')[:10]

    # Top users
    top_users = UserProfile.objects.select_related('user').order_by('-total_points')[:5]

    # Activity breakdown
    activity_breakdown = []
    for activity_type in ['Travel', 'Energy', 'Diet']:
        count = ActivityLog.objects.filter(activity_type=activity_type).count()
        carbon = ActivityLog.objects.filter(activity_type=activity_type).aggregate(Sum('calculated_carbon'))['calculated_carbon__sum'] or 0
        activity_breakdown.append({
            'type': activity_type,
            'count': count,
            'carbon': carbon
        })

    # Badge stats
    total_badges = Badge.objects.count()
    total_earned = UserBadge.objects.count()

    # Challenge stats
    active_challenges = Challenge.objects.filter(status='active').count()
    total_challenge_participants = ChallengeParticipant.objects.count()

    # Streak stats
    total_streaks = UserProfile.objects.aggregate(Sum('streak_days'))['streak_days__sum'] or 0
    avg_streak = UserProfile.objects.aggregate(Avg('streak_days'))['streak_days__avg'] or 0

    context = {
        **site.each_context(request),
        'title': 'EcoTrack Dashboard',
        'total_users': total_users,
        'total_activities': total_activities,
        'total_carbon': total_carbon,
        'total_points': total_points,
        'avg_points': avg_points,
        'recent_activities': recent_activities,
        'top_users': top_users,
        'activity_breakdown': activity_breakdown,
        'total_badges': total_badges,
        'total_earned': total_earned,
        'active_challenges': active_challenges,
        'total_challenge_participants': total_challenge_participants,
        'total_streaks': total_streaks,
        'avg_streak': avg_streak,
    }
    return render(request, 'admin/custom_dashboard.html', context)


# Patch the admin site's get_urls method
original_get_urls = admin.site.get_urls
def custom_get_urls():
    return get_admin_urls(original_get_urls())
admin.site.get_urls = custom_get_urls


# Note: The EcoTrackAdminSite class below is not used currently
# but can be used if you want to create a completely separate admin interface
class EcoTrackAdminSite(admin.AdminSite):
    site_header = '🌱 EcoTrack Administration'
    site_title = 'EcoTrack Admin'
    index_title = 'Welcome to EcoTrack Admin Panel'

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('custom-dashboard/', self.admin_view(self.custom_dashboard), name='custom_dashboard'),
        ]
        return custom_urls + urls

    def custom_dashboard(self, request):
        """Custom admin dashboard with enhanced statistics"""
        # Get statistics
        total_users = User.objects.filter(is_active=True).count()
        total_activities = ActivityLog.objects.count()
        total_carbon = ActivityLog.objects.aggregate(Sum('calculated_carbon'))['calculated_carbon__sum'] or 0
        total_points = UserProfile.objects.aggregate(Sum('total_points'))['total_points__sum'] or 0
        avg_points = UserProfile.objects.aggregate(Avg('total_points'))['total_points__avg'] or 0

        # Recent activities
        recent_activities = ActivityLog.objects.select_related('user').order_by('-created_at')[:10]

        # Top users
        top_users = UserProfile.objects.select_related('user').order_by('-total_points')[:5]

        # Activity breakdown
        activity_breakdown = []
        for activity_type in ['Travel', 'Energy', 'Diet']:
            count = ActivityLog.objects.filter(activity_type=activity_type).count()
            carbon = ActivityLog.objects.filter(activity_type=activity_type).aggregate(Sum('calculated_carbon'))['calculated_carbon__sum'] or 0
            activity_breakdown.append({
                'type': activity_type,
                'count': count,
                'carbon': carbon
            })

        # Badge stats
        total_badges = Badge.objects.count()
        total_earned = UserBadge.objects.count()

        # Challenge stats
        active_challenges = Challenge.objects.filter(status='active').count()
        total_challenge_participants = ChallengeParticipant.objects.count()

        # Streak stats
        total_streaks = UserProfile.objects.aggregate(Sum('streak_days'))['streak_days__sum'] or 0
        avg_streak = UserProfile.objects.aggregate(Avg('streak_days'))['streak_days__avg'] or 0

        context = {
            **self.each_context(request),
            'title': 'EcoTrack Dashboard',
            'total_users': total_users,
            'total_activities': total_activities,
            'total_carbon': total_carbon,
            'total_points': total_points,
            'avg_points': avg_points,
            'recent_activities': recent_activities,
            'top_users': top_users,
            'activity_breakdown': activity_breakdown,
            'total_badges': total_badges,
            'total_earned': total_earned,
            'active_challenges': active_challenges,
            'total_challenge_participants': total_challenge_participants,
            'total_streaks': total_streaks,
            'avg_streak': avg_streak,
        }
        return render(request, 'admin/custom_dashboard.html', context)


# Use custom admin site
ecotrack_admin = EcoTrackAdminSite(name='ecotrack_admin')
