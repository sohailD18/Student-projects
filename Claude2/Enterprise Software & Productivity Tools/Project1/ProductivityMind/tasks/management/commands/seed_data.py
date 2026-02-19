"""
Management command to seed the database with sample data for testing.
Run: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, datetime
import random

from tasks.models import (
    Task, Project, ProjectMember, Tag, Category,
    WorkLog, UserProfile
)
from tasks.ai_engine import TaskPrioritizationEngine, RiskPredictionEngine


class Command(BaseCommand):
    help = 'Seeds the database with sample data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_data()

        self.stdout.write(self.style.SUCCESS('Starting data seeding...'))

        # Create users
        users = self.create_users()

        # Create categories and tags
        categories = self.create_categories()
        tags = self.create_tags()

        # Create projects
        projects = self.create_projects(users)

        # Create tasks
        tasks = self.create_tasks(users, projects, categories, tags)

        # Create work logs
        self.create_work_logs(users, tasks)

        # Calculate AI scores
        self.calculate_ai_scores(tasks)

        self.stdout.write(self.style.SUCCESS(
            f'\nData seeding complete!\n'
            f'   - {len(users)} users\n'
            f'   - {len(categories)} categories\n'
            f'   - {len(tags)} tags\n'
            f'   - {len(projects)} projects\n'
            f'   - {len(tasks)} tasks\n'
            f'\nYou can now login at http://127.0.0.1:8000/admin/\n'
            f'Username: admin\n'
            f'Password: admin123\n'
        ))

    def clear_data(self):
        self.stdout.write(self.style.WARNING('Clearing existing data...'))
        WorkLog.objects.all().delete()
        Task.objects.all().delete()
        ProjectMember.objects.all().delete()
        Project.objects.all().delete()
        Tag.objects.all().delete()
        Category.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.all().delete()

    def create_users(self):
        self.stdout.write('Creating users...')

        users_data = [
            {'username': 'admin', 'first_name': 'Admin', 'last_name': 'User', 'is_staff': True, 'is_superuser': True},
            {'username': 'alice', 'first_name': 'Alice', 'last_name': 'Johnson'},
            {'username': 'bob', 'first_name': 'Bob', 'last_name': 'Smith'},
            {'username': 'charlie', 'first_name': 'Charlie', 'last_name': 'Brown'},
            {'username': 'diana', 'first_name': 'Diana', 'last_name': 'Prince'},
            {'username': 'evan', 'first_name': 'Evan', 'last_name': 'Williams'},
        ]

        users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': f"{user_data['username']}@example.com",
                    'first_name': user_data.get('first_name', ''),
                    'last_name': user_data.get('last_name', ''),
                    'is_staff': user_data.get('is_staff', False),
                    'is_superuser': user_data.get('is_superuser', False),
                }
            )
            if created:
                user.set_password('admin123')
                user.save()

            # Create or update profile
            UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'department': random.choice(['Engineering', 'Design', 'Marketing', 'Sales']),
                    'position': random.choice(['Developer', 'Designer', 'Manager', 'Analyst']),
                }
            )

            users.append(user)

        return users

    def create_categories(self):
        self.stdout.write('Creating categories...')

        categories_data = [
            {'name': 'Development', 'icon': '💻'},
            {'name': 'Design', 'icon': '🎨'},
            {'name': 'Marketing', 'icon': '📣'},
            {'name': 'Research', 'icon': '🔬'},
            {'name': 'Documentation', 'icon': '📝'},
        ]

        categories = []
        for cat_data in categories_data:
            cat, _ = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'icon': cat_data['icon']}
            )
            categories.append(cat)

        return categories

    def create_tags(self):
        self.stdout.write('Creating tags...')

        tags_data = [
            {'name': 'Urgent', 'color': '#ef4444'},
            {'name': 'Bug', 'color': '#f97316'},
            {'name': 'Feature', 'color': '#3b82f6'},
            {'name': 'Enhancement', 'color': '#8b5cf6'},
            {'name': 'Documentation', 'color': '#06b6d4'},
            {'name': 'Testing', 'color': '#10b981'},
            {'name': 'Frontend', 'color': '#ec4899'},
            {'name': 'Backend', 'color': '#6366f1'},
        ]

        tags = []
        for tag_data in tags_data:
            tag, _ = Tag.objects.get_or_create(
                name=tag_data['name'],
                defaults={'color': tag_data['color']}
            )
            tags.append(tag)

        return tags

    def create_projects(self, users):
        self.stdout.write('Creating projects...')

        projects_data = [
            {'name': 'Website Redesign', 'description': 'Complete overhaul of the company website'},
            {'name': 'Mobile App', 'description': 'Native mobile application development'},
            {'name': 'API Integration', 'description': 'Third-party API integrations'},
            {'name': 'Database Migration', 'description': 'Migrate to new database system'},
        ]

        projects = []
        for proj_data in projects_data:
            project, _ = Project.objects.get_or_create(
                name=proj_data['name'],
                defaults={'description': proj_data['description']}
            )

            # Add random members
            for user in random.sample(users, random.randint(2, len(users))):
                ProjectMember.objects.get_or_create(
                    project=project,
                    user=user,
                    defaults={'role': random.choice(['member', 'admin', 'viewer'])}
                )

            projects.append(project)

        return projects

    def create_tasks(self, users, projects, categories, tags):
        self.stdout.write('Creating tasks...')

        task_titles = [
            # Development tasks
            'Fix login bug on mobile devices',
            'Implement user authentication API',
            'Create responsive navigation component',
            'Optimize database queries for dashboard',
            'Add error handling for API calls',
            'Set up CI/CD pipeline',
            'Refactor legacy code module',
            'Write unit tests for payment processing',

            # Design tasks
            'Design new landing page mockup',
            'Create icon set for mobile app',
            'Update brand guidelines document',
            'Redesign user profile page',
            'Create accessibility improvements',

            # Documentation tasks
            'Write API documentation',
            'Update user manual with new features',
            'Create onboarding guide for new users',
            'Document deployment process',

            # Marketing tasks
            'Prepare social media campaign',
            'Analyze user engagement metrics',
            'Create email newsletter template',
            'Plan product launch event',

            # Research tasks
            'Research competitor pricing strategies',
            'Analyze user feedback from surveys',
            'Investigate new technology stack options',
            'Conduct user interviews for new features',
        ]

        priorities = ['low', 'medium', 'high', 'critical']
        statuses = ['todo', 'in_progress', 'done']

        tasks = []
        for i, title in enumerate(task_titles):
            # Select random category based on task title
            if 'design' in title.lower() or 'mockup' in title.lower() or 'icon' in title.lower():
                category = next((c for c in categories if 'Design' in c.name), categories[0])
            elif 'api' in title.lower() or 'bug' in title.lower() or 'code' in title.lower():
                category = next((c for c in categories if 'Development' in c.name), categories[0])
            elif 'document' in title.lower() or 'manual' in title.lower() or 'guide' in title.lower():
                category = next((c for c in categories if 'Documentation' in c.name), categories[0])
            elif 'marketing' in title.lower() or 'campaign' in title.lower() or 'social' in title.lower():
                category = next((c for c in categories if 'Marketing' in c.name), categories[0])
            elif 'research' in title.lower() or 'analyze' in title.lower() or 'investigate' in title.lower():
                category = next((c for c in categories if 'Research' in c.name), categories[0])
            else:
                category = random.choice(categories)

            # Calculate due date (some overdue, some upcoming)
            days_offset = random.randint(-10, 30)
            due_date = timezone.now() + timedelta(days=days_offset) if days_offset != 0 else None

            task = Task.objects.create(
                title=title,
                description=f'Detailed description for: {title}. This task includes specific requirements and acceptance criteria.',
                status=random.choice(statuses),
                priority=random.choice(priorities),
                project=random.choice(projects),
                assignee=random.choice(users),
                category=category,
                due_date=due_date,
                estimated_hours=random.choice([1, 2, 4, 8, 16]),
            )

            # Add random tags
            task_tags = random.sample(tags, random.randint(1, 3))
            task.tags.set(task_tags)

            # Create dependencies for some tasks
            if len(tasks) > 0 and random.random() > 0.7:
                blockers = random.sample(tasks, random.randint(1, min(3, len(tasks))))
                task.blocked_by.set(blockers)

            tasks.append(task)

        return tasks

    def create_work_logs(self, users, tasks):
        self.stdout.write('Creating work logs...')

        notes_templates = [
            'Completed initial implementation',
            'Fixed bugs found during testing',
            'Code review and refactoring',
            'Updated documentation',
            'Team meeting and planning',
            'Debugging and issue resolution',
            'Feature development',
            'Performance optimization',
        ]

        for task in tasks:
            # Only add work logs to some tasks (mostly in_progress or done)
            if task.status in ['in_progress', 'done'] and random.random() > 0.3:
                num_logs = random.randint(1, 5)
                for _ in range(num_logs):
                    WorkLog.objects.create(
                        task=task,
                        user=task.assignee or random.choice(users),
                        hours=random.choice([0.5, 1, 1.5, 2, 3, 4]),
                        notes=random.choice(notes_templates),
                        logged_at=timezone.now() - timedelta(days=random.randint(1, 30))
                    )

    def calculate_ai_scores(self, tasks):
        self.stdout.write('Calculating AI scores...')

        priority_engine = TaskPrioritizationEngine()
        risk_engine = RiskPredictionEngine()

        for task in tasks:
            task.smart_priority_score = priority_engine.calculate_smart_priority_score(task)
            task.risk_level = risk_engine.assess_task_risk(task)
            task.is_at_risk = task.risk_level in ['high', 'critical']
            task.save()
