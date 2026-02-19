from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta


class Command(BaseCommand):
    help = 'Load demo data for CRM System'

    def handle(self, *args, **options):
        self.stdout.write('Loading demo data for CRM...')
        
        # Clear existing demo data (keep superuser and admin)
        self.clear_existing_demo_data()
        
        # Create demo users
        self.stdout.write('Creating users...')
        users = self.create_users()
        
        # Create pipeline and stages
        self.stdout.write('Creating pipeline and stages...')
        pipeline = self.create_pipeline()
        
        # Create companies
        self.stdout.write('Creating companies...')
        companies = self.create_companies(users)
        
        # Create contacts
        self.stdout.write('Creating contacts...')
        contacts = self.create_contacts(users, companies)
        
        # Create deals
        self.stdout.write('Creating deals...')
        deals = self.create_deals(users, contacts, companies)
        
        # Create activities
        self.stdout.write('Creating activities...')
        self.create_activities(users, contacts, deals)
        
        self.stdout.write(self.style.SUCCESS('Demo data loaded successfully!'))
        self.stdout.write('\nDemo Login Credentials:')
        for i, user in enumerate(users[:3]):
            self.stdout.write(f'  {i+1}. Username: {user.username} | Password: Demo1@123')

    def clear_existing_demo_data(self):
        from deals.models import Deal, PipelineStage, Pipeline
        from activities.models import Activity
        from contacts.models import Contact, Company, Tag
        
        Deal.objects.all().delete()
        Activity.objects.all().delete()
        Contact.objects.filter(user__username__in=['user1', 'user2', 'user3', 'user4']).delete()
        Company.objects.all().delete()
        PipelineStage.objects.all().delete()
        Pipeline.objects.all().delete()
        Tag.objects.all().delete()
        
        User.objects.filter(username__in=['user1', 'user2', 'user3']).delete()

    def create_users(self):
        users = []
        
        user_data = [
            {
                'username': 'user1',
                'first_name': 'John',
                'last_name': 'Smith',
                'email': 'john.smith@company.com',
            },
            {
                'username': 'user2',
                'first_name': 'Jane',
                'last_name': 'Johnson',
                'email': 'jane.johnson@company.com',
            },
            {
                'username': 'user3',
                'first_name': 'Mike',
                'last_name': 'Williams',
                'email': 'mike.williams@company.com',
            },
        ]
        
        for data in user_data:
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                password='Demo1@123',
            )
            users.append(user)
        
        return users

    def create_pipeline(self):
        from deals.models import Pipeline, PipelineStage
        
        pipeline = Pipeline.objects.create(
            name='Sales Pipeline',
            description='Standard sales process from lead to close',
            is_default=True,
        )
        
        stage_names = ['Lead', 'Qualified', 'Proposal', 'Negotiation', 'Won', 'Lost']
        stage_keys = ['lead', 'qualified', 'proposal', 'negotiation', 'won', 'lost']
        stage_colors = ['#6c757d', '#0dcaf0', '#fd7e14', '#ffc107', '#28a745', '#dc3545']
        win_probabilities = [10, 25, 50, 75, 100, 0]
        
        for i, (name, key, color, win_prob) in enumerate(zip(stage_names, stage_keys, stage_colors, win_probabilities)):
            PipelineStage.objects.create(
                pipeline=pipeline,
                name=name,
                stage_key=key,
                order=i + 1,
                color=color,
                win_probability=win_prob,
            )
        
        return pipeline

    def create_companies(self, users):
        from contacts.models import Company
        
        companies = []
        
        company_data = [
            {
                'name': 'TechCorp Solutions',
                'industry': 'TECHNOLOGY',
                'company_size': '500+',
                'website': 'https://techcorp.com',
                'email': 'contact@techcorp.com',
                'phone': '+1-555-0101',
                'address': '123 Tech Park, San Francisco, CA 94105',
                'city': 'San Francisco',
                'state': 'CA',
                'country': 'USA',
                'description': 'Leading technology solutions provider',
            },
            {
                'name': 'Global Marketing Group',
                'industry': 'SERVICES',
                'company_size': '201-500',
                'website': 'https://globalmarketing.com',
                'email': 'info@globalmarketing.com',
                'phone': '+1-555-0102',
                'address': '456 Marketing Ave, New York, NY 10001',
                'city': 'New York',
                'state': 'NY',
                'country': 'USA',
                'description': 'Full-service marketing agency',
            },
            {
                'name': 'Startup Ventures Inc',
                'industry': 'SERVICES',
                'company_size': '51-200',
                'website': 'https://startupventures.com',
                'email': 'hello@startupventures.com',
                'phone': '+1-555-0103',
                'address': '789 Innovation Blvd, Austin, TX 78701',
                'city': 'Austin',
                'state': 'TX',
                'country': 'USA',
                'description': 'Innovative startup',
            },
            {
                'name': 'Manufacturing Pro',
                'industry': 'MANUFACTURING',
                'company_size': '500+',
                'website': 'https://manufacturingpro.com',
                'email': 'sales@manufacturingpro.com',
                'phone': '+1-555-0104',
                'address': '321 Industrial Drive, Detroit, MI 48201',
                'city': 'Detroit',
                'state': 'MI',
                'country': 'USA',
                'description': 'Leading manufacturer',
            },
        ]
        
        for i, data in enumerate(company_data):
            company = Company.objects.create(**data)
            companies.append(company)
        
        return companies

    def create_contacts(self, users, companies):
        from contacts.models import Contact
        
        contacts = []
        
        contact_data = [
            {
                'user': users[0],
                'company': companies[0],
                'first_name': 'David',
                'last_name': 'Miller',
                'email': 'david.miller@techcorp.com',
                'phone': '+1-555-0201',
                'job_title': 'CTO',
                'department': 'Engineering',
                'status': 'CUSTOMER',
                'source': 'Website',
                'address': '123 Tech Park, San Francisco, CA 94105',
                'city': 'San Francisco',
                'state': 'CA',
                'country': 'USA',
                'linkedin': 'https://linkedin.com/in/davidmiller',
                'notes': 'Key decision maker for technology purchases.',
                'tags': 'technical',
            },
            {
                'user': users[0],
                'company': companies[0],
                'first_name': 'Sarah',
                'last_name': 'Chen',
                'email': 'sarah.chen@techcorp.com',
                'phone': '+1-555-0202',
                'job_title': 'Engineering Manager',
                'department': 'Engineering',
                'status': 'PROSPECT',
                'source': 'Referral',
                'address': '123 Tech Park, San Francisco, CA 94105',
                'city': 'San Francisco',
                'state': 'CA',
                'country': 'USA',
                'linkedin': 'https://linkedin.com/in/sarahchen',
                'notes': 'Managing team of senior engineers.',
                'tags': 'technical',
            },
            {
                'user': users[1],
                'company': companies[1],
                'first_name': 'Michael',
                'last_name': 'Brown',
                'email': 'michael.brown@globalmarketing.com',
                'phone': '+1-555-0301',
                'job_title': 'Marketing Director',
                'department': 'Marketing',
                'status': 'PROSPECT',
                'source': 'Trade Show',
                'address': '456 Marketing Ave, New York, NY 10001',
                'city': 'New York',
                'state': 'NY',
                'country': 'USA',
                'linkedin': 'https://linkedin.com/in/michaelbrown',
                'notes': 'Looking for strategic partnerships with tech companies.',
                'tags': 'marketing,director',
            },
            {
                'user': users[1],
                'company': companies[1],
                'first_name': 'Jessica',
                'last_name': 'Wilson',
                'email': 'jessica.wilson@globalmarketing.com',
                'phone': '+1-555-0302',
                'job_title': 'Account Manager',
                'department': 'Sales',
                'status': 'PROSPECT',
                'source': 'Referral',
                'address': '456 Marketing Ave, New York, NY 10001',
                'city': 'New York',
                'state': 'NY',
                'country': 'USA',
                'linkedin': 'https://linkedin.com/in/jessicawilson',
                'notes': 'Long-term client with high retention rate.',
                'tags': 'accounting,finance',
            },
            {
                'user': users[2],
                'company': companies[2],
                'first_name': 'Robert',
                'last_name': 'Garcia',
                'email': 'robert.garcia@startupventures.com',
                'phone': '+1-555-0401',
                'job_title': 'CEO',
                'department': 'Executive',
                'status': 'PROSPECT',
                'source': 'Website',
                'address': '789 Innovation Blvd, Austin, TX 78701',
                'city': 'Austin',
                'state': 'TX',
                'country': 'USA',
                'linkedin': 'https://linkedin.com/in/robertgarcia',
                'notes': 'Founded startup in 2020, looking to scale.',
                'tags': 'executive,startup',
            },
            {
                'user': users[2],
                'company': companies[3],
                'first_name': 'Emily',
                'last_name': 'Davis',
                'email': 'emily.davis@manufacturingpro.com',
                'phone': '+1-555-0501',
                'job_title': 'Procurement Manager',
                'department': 'Procurement',
                'status': 'CUSTOMER',
                'source': 'Referral',
                'address': '321 Industrial Drive, Detroit, MI 48201',
                'city': 'Detroit',
                'state': 'MI',
                'country': 'USA',
                'linkedin': 'https://linkedin.com/in/emilydavis',
                'notes': 'Long-term client relationship.',
                'tags': 'procurement,manufacturing',
            },
        ]
        
        for data in contact_data:
            contact = Contact.objects.create(**data)
            contacts.append(contact)
        
        return contacts

    def create_deals(self, users, contacts, companies):
        from deals.models import Deal, PipelineStage, Pipeline
        
        # Get pipeline stages
        pipeline = Pipeline.objects.filter(is_default=True).first()
        stages = {stage.stage_key: stage for stage in pipeline.stages.all()}
        
        deals = []
        deal_values = [
            {
                'user': users[0],
                'contact': contacts[0],
                'company': companies[0],
                'title': 'Enterprise License Deal - TechCorp',
                'description': 'Annual enterprise software license worth $250,000',
                'value': Decimal('250000'),
                'currency': 'USD',
                'source': 'Referral',
                'priority': 'HIGH',
                'stage': stages['qualified'],
                'expected_close_date': timezone.now() + timedelta(days=30),
            },
            {
                'user': users[0],
                'contact': contacts[1],
                'company': companies[0],
                'title': 'Support Contract - TechCorp',
                'description': 'Annual support and maintenance contract worth $75,000',
                'value': Decimal('75000'),
                'currency': 'USD',
                'source': 'Referral',
                'priority': 'MEDIUM',
                'stage': stages['won'],
                'expected_close_date': timezone.now() - timedelta(days=5),
            },
            {
                'user': users[0],
                'contact': contacts[2],
                'company': companies[1],
                'title': 'Marketing Campaign - Global Marketing',
                'description': 'Digital marketing campaign package - $15,000/month retainer',
                'value': Decimal('15000'),
                'currency': 'USD',
                'source': 'Cold Call',
                'priority': 'MEDIUM',
                'stage': stages['proposal'],
                'expected_close_date': timezone.now() + timedelta(days=45),
            },
            {
                'user': users[0],
                'contact': contacts[3],
                'company': companies[2],
                'title': 'AI Platform Integration - Startup Ventures',
                'description': 'Integration of AI platform for business automation',
                'value': Decimal('50000'),
                'currency': 'USD',
                'source': 'Cold Call',
                'priority': 'HIGH',
                'stage': stages['proposal'],
                'expected_close_date': timezone.now() + timedelta(days=30),
            },
            {
                'user': users[1],
                'contact': contacts[4],
                'company': companies[2],
                'title': 'Equipment Purchase - Manufacturing Pro',
                'description': 'Industrial equipment purchase - $125,000',
                'value': Decimal('125000'),
                'currency': 'USD',
                'source': 'Cold Call',
                'priority': 'HIGH',
                'stage': stages['qualified'],
                'expected_close_date': timezone.now() + timedelta(days=90),
            },
            {
                'user': users[1],
                'contact': contacts[4],
                'company': companies[2],
                'title': 'Consulting Services Contract - Manufacturing Pro',
                'description': 'Quarterly consulting services - $50,000',
                'value': Decimal('50000'),
                'currency': 'USD',
                'source': 'Referral',
                'priority': 'HIGH',
                'stage': stages['won'],
                'expected_close_date': timezone.now() - timedelta(days=10),
            },
            {
                'user': users[2],
                'contact': contacts[5],
                'company': companies[3],
                'title': 'Support Renewal - Manufacturing Pro',
                'description': 'Annual support contract renewal - $200,000',
                'value': Decimal('200000'),
                'currency': 'USD',
                'source': 'Email',
                'priority': 'MEDIUM',
                'stage': stages['won'],
                'expected_close_date': timezone.now() + timedelta(days=60),
            },
        ]
        
        for data in deal_values:
            deal = Deal.objects.create(**data)
            deals.append(deal)
            
            # Create deal activity
            from activities.models import Activity
            Activity.objects.create(
                user=data['user'],
                contact=data['contact'],
                deal=deal,
                activity_type='STAGE_CHANGE',
                description=f"Deal created in {data['stage']} stage",
                activity_date=timezone.now(),
            )
        
        return deals

    def create_activities(self, users, contacts, deals):
        from activities.models import Activity
        
        activities = []
        activity_data = [
            {
                'user': users[0],
                'contact': contacts[0],
                'deal': deals[0],
                'activity_type': 'CALL',
                'subject': 'Initial discovery call with David Miller',
                'description': 'Discussed tech needs and explored opportunities for partnership.',
                'activity_date': timezone.now() - timedelta(days=14),
            },
            {
                'user': users[0],
                'contact': contacts[1],
                'deal': deals[1],
                'activity_type': 'MEETING',
                'subject': 'On-site demo presentation',
                'description': 'Presented platform capabilities and value proposition.',
                'activity_date': timezone.now() - timedelta(days=7),
            },
            {
                'user': users[1],
                'contact': contacts[2],
                'deal': deals[2],
                'activity_type': 'EMAIL',
                'subject': 'Marketing campaign proposal sent',
                'description': 'Sent detailed proposal for digital marketing campaign.',
                'activity_date': timezone.now() - timedelta(days=10),
            },
            {
                'user': users[1],
                'contact': contacts[3],
                'deal': deals[3],
                'activity_type': 'CALL',
                'subject': 'Follow-up on marketing proposal',
                'description': 'Discussed campaign details and answered questions.',
                'activity_date': timezone.now() - timedelta(days=5),
            },
            {
                'user': users[1],
                'contact': contacts[3],
                'deal': deals[4],
                'activity_type': 'CALL',
                'subject': 'Product requirements discussion',
                'description': 'Met with engineering team to discuss AI integration requirements.',
                'activity_date': timezone.now() - timedelta(days=20),
            },
            {
                'user': users[2],
                'contact': contacts[4],
                'deal': deals[4],
                'activity_type': 'MEETING',
                'subject': 'Contract negotiation meeting',
                'description': 'Negotiated terms and conditions for equipment purchase.',
                'activity_date': timezone.now() - timedelta(days=3),
                'status': 'COMPLETED',
                'outcome': 'Contract signed - $125,000',
            },
            {
                'user': users[2],
                'contact': contacts[4],
                'deal': None,
                'activity_type': 'EMAIL',
                'subject': 'Contract sent for signature',
                'description': 'Sent final contract documents to Manufacturing Pro.',
                'activity_date': timezone.now() - timedelta(days=2),
            },
            {
                'user': users[2],
                'contact': contacts[5],
                'deal': deals[5],
                'activity_type': 'NOTE',
                'subject': 'Support renewal reminder',
                'description': 'Set reminder for annual support contract renewal.',
                'activity_date': timezone.now() - timedelta(days=30),
                'priority': 'URGENT',
            },
            {
                'user': users[0],
                'contact': contacts[0],
                'deal': None,
                'activity_type': 'CALL',
                'subject': 'Contract renewal discussion',
                'description': 'Called to discuss renewal terms and renewal discount.',
                'activity_date': timezone.now() - timedelta(days=7),
            },
            {
                'user': users[0],
                'contact': contacts[1],
                'deal': deals[1],
                'activity_type': 'MEETING',
                'subject': 'Contract renewal meeting',
                'description': 'Meeting with Sarah to discuss renewal options and upsell opportunities.',
                'activity_date': timezone.now() - timedelta(days=14),
                'status': 'COMPLETED',
                'outcome': 'Renewed for $80,000 - discount applied',
            },
            {
                'user': users[0],
                'contact': contacts[1],
                'deal': None,
                'activity_type': 'NOTE',
                'subject': 'Renewed contract documentation',
                'description': 'Updated CRM with renewed contract details.',
                'activity_date': timezone.now() - timedelta(days=2),
            },
            {
                'user': users[0],
                'contact': contacts[3],
                'deal': None,
                'activity_type': 'EMAIL',
                'subject': 'Cold outreach to new prospect',
                'description': 'Sent introduction email to Robert Garcia at Startup Ventures.',
                'activity_date': timezone.now() - timedelta(days=21),
            },
            {
                'user': users[1],
                'contact': contacts[3],
                'deal': None,
                'activity_type': 'CALL',
                'subject': 'Discovery call - Startup Ventures',
                'description': 'Had initial discovery call discussing their business model and needs.',
                'activity_date': timezone.now() - timedelta(days=18),
            },
            {
                'user': users[1],
                'contact': contacts[4],
                'deal': None,
                'activity_type': 'MEETING',
                'subject': 'Technical feasibility call',
                'description': 'Discussed technical requirements and implementation timeline.',
                'activity_date': timezone.now() - timedelta(days=15),
            },
        ]
        
        for data in activity_data:
            activity = Activity.objects.create(**data)
            activities.append(activity)
        
        return activities
