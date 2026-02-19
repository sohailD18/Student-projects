from django.core.management.base import BaseCommand
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
import random
from tickets.models import Complaint, Ticket, Feedback


class Command(BaseCommand):
    help = 'Load demo data for HelpDeskPro system'

    def handle(self, *args, **kwargs):
        self.stdout.write('Loading demo data...')

        # Clear existing data
        Feedback.objects.all().delete()
        Ticket.objects.all().delete()
        Complaint.objects.all().delete()

        # Demo complaints data
        demo_complaints = [
            {
                'name': 'John Smith',
                'email': 'john.smith@example.com',
                'category': 'technical',
                'priority': 'high',
                'description': 'Unable to login to my account. I keep getting "Invalid credentials" error even though I am using the correct password. This is urgent as I need to access my account for work.'
            },
            {
                'name': 'Sarah Johnson',
                'email': 'sarah.j@company.com',
                'category': 'billing',
                'priority': 'medium',
                'description': 'I was charged twice for my monthly subscription. The transaction IDs are #TXN-12345 and #TXN-12346. Please refund one of these charges.'
            },
            {
                'name': 'Mike Williams',
                'email': 'm.williams@techcorp.com',
                'category': 'feature',
                'priority': 'low',
                'description': 'It would be great if you could add dark mode to the application. Many users have requested this feature and it would improve the user experience significantly.'
            },
            {
                'name': 'Emily Davis',
                'email': 'emily.d@startup.io',
                'category': 'bug',
                'priority': 'high',
                'description': 'Critical bug found! When I try to export reports to PDF, the application crashes and I lose all my data. This happens every time on the reports page.'
            },
            {
                'name': 'Robert Brown',
                'email': 'r.brown@enterprise.com',
                'category': 'technical',
                'priority': 'medium',
                'description': 'The mobile app is very slow and takes forever to load. Pages take 10-15 seconds to load. Please optimize performance.'
            },
            {
                'name': 'Lisa Anderson',
                'email': 'lisa.a@agency.com',
                'category': 'billing',
                'priority': 'low',
                'description': 'I need to update my payment method but cannot find the option in the settings. Can you guide me on how to do this?'
            },
            {
                'name': 'David Wilson',
                'email': 'd.wilson@corp.net',
                'category': 'feature',
                'priority': 'medium',
                'description': 'Please add an option to download all data at once. Currently I have to download each file separately which is very time-consuming.'
            },
            {
                'name': 'Jennifer Martinez',
                'email': 'j.martinez@org.com',
                'category': 'bug',
                'priority': 'high',
                'description': 'Email notifications are not being sent. I have enabled all notifications but I am not receiving any emails when tickets are updated.'
            },
            {
                'name': 'Christopher Lee',
                'email': 'c.lee@firm.com',
                'category': 'technical',
                'priority': 'low',
                'description': 'I cannot find the logout button. It seems to be missing from the navigation menu. Please advise.'
            },
            {
                'name': 'Amanda Taylor',
                'email': 'a.taylor@studio.com',
                'category': 'other',
                'priority': 'medium',
                'description': 'I would like to request a refund for my annual subscription. I accidentally purchased it twice.'
            },
            {
                'name': 'James Moore',
                'email': 'j.moore@tech.io',
                'category': 'technical',
                'priority': 'high',
                'description': 'Server is down! I cannot access any of my data. Getting 500 Internal Server Error on all pages. This is critical!'
            },
            {
                'name': 'Jessica Thomas',
                'email': 'j.thomas@ltd.com',
                'category': 'billing',
                'priority': 'medium',
                'description': 'My invoice shows a different amount than what was quoted. The quote was $500 but the invoice shows $650. Please clarify.'
            },
            {
                'name': 'Daniel Harris',
                'email': 'd.harris@co.com',
                'category': 'technical',
                'priority': 'high',
                'description': 'Database connection errors are occurring frequently. Our team cannot access the customer data needed for daily operations.'
            },
            {
                'name': 'Laura Martin',
                'email': 'laura.m@tech.net',
                'category': 'feature',
                'priority': 'low',
                'description': 'Would love to see a mobile app for iOS and Android. The current mobile web experience is not great.'
            },
            {
                'name': 'Matthew Clark',
                'email': 'm.clark@systems.io',
                'category': 'bug',
                'priority': 'high',
                'description': 'The search functionality is not working properly. It returns irrelevant results or no results at all for valid queries.'
            },
            {
                'name': 'Sophia White',
                'email': 's.white@globals.com',
                'category': 'billing',
                'priority': 'medium',
                'description': 'My subscription was renewed without notification. I did not want auto-renewal enabled. Please cancel and refund.'
            },
            {
                'name': 'Andrew Lewis',
                'email': 'a.lewis@corp.net',
                'category': 'technical',
                'priority': 'medium',
                'description': 'File uploads are failing. I keep getting timeout errors when trying to upload documents larger than 5MB.'
            },
            {
                'name': 'Olivia Walker',
                'email': 'o.walker@agency.com',
                'category': 'feature',
                'priority': 'low',
                'description': 'Add keyboard shortcuts for common actions. This would greatly improve productivity for power users.'
            },
            {
                'name': 'Ethan Hall',
                'email': 'e.hall@tech.io',
                'category': 'bug',
                'priority': 'medium',
                'description': 'The date picker is not working correctly in Safari browser. It shows the wrong dates.'
            },
            {
                'name': 'Isabella Young',
                'email': 'i.young@firm.com',
                'category': 'technical',
                'priority': 'high',
                'description': 'API authentication is failing. All our integrations stopped working suddenly. This is blocking our business operations.'
            },
            {
                'name': 'Lucas King',
                'email': 'l.king@start.co',
                'category': 'other',
                'priority': 'low',
                'description': 'I have a general question about your enterprise pricing plans. Can someone contact me to discuss?'
            },
        ]

        staff_members = ['Alex Turner', 'Maria Garcia', 'Steven Clark', 'Nancy White', 'Kevin Hall']
        statuses = ['open', 'open', 'open', 'in_progress', 'in_progress', 'escalated', 'closed', 'closed', 'closed', 'closed', 'closed', 'closed',
                     'open', 'in_progress', 'in_progress', 'closed', 'closed', 'closed', 'closed', 'closed', 'open']

        # Create complaints and tickets
        complaints = []
        for i, data in enumerate(demo_complaints):
            complaint = Complaint.objects.create(**data)
            complaints.append(complaint)

            # Create ticket with random date in last 30 days
            days_ago = random.randint(1, 30)
            created_at = timezone.now() - timedelta(days=days_ago)

            # Create ticket directly with custom created_at
            ticket = Ticket(
                complaint=complaint,
                status=statuses[i],
                assigned_staff=random.choice(staff_members) if statuses[i] != 'open' else None,
                created_at=created_at,
                updated_at=created_at + timedelta(hours=random.randint(1, 48))
            )

            # Escalate some tickets
            if statuses[i] == 'escalated':
                ticket.is_escalated = True
                ticket.escalated_at = ticket.updated_at
                ticket.escalated_by = random.choice(staff_members)

            ticket.save()

            # Add feedback for closed tickets
            if statuses[i] == 'closed':
                ratings = [5, 5, 4, 4, 5, 3, 4, 5, 5, 4, 3, 5]
                comments = [
                    'Excellent support! The issue was resolved very quickly.',
                    'Good service overall. Would appreciate faster response time.',
                    'The team was helpful and professional. Thank you!',
                    'Outstanding service! The agent went above and beyond.',
                    'Issue was resolved but took longer than expected.',
                    'Very satisfied with the resolution. Great job!',
                    'Professional and efficient service. Thank you for your help.',
                    'Quick resolution and friendly staff. Highly recommend!',
                    'The support team was knowledgeable and fixed my issue fast.',
                    'Good experience overall. The dashboard is easy to use.',
                    'Took a while to resolve but the outcome was satisfactory.',
                    'Perfect! Everything works smoothly now. Thank you for your help.',
                ]
                Feedback.objects.create(
                    ticket=ticket,
                    rating=random.choice(ratings),
                    comments=random.choice(comments),
                    created_at=created_at + timedelta(days=random.randint(1, 5))
                )

        # Statistics
        total = Complaint.objects.count()
        tickets = Ticket.objects.count()
        feedback_count = Feedback.objects.count()

        self.stdout.write(self.style.SUCCESS(f'\n[*] Demo data loaded successfully!'))
        self.stdout.write(f'   - Complaints: {total}')
        self.stdout.write(f'   - Tickets: {tickets}')
        self.stdout.write(f'   - Feedback: {feedback_count}')
        self.stdout.write(f'\n[*] Breakdown:')
        self.stdout.write(f'   - Open: {Ticket.objects.filter(status="open").count()}')
        self.stdout.write(f'   - In Progress: {Ticket.objects.filter(status="in_progress").count()}')
        self.stdout.write(f'   - Escalated: {Ticket.objects.filter(status="escalated").count()}')
        self.stdout.write(f'   - Closed: {Ticket.objects.filter(status="closed").count()}')
        avg_rating = Feedback.objects.aggregate(avg=models.Avg('rating'))['avg'] or 0
        self.stdout.write(f'\n[*] Average Rating: {avg_rating:.1f}/5')
