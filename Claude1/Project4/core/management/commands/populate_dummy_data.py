from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import random
from core.models import ActivityLog, UserProfile, Badge, UserBadge, Challenge, ChallengeParticipant, UserGoal, Achievement


class Command(BaseCommand):
    help = 'Populate the database with dummy data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Starting to populate dummy data...')

        # Create dummy users
        self.create_users()

        # Create badges
        self.create_badges()

        # Create activities
        self.create_activities()

        # Create challenges
        self.create_challenges()

        # Create achievements
        self.create_achievements()

        # Award badges to users
        self.award_badges()

        self.stdout.write(self.style.SUCCESS('✅ Dummy data populated successfully!'))

    def create_users(self):
        """Create dummy users"""
        users_data = [
            ('ecowarrior', 'Eco Warrior', 'New York', 'Passionate about sustainable living and reducing my carbon footprint! 🌱'),
            ('greenqueen', 'Green Queen', 'San Francisco', 'Environmental scientist spreading awareness about climate change.'),
            ('sustainable_sam', 'Sustainable Sam', 'Portland', 'Living zero waste since 2020. Every small action counts!'),
            ('carbon_cutter', 'Carbon Cutter', 'Seattle', 'Tech professional committed to green transportation.'),
            ('earth_guardian', 'Earth Guardian', 'Austin', 'Growing my own food and composting everything.'),
            ('nature_lover', 'Nature Lover', 'Denver', 'Hiking enthusiast and advocate for outdoor conservation.'),
            ('recycler_pro', 'Recycler Pro', 'Boston', 'Master recycler and sustainability consultant.'),
            ('solar_powered', 'Solar Powered', 'Phoenix', 'Powered by the sun and driving towards a greener future.'),
            ('bike_commuter', 'Bike Commuter', 'Chicago', 'Year-round cyclist proving cars are optional.'),
            ('vegan_vibes', 'Vegan Vibes', 'Los Angeles', 'Plant-based lifestyle advocate and animal lover.'),
        ]

        for username, display_name, location, bio in users_data:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f'{username}@ecotrack.com',
                    password='demo123',
                    first_name=display_name.split()[0],
                    last_name=' '.join(display_name.split()[1:])
                )
                UserProfile.objects.filter(user=user).update(
                    bio=bio,
                    location=location,
                    total_points=random.randint(100, 5000),
                    streak_days=random.randint(0, 30),
                    longest_streak=random.randint(5, 60)
                )
                self.stdout.write(f'Created user: {username}')

    def create_badges(self):
        """Create various badges"""
        badges_data = [
            # Points-based badges
            ('First Steps', 'Logged your first activity', 10, '🌱', 'points', 'common'),
            ('Eco Beginner', 'Reached 100 points', 100, '🌿', 'points', 'common'),
            ('Green Enthusiast', 'Reached 500 points', 500, '🍀', 'points', 'common'),
            ('Earth Friend', 'Reached 1000 points', 1000, '🌳', 'points', 'rare'),
            ('Planet Protector', 'Reached 2500 points', 2500, '🌍', 'points', 'rare'),
            ('Climate Hero', 'Reached 5000 points', 5000, '🦸', 'points', 'epic'),
            ('Carbon Master', 'Reached 10000 points', 10000, '⚡', 'points', 'legendary'),

            # Streak-based badges
            ('Week Warrior', '7-day streak', 0, '🔥', 'streak', 'common', 7),
            ('Monthly Master', '30-day streak', 0, '🏆', 'streak', 'rare', 30),
            ('Tri-monthly Champion', '90-day streak', 0, '💎', 'streak', 'epic', 90),
            ('Year Legend', '365-day streak', 0, '👑', 'streak', 'legendary', 365),

            # Activity-based badges
            ('Traveler', 'Logged 10 travel activities', 0, '✈️', 'activities', 'common', 10),
            ('Energy Saver', 'Logged 10 energy activities', 0, '⚡', 'activities', 'common', 10),
            ('Foodie', 'Logged 10 diet activities', 0, '🥗', 'activities', 'common', 10),
            ('Activity Master', 'Logged 100 total activities', 0, '📊', 'activities', 'rare', 100),

            # Special achievements
            ('Early Adopter', 'Joined in the first month', 0, '🎯', 'special', 'rare'),
            ('Community Leader', 'Top 10 on leaderboard', 0, '👑', 'special', 'epic'),
        ]

        for badge_data in badges_data:
            if len(badge_data) == 7:
                name, desc, points, icon, category, rarity, streak = badge_data
                Badge.objects.get_or_create(
                    name=name,
                    defaults={
                        'description': desc,
                        'points_required': points,
                        'icon': icon,
                        'category': category,
                        'rarity': rarity,
                        'streak_required': streak
                    }
                )
            else:
                name, desc, points, icon, category, rarity = badge_data
                Badge.objects.get_or_create(
                    name=name,
                    defaults={
                        'description': desc,
                        'points_required': points,
                        'icon': icon,
                        'category': category,
                        'rarity': rarity
                    }
                )

        self.stdout.write('Created badges')

    def create_activities(self):
        """Create activities for all users"""
        activity_types = ['Travel', 'Energy', 'Diet']
        travel_subtypes = ['car', 'bus', 'train', 'bike', 'walking', 'flight']
        diet_subtypes = ['vegan', 'vegetarian', 'meat']

        for user in User.objects.all():
            # Create 20-50 activities per user
            num_activities = random.randint(20, 50)

            for _ in range(num_activities):
                activity_type = random.choice(activity_types)
                days_ago = random.randint(0, 90)
                date = timezone.now().date() - timedelta(days=days_ago)

                activity = ActivityLog()
                activity.user = user
                activity.activity_type = activity_type
                activity.date = date

                if activity_type == 'Travel':
                    activity.activity_subtype = random.choice(travel_subtypes)
                    activity.value = random.uniform(1, 100)
                elif activity_type == 'Energy':
                    activity.value = random.uniform(5, 50)
                elif activity_type == 'Diet':
                    activity.activity_subtype = random.choice(diet_subtypes)
                    activity.value = random.randint(1, 5)

                activity.save()

        self.stdout.write('Created activities')

    def create_challenges(self):
        """Create community challenges"""
        challenges_data = [
            ('January Green Start', 'Start the year right! Log 50 activities in January', 50, 100),
            ('February Travel Light', 'Reduce your travel footprint', 200, 150),
            ('March Energy Saver', 'Cut down on energy usage', 150, 120),
            ('April Earth Month', 'Celebrate Earth Day with 100 points', 100, 200),
            ('May Bike Month', 'Log 20 bike activities', 80, 100),
        ]

        for title, desc, target, reward in challenges_data:
            challenge, created = Challenge.objects.get_or_create(
                title=title,
                defaults={
                    'description': desc,
                    'start_date': timezone.now().date() - timedelta(days=30),
                    'end_date': timezone.now().date() + timedelta(days=30),
                    'target_points': target,
                    'reward_points': reward,
                    'status': 'active'
                }
            )

            # Add random participants
            if created:
                participants = User.objects.order_by('?')[:random.randint(3, 8)]
                for user in participants:
                    ChallengeParticipant.objects.get_or_create(
                        challenge=challenge,
                        user=user,
                        defaults={
                            'points_earned': random.randint(0, target),
                            'status': random.choice(['joined', 'in_progress', 'completed'])
                        }
                    )

        self.stdout.write('Created challenges')

    def create_achievements(self):
        """Create special achievements"""
        achievements_data = [
            ('First Activity', 'Logged your very first activity', '🎉', 50),
            ('Week Streak', 'Maintained a 7-day streak', '🔥', 100),
            ('Century Club', 'Reached 100 points', '💯', 150),
            ('Social Butterfly', 'Set up your profile', '🦋', 25),
            ('Data Master', 'Logged 50 activities', '📈', 200),
            ('Eco Warrior', 'Reduced carbon by 100kg', '⚔️', 300),
        ]

        for title, desc, icon, points in achievements_data:
            Achievement.objects.get_or_create(
                title=title,
                defaults={
                    'description': desc,
                    'icon': icon,
                    'points_reward': points
                }
            )

        self.stdout.write('Created achievements')

    def award_badges(self):
        """Award badges to users based on their stats"""
        for user in User.objects.all():
            profile = user.profile
            earned_badges = UserBadge.objects.filter(user=user).count()

            # Award points-based badges
            points_badges = Badge.objects.filter(category='points').order_by('points_required')
            for badge in points_badges:
                if profile.total_points >= badge.points_required:
                    UserBadge.objects.get_or_create(user=user, badge=badge)

            # Award streak-based badges
            streak_badges = Badge.objects.filter(category='streak').order_by('streak_required')
            for badge in streak_badges:
                if profile.streak_days >= badge.streak_required:
                    UserBadge.objects.get_or_create(user=user, badge=badge)

            # Award activity-based badges
            activity_count = ActivityLog.objects.filter(user=user).count()
            activity_badges = Badge.objects.filter(category='activities').order_by('activities_required')
            for badge in activity_badges:
                if activity_count >= badge.activities_required:
                    UserBadge.objects.get_or_create(user=user, badge=badge)

        self.stdout.write('Awarded badges to users')
