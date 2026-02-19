from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
from core.models import Incident, Comment, UserProfile, IncidentVerification, Notification


class Command(BaseCommand):
    help = 'Create dummy data for testing'

    def handle(self, *args, **kwargs):
        # Create users
        users_data = [
            {'username': 'john_doe', 'email': 'john@example.com', 'location': 'Downtown', 'bio': 'Community safety advocate'},
            {'username': 'jane_smith', 'email': 'jane@example.com', 'location': 'Westside', 'bio': 'Concerned citizen'},
            {'username': 'mike_wilson', 'email': 'mike@example.com', 'location': 'North Hills', 'bio': 'Neighborhood watch coordinator'},
            {'username': 'sarah_davis', 'email': 'sarah@example.com', 'location': 'Eastside', 'bio': 'Safety conscious parent'},
            {'username': 'tom_brown', 'email': 'tom@example.com', 'location': 'Suburbia', 'bio': 'Active community member'},
        ]

        users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'is_active': True,
                }
            )
            if created:
                user.set_password('password123')
                user.save()

            # Get or create profile
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'location': user_data['location'],
                    'bio': user_data['bio'],
                    'latitude': random.uniform(40.7, 40.8),
                    'longitude': random.uniform(-74.0, -73.9),
                    'reputation_score': random.randint(0, 100),
                    'notification_enabled': True,
                }
            )
            users.append(user)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created user: {user.username}'))

        # Get categories
        from core.models import IncidentCategory
        categories = list(IncidentCategory.objects.all())

        if not categories:
            self.stdout.write(self.style.ERROR('No categories found. Run load_initial_data first.'))
            return

        # Sample incident data
        incidents_data = [
            {
                'title': 'Suspicious Vehicle Parked Overnight',
                'description': 'A dark van has been parked on Oak Street for two nights now. No license plate visible. People have been seen coming and going at odd hours.',
                'location': 'Oak Street, Downtown',
                'address': '123 Oak Street, near the old warehouse',
                'severity': 'medium',
                'status': 'pending',
                'category': categories[3],  # Suspicious Activity
            },
            {
                'title': 'Broken Traffic Light at Main Intersection',
                'description': 'The traffic light at the intersection of Main St and 5th Avenue is not working. It\'s been flashing yellow for Main Street traffic. Causing confusion and near-misses.',
                'location': 'Main St & 5th Avenue',
                'address': 'Intersection of Main Street and 5th Avenue, Downtown',
                'severity': 'high',
                'status': 'investigating',
                'category': categories[4],  # Traffic Hazard
            },
            {
                'title': 'Vandalism at Community Park',
                'description': 'Graffiti has been spray-painted on the playground equipment and benches. Happened sometime last night. Needs cleanup before children use it.',
                'location': 'Riverside Community Park',
                'address': '200 Park Avenue, Westside',
                'severity': 'low',
                'status': 'pending',
                'category': categories[2],  # Vandalism
            },
            {
                'title': 'Package Theft from Porch',
                'description': 'Delivered package was stolen from my porch within 30 minutes of delivery. Caught on doorbell camera - two individuals on foot, one wearing a red hoodie.',
                'location': 'Maple Drive, North Hills',
                'address': '45 Maple Drive',
                'severity': 'medium',
                'status': 'investigating',
                'category': categories[0],  # Theft
            },
            {
                'title': 'Large Pothole Causing Damage',
                'description': 'Massive pothole on Elm Street near the fire station. Multiple cars have hit it and sustained tire/rim damage. Very dangerous, especially at night.',
                'location': 'Elm Street',
                'address': 'Elm Street, between 2nd and 3rd Street',
                'severity': 'high',
                'status': 'verified',
                'category': categories[4],  # Traffic Hazard
            },
            {
                'title': 'Stray Dog Aggressive Behavior',
                'description': 'Large stray dog, looks like a pit bull mix, has been showing aggressive behavior toward pedestrians. Seen near the school bus stop. Very concerning for children.',
                'location': 'Pine Street near Elementary School',
                'address': 'Near 75 Pine Street',
                'severity': 'high',
                'status': 'investigating',
                'category': categories[9],  # Animal Issue
            },
            {
                'title': 'Water Main Break',
                'description': 'Significant water main break flooding Cedar Street. Water is gushing onto the road and creating icy conditions. City has been notified.',
                'location': 'Cedar Street',
                'address': '300 block of Cedar Street',
                'severity': 'critical',
                'status': 'resolved',
                'category': categories[11],  # Utility Issue
            },
            {
                'title': 'Loud Party Disturbance',
                'description': 'House party at 78 Birch Lane with extremely loud music continuing past 2AM. People yelling in the street. Has happened multiple weekends.',
                'location': 'Birch Lane',
                'address': '78 Birch Lane, Suburbia',
                'severity': 'low',
                'status': 'resolved',
                'category': categories[10],  # Public Disturbance
            },
            {
                'title': 'Attempted Break-in Reported',
                'description': 'My neighbor noticed someone trying to pry open back windows of the house at 92 Willow Court. They ran off when spotted. Police report filed.',
                'location': 'Willow Court',
                'address': '92 Willow Court, Eastside',
                'severity': 'high',
                'status': 'verified',
                'category': categories[0],  # Theft
            },
            {
                'title': 'Fallen Power Line',
                'description': 'Power line down across Walnut Street after storm. Sparks visible. Stay away! Utility company notified but not arrived yet.',
                'location': 'Walnut Street',
                'address': 'Walnut Street near the community center',
                'severity': 'critical',
                'status': 'resolved',
                'category': categories[11],  # Utility Issue
            },
            {
                'title': 'Missing Cat - Family Pet',
                'description': 'Our orange tabby cat "Whiskers" has been missing since yesterday evening. Very friendly, wearing blue collar. Last seen near Oak Park.',
                'location': 'Oak Park Area',
                'address': 'Near Oak Park, Eastside',
                'severity': 'low',
                'status': 'pending',
                'category': categories[8],  # Missing Person
            },
            {
                'title': 'Fire Hydrant Damaged',
                'description': 'Someone hit the fire hydrant at the corner of 4th and Pine. Water is spraying everywhere. Road is flooding. Fire department on the way.',
                'location': '4th Street & Pine Avenue',
                'address': 'Corner of 4th Street and Pine Avenue',
                'severity': 'medium',
                'status': 'resolved',
                'category': categories[5],  # Fire
            },
        ]

        incidents = []
        for incident_data in incidents_data:
            user = random.choice(users)
            days_ago = random.randint(1, 30)

            incident, created = Incident.objects.get_or_create(
                title=incident_data['title'],
                defaults={
                    'description': incident_data['description'],
                    'category': incident_data['category'],
                    'location': incident_data['location'],
                    'address': incident_data['address'],
                    'latitude': random.uniform(40.7, 40.8),
                    'longitude': random.uniform(-74.0, -73.9),
                    'severity': incident_data['severity'],
                    'status': incident_data['status'],
                    'timestamp': timezone.now() - timedelta(days=days_ago),
                    'user': user,
                    'is_verified': incident_data['status'] in ['verified', 'resolved'],
                    'verification_count': random.randint(0, 5) if incident_data['status'] in ['verified', 'resolved'] else 0,
                    'view_count': random.randint(5, 100),
                    'is_anonymous': random.choice([False, False, True]),
                }
            )
            incidents.append(incident)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created incident: {incident.title}'))

        # Add comments
        comments_data = [
            'Thank you for reporting this. I\'ve seen the same thing.',
            'Has anyone contacted the authorities about this?',
            'This happened on my street too. Very concerning.',
            'Good to know, I\'ll avoid this area for now.',
            'I can confirm this, saw it myself yesterday.',
            'Update: This has been resolved now.',
            'Be careful everyone, stay safe!',
            'Does anyone have more details about this?',
            'I\'ve reported this to the local authorities.',
            'Thanks for the heads up!',
        ]

        for incident in incidents:
            # Add 1-5 comments per incident
            num_comments = random.randint(1, 5)
            for _ in range(num_comments):
                commenter = random.choice(users)
                comment = Comment.objects.create(
                    incident=incident,
                    user=commenter,
                    content=random.choice(comments_data),
                    created_at=incident.created_at + timedelta(hours=random.randint(1, 48)),
                )
                # Add some likes
                num_likes = random.randint(0, 5)
                for _ in range(num_likes):
                    liker = random.choice([u for u in users if u != commenter])
                    from core.models import CommentLike
                    CommentLike.objects.get_or_create(
                        comment=comment,
                        user=liker
                    )
                comment.likes_count = num_likes
                comment.save()

        # Add verifications
        for incident in incidents:
            if not incident.is_verified:
                # Add 0-2 verifications for unverified incidents
                num_verifications = random.randint(0, 2)
            else:
                # Add 3-5 verifications for verified incidents
                num_verifications = random.randint(3, 5)

            verifiers = random.sample(users, min(num_verifications, len(users)))
            for verifier in verifiers:
                if verifier != incident.user:
                    IncidentVerification.objects.get_or_create(
                        incident=incident,
                        user=verifier,
                        defaults={
                            'is_confirmed': random.choice([True, True, True, False]),
                            'comments': 'I can confirm this is accurate.' if random.random() > 0.5 else '',
                        }
                    )

        # Create some notifications
        notification_types = ['new_incident', 'incident_verified', 'incident_updated']
        for user in users:
            # Give each user 2-5 notifications
            for _ in range(random.randint(2, 5)):
                incident = random.choice(incidents)
                notification = Notification.objects.create(
                    recipient=user,
                    notification_type=random.choice(notification_types),
                    title=f'Update: {incident.title}',
                    message=f'There has been an update regarding "{incident.title}". Check the incident page for details.',
                    incident=incident,
                    is_read=random.choice([True, False]),
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nCreated {len(users)} users\n'
                f'Created {len(incidents)} incidents\n'
                f'Added comments and verifications\n'
                f'Created notifications\n\n'
                f'Dummy data creation complete!'
            )
        )
