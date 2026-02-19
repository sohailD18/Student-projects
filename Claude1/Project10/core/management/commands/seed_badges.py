from django.core.management.base import BaseCommand
from users.models import Badge


class Command(BaseCommand):
    help = 'Seeds the database with initial badges for the SkillSwap platform'

    def handle(self, *args, **options):
        badges_data = [
            {
                'name': 'First Step',
                'description': 'Completed your first learning session!',
                'icon': '👣',
                'points_required': 0,
                'sessions_required': 1
            },
            {
                'name': 'Curious Mind',
                'description': 'Completed 5 learning sessions',
                'icon': '🧠',
                'points_required': 0,
                'sessions_required': 5
            },
            {
                'name': 'Dedicated Learner',
                'description': 'Completed 10 learning sessions',
                'icon': '📚',
                'points_required': 0,
                'sessions_required': 10
            },
            {
                'name': 'Knowledge Seeker',
                'description': 'Completed 25 learning sessions',
                'icon': '🎓',
                'points_required': 0,
                'sessions_required': 25
            },
            {
                'name': 'Master Learner',
                'description': 'Completed 50 learning sessions',
                'icon': '🏆',
                'points_required': 0,
                'sessions_required': 50
            },
            {
                'name': 'First Teaching Session',
                'description': 'Completed your first teaching session!',
                'icon': '🎯',
                'points_required': 0,
                'sessions_required': 1
            },
            {
                'name': 'Inspiring Teacher',
                'description': 'Completed 10 teaching sessions',
                'icon': '🌟',
                'points_required': 0,
                'sessions_required': 10
            },
            {
                'name': 'Expert Mentor',
                'description': 'Completed 25 teaching sessions',
                'icon': '👨‍🏫',
                'points_required': 0,
                'sessions_required': 25
            },
            {
                'name': 'Rising Star',
                'description': 'Earned 100 points',
                'icon': '⭐',
                'points_required': 100,
                'sessions_required': 0
            },
            {
                'name': 'Point Collector',
                'description': 'Earned 500 points',
                'icon': '💎',
                'points_required': 500,
                'sessions_required': 0
            },
            {
                'name': 'Point Master',
                'description': 'Earned 1000 points',
                'icon': '👑',
                'points_required': 1000,
                'sessions_required': 0
            },
            {
                'name': 'Community Builder',
                'description': 'Completed 100 sessions (teaching + learning)',
                'icon': '🤝',
                'points_required': 0,
                'sessions_required': 100
            },
            {
                'name': 'SkillSwap Legend',
                'description': 'Completed 200 sessions (teaching + learning)',
                'icon': '🏅',
                'points_required': 0,
                'sessions_required': 200
            },
        ]

        created_count = 0
        updated_count = 0

        for badge_data in badges_data:
            badge, created = Badge.objects.get_or_create(
                name=badge_data['name'],
                defaults={
                    'description': badge_data['description'],
                    'icon': badge_data['icon'],
                    'points_required': badge_data['points_required'],
                    'sessions_required': badge_data['sessions_required']
                }
            )

            if created:
                created_count += 1
                # Use ASCII-safe output for Windows console
                self.stdout.write(
                    self.style.SUCCESS(f'Created badge: {badge.name}')
                )
            else:
                # Update existing badge
                badge.description = badge_data['description']
                badge.icon = badge_data['icon']
                badge.points_required = badge_data['points_required']
                badge.sessions_required = badge_data['sessions_required']
                badge.save()
                updated_count += 1
                # Use ASCII-safe output for Windows console
                self.stdout.write(
                    self.style.WARNING(f'Updated badge: {badge.name}')
                )

        total_badges = created_count + updated_count
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully seeded {total_badges} badges! '
                f'({created_count} created, {updated_count} updated)'
            )
        )
