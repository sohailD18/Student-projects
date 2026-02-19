from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random

from users.models import UserProfile, Badge
from core.models import Skill, Session, Review


class Command(BaseCommand):
    help = 'Seeds the database with demo data for testing and development'

    def handle(self, *args, **options):
        self.stdout.write('Seeding demo data...')

        # Create demo users
        demo_users_data = [
            {'username': 'john_developer', 'bio': 'Full-stack developer with 10 years of experience'},
            {'username': 'sarah_designer', 'bio': 'UI/UX designer passionate about creating beautiful interfaces'},
            {'username': 'mike_musician', 'bio': 'Music teacher specializing in guitar and piano'},
            {'username': 'emma_chef', 'bio': 'Professional chef teaching culinary arts'},
            {'username': 'david_fitness', 'bio': 'Certified fitness trainer and nutritionist'},
            {'username': 'lisa_linguist', 'bio': 'Polyglot fluent in 5 languages'},
            {'username': 'tom_artist', 'bio': 'Digital artist and illustrator'},
            {'username': 'anna_writer', 'bio': 'Content writer and copyeditor'},
        ]

        demo_users = []
        for user_data in demo_users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': f"{user_data['username']}@example.com",
                    'first_name': user_data['username'].split('_')[0].title(),
                    'last_name': user_data['username'].split('_')[1].title() if '_' in user_data['username'] else 'User',
                }
            )
            if created:
                user.set_password('demo123')
                user.save()
                self.stdout.write(f'  Created user: {user.username}')

            # Get or create profile
            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'bio': user_data['bio'],
                    'points_earned': random.randint(50, 500),
                    'skills_to_teach': self._get_random_skills(),
                    'skills_to_learn': self._get_random_skills(),
                }
            )
            demo_users.append(user)

        # Award some badges to users
        all_badges = list(Badge.objects.all())
        for user in demo_users:
            profile = user.profile
            # Award 1-3 random badges to each user
            badges_to_award = random.sample(all_badges, min(random.randint(1, 3), len(all_badges)))
            profile.badges.add(*badges_to_award)

        # Create demo skills
        demo_skills_data = [
            {
                'teacher': 'john_developer',
                'title': 'Python Programming for Beginners',
                'description': 'Learn Python from scratch. We will cover variables, data types, loops, functions, and object-oriented programming. Perfect for absolute beginners with no prior coding experience.',
                'category': 'tech',
                'points': 50
            },
            {
                'teacher': 'john_developer',
                'title': 'Web Development with Django',
                'description': 'Build modern web applications using Django framework. Covers models, views, templates, forms, and deployment. Includes a real-world project.',
                'category': 'tech',
                'points': 75
            },
            {
                'teacher': 'sarah_designer',
                'title': 'UI/UX Design Fundamentals',
                'description': 'Master the principles of user interface and user experience design. Learn Figma, color theory, typography, and design thinking methodology.',
                'category': 'art',
                'points': 60
            },
            {
                'teacher': 'sarah_designer',
                'title': 'Logo Design Masterclass',
                'description': 'Create memorable logos from concept to final design. Learn Adobe Illustrator, branding principles, and client communication.',
                'category': 'art',
                'points': 45
            },
            {
                'teacher': 'mike_musician',
                'title': 'Acoustic Guitar for Beginners',
                'description': 'Start your guitar journey! Learn basic chords, strumming patterns, fingerpicking, and play your first songs within weeks.',
                'category': 'music',
                'points': 40
            },
            {
                'teacher': 'mike_musician',
                'title': 'Music Theory Essentials',
                'description': 'Understand the language of music. Scales, chords, progressions, and how to compose your own melodies.',
                'category': 'music',
                'points': 55
            },
            {
                'teacher': 'emma_chef',
                'title': 'Italian Cuisine Mastery',
                'description': 'Authentic Italian cooking from pasta making to risotto, pizza, and classic desserts. Learn from a professional chef.',
                'category': 'cooking',
                'points': 50
            },
            {
                'teacher': 'emma_chef',
                'title': 'Baking Fundamentals',
                'description': 'Master bread, pastries, cakes, and cookies. Learn techniques, recipes, and presentation skills for professional results.',
                'category': 'cooking',
                'points': 45
            },
            {
                'teacher': 'david_fitness',
                'title': 'Home Workout Guide',
                'description': 'Get fit at home with no equipment! Full-body workouts, HIIT routines, and flexibility training for all fitness levels.',
                'category': 'sports',
                'points': 35
            },
            {
                'teacher': 'david_fitness',
                'title': 'Nutrition for Healthy Living',
                'description': 'Learn about macros, meal planning, superfoods, and sustainable eating habits. Transform your relationship with food.',
                'category': 'sports',
                'points': 40
            },
            {
                'teacher': 'lisa_linguist',
                'title': 'Conversational Spanish',
                'description': 'Speak Spanish confidently! Focus on pronunciation, common phrases, grammar, and cultural insights for real conversations.',
                'category': 'language',
                'points': 60
            },
            {
                'teacher': 'lisa_linguist',
                'title': 'French for Travelers',
                'description': 'Essential French for tourists. Greetings, directions, ordering food, and emergency phrases for a stress-free trip.',
                'category': 'language',
                'points': 35
            },
            {
                'teacher': 'tom_artist',
                'title': 'Digital Illustration Basics',
                'description': 'Create stunning digital art using Procreate and Photoshop. Learn composition, color, and digital painting techniques.',
                'category': 'art',
                'points': 55
            },
            {
                'teacher': 'anna_writer',
                'title': 'Creative Writing Workshop',
                'description': 'Unleash your creativity! Fiction writing techniques, character development, plot structure, and finding your unique voice.',
                'category': 'academic',
                'points': 45
            },
        ]

        demo_skills = []
        for skill_data in demo_skills_data:
            teacher = User.objects.get(username=skill_data['teacher'])
            skill, created = Skill.objects.get_or_create(
                teacher=teacher,
                title=skill_data['title'],
                defaults={
                    'description': skill_data['description'],
                    'category': skill_data['category'],
                    'hourly_rate_points': skill_data['points'],
                }
            )
            if created:
                self.stdout.write(f'  Created skill: {skill.title}')
            demo_skills.append(skill)

        # Create demo sessions
        now = timezone.now()
        session_statuses = ['pending', 'accepted', 'completed', 'cancelled']

        for i, skill in enumerate(demo_skills[:10]):  # Create sessions for first 10 skills
            teacher = skill.teacher
            # Get a random student (not the teacher)
            potential_students = [u for u in demo_users if u != teacher]
            if not potential_students:
                continue

            student = random.choice(potential_students)

            # Create 1-3 sessions per skill
            for j in range(random.randint(1, 3)):
                scheduled_time = now + timedelta(days=random.randint(-5, 15))

                session, created = Session.objects.get_or_create(
                    skill=skill,
                    student=student,
                    teacher=teacher,
                    scheduled_time=scheduled_time,
                    defaults={
                        'status': random.choice(session_statuses)
                    }
                )
                if created:
                    self.stdout.write(f'  Created session: {skill.title[:30]}...')

                    # Add reviews for completed sessions
                    if session.status == 'completed':
                        Review.objects.get_or_create(
                            session=session,
                            defaults={
                                'rating': random.choice([4, 5, 5, 5, 3, 4, 5]),  # Weight towards good ratings
                                'comment': self._get_random_review(),
                                'reviewer': student,
                            }
                        )

        self.stdout.write(self.style.SUCCESS('\nDemo data seeded successfully!'))
        self.stdout.write(self.style.SUCCESS('\nDemo User Credentials:'))
        for user in demo_users:
            self.stdout.write(f'  {user.username} / demo123')

    def _get_random_skills(self):
        """Return random comma-separated skills"""
        all_skills = [
            'Python', 'JavaScript', 'Django', 'React', 'UI Design', 'UX Design',
            'Guitar', 'Piano', 'Cooking', 'Baking', 'Fitness', 'Yoga',
            'Spanish', 'French', 'German', 'Writing', 'Photography'
        ]
        return ', '.join(random.sample(all_skills, random.randint(2, 5)))

    def _get_random_review(self):
        """Return a random review comment"""
        reviews = [
            'Excellent teacher! Very patient and knowledgeable.',
            'Great session, learned a lot!',
            'Highly recommend! Clear explanations and practical examples.',
            'Amazing experience. Will book again!',
            'Very professional and well-prepared.',
            'Friendly and approachable teaching style.',
            'Perfect for beginners. Made complex topics easy to understand.',
            'Exceeded my expectations. Thank you!',
            'Practical and useful content.',
            'Looking forward to the next session!',
        ]
        return random.choice(reviews)
