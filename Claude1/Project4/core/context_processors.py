from django.contrib.auth.models import User
from .models import ActivityLog, UserProfile, Badge, UserBadge, Challenge, ChallengeParticipant
from django.db.models import Sum, Avg


def admin_stats(request):
    """
    Context processor to provide statistics to the admin panel.
    """
    if request.path.startswith('/admin/'):
        try:
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

            return {
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
        except Exception as e:
            # Return empty dict if there's any error
            return {}
    return {}
