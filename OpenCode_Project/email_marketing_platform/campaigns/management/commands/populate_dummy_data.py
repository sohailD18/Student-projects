from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from campaigns.models import EmailList, Subscriber, EmailTemplate, Campaign, EmailLog, EmailAnalytics
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Populate the database with dummy data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Populating dummy data...')

        # Get admin user
        admin_user = User.objects.get(username='admin')

        # Create Email Lists
        self.stdout.write('Creating email lists...')
        lists_data = [
            {'name': 'Newsletter Subscribers', 'description': 'General newsletter subscribers'},
            {'name': 'Premium Customers', 'description': 'High-value customers'},
            {'name': 'New Leads', 'description': 'Recently acquired leads'},
            {'name': 'Inactive Users', 'description': 'Users who haven\'t engaged recently'},
        ]

        email_lists = []
        for list_data in lists_data:
            email_list, created = EmailList.objects.get_or_create(
                name=list_data['name'],
                defaults={'description': list_data['description']}
            )
            email_lists.append(email_list)
            if created:
                self.stdout.write(f'  Created: {email_list.name}')

        # Create Subscribers
        self.stdout.write('Creating subscribers...')
        first_names = ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda',
                       'David', 'Elizabeth', 'William', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica',
                       'Thomas', 'Sarah', 'Charles', 'Karen', 'Christopher', 'Nancy', 'Daniel', 'Lisa']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
                     'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson']
        domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'company.com', 'work.org']

        subscribers = []
        for i in range(50):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            email = f'{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@{random.choice(domains)}'

            subscriber, created = Subscriber.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'status': random.choice(['active', 'active', 'active', 'pending', 'unsubscribed']),
                    'is_active': random.choice([True, True, True, False])
                }
            )

            # Add to random lists
            if created:
                num_lists = random.randint(1, 3)
                for email_list in random.sample(email_lists, num_lists):
                    subscriber.email_list.add(email_list)
                subscribers.append(subscriber)

        self.stdout.write(f'  Created {len(subscribers)} subscribers')

        # Create Email Templates
        self.stdout.write('Creating email templates...')
        templates_data = [
            {
                'name': 'Welcome Email',
                'subject': 'Welcome to Our Newsletter! 🎉',
                'html_content': '''
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #4f46e5, #7c3aed); color: white; padding: 30px; text-align: center; border-radius: 10px; }
        .content { padding: 30px 0; }
        .button { display: inline-block; padding: 15px 30px; background: #4f46e5; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
        .footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome {{ first_name }}! 👋</h1>
        </div>
        <div class="content">
            <h2>We\'re So Glad You\'re Here!</h2>
            <p>Thank you for subscribing to our newsletter. We\'re excited to share amazing content with you.</p>
            <p>Here\'s what you can expect:</p>
            <ul>
                <li>Weekly tips and tricks</li>
                <li>Exclusive offers and discounts</li>
                <li>Early access to new features</li>
            </ul>
            <a href="#" class="button">Get Started</a>
            <p>If you have any questions, feel free to reach out to us.</p>
        </div>
        <div class="footer">
            <p>&copy; 2025 Your Company. All rights reserved.</p>
        </div>
    </div>
</body>
</html>''',
                'text_content': 'Hi {{ first_name }},\n\nWelcome to our newsletter! We\'re excited to have you on board.\n\nBest regards,\nThe Team'
            },
            {
                'name': 'Product Launch',
                'subject': 'Introducing Our New Product! 🚀',
                'html_content': '''
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 30px; text-align: center; border-radius: 10px; }
        .product { background: #f9fafb; padding: 30px; border-radius: 10px; margin: 20px 0; }
        .button { display: inline-block; padding: 15px 30px; background: #10b981; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 New Product Launch!</h1>
            <p>Something amazing is here</p>
        </div>
        <div class="product">
            <h2>Introducing: SuperProduct X</h2>
            <p>Dear {{ first_name }},</p>
            <p>We\'re thrilled to announce the launch of our latest product! SuperProduct X is designed to revolutionize the way you work.</p>
            <h3>Key Features:</h3>
            <ul>
                <li>✨ Feature 1: Amazing capability</li>
                <li>⚡ Feature 2: Lightning fast</li>
                <li>🎯 Feature 3: Precise results</li>
                <li>💪 Feature 4: Powerful performance</li>
            </ul>
            <p><strong>Special Launch Price: $99 (Regular $149)</strong></p>
            <center><a href="#" class="button">Buy Now - Save 33%</a></center>
        </div>
    </div>
</body>
</html>''',
                'text_content': 'Hi {{ first_name }},\n\nCheck out our new product SuperProduct X!\n\nSpecial launch price: $99\n\nBuy now!'
            },
            {
                'name': 'Weekly Newsletter',
                'subject': 'Your Weekly Digest 📰',
                'html_content': '''
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #f59e0b, #d97706); color: white; padding: 30px; text-align: center; border-radius: 10px; }
        .article { border-bottom: 1px solid #e5e7eb; padding: 20px 0; }
        .article:last-child { border-bottom: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📰 Weekly Digest</h1>
            <p>This week\'s top stories</p>
        </div>
        <div class="article">
            <h3>🎯 Article 1: 10 Tips for Success</h3>
            <p>Learn the secrets of successful people and how you can apply them to your life...</p>
            <a href="#">Read more →</a>
        </div>
        <div class="article">
            <h3>💡 Article 2: Innovation in 2025</h3>
            <p>Discover the latest trends and innovations that are shaping our future...</p>
            <a href="#">Read more →</a>
        </div>
        <div class="article">
            <h3>📊 Article 3: Market Insights</h3>
            <p>Our analysis of the current market trends and what they mean for you...</p>
            <a href="#">Read more →</a>
        </div>
        <p style="text-align: center; color: #666; margin-top: 30px;">
            See you next week!<br>
            The Team
        </p>
    </div>
</body>
</html>''',
                'text_content': 'Hi {{ first_name }},\n\nHere\'s your weekly digest:\n\n1. 10 Tips for Success\n2. Innovation in 2025\n3. Market Insights\n\nEnjoy!'
            },
            {
                'name': 'Special Offer',
                'subject': '🔥 Exclusive 50% OFF - Limited Time!',
                'html_content': '''
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .offer { background: linear-gradient(135deg, #ef4444, #dc2626); color: white; padding: 40px; text-align: center; border-radius: 10px; }
        .button { display: inline-block; padding: 20px 40px; background: white; color: #ef4444; text-decoration: none; border-radius: 5px; font-size: 18px; font-weight: bold; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="offer">
            <h1 style="font-size: 48px; margin: 0;">🔥 50% OFF</h1>
            <p style="font-size: 24px;">Just for you, {{ first_name }}!</p>
            <p style="font-size: 18px; opacity: 0.9;">Limited time offer - Expires in 24 hours</p>
        </div>
        <div style="padding: 30px 0;">
            <h2 style="color: #ef4444;">Don\'t Miss Out!</h2>
            <p>Hi {{ first_name }},</p>
            <p>We\'re offering you an exclusive 50% discount on all products. This is our biggest sale of the year!</p>
            <p style="font-size: 24px; font-weight: bold; color: #ef4444;">Use code: SAVE50</p>
            <center><a href="#" class="button">Shop Now →</a></center>
            <p style="text-align: center; color: #666; margin-top: 20px;">
                *Offer expires in 24 hours. Terms and conditions apply.
            </p>
        </div>
    </div>
</body>
</html>''',
                'text_content': 'Hi {{ first_name }},\n\nExclusive offer: 50% off everything!\nUse code: SAVE50\n\nShop now!'
            },
            {
                'name': 'Event Invitation',
                'subject': 'You\'re Invited! 🎪 Special Event',
                'html_content': '''
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .invitation { background: linear-gradient(135deg, #8b5cf6, #7c3aed); color: white; padding: 40px; text-align: center; border-radius: 10px; }
        .details { background: #f9fafb; padding: 30px; border-radius: 10px; margin: 20px 0; }
        .button { display: inline-block; padding: 15px 30px; background: #8b5cf6; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="invitation">
            <h1>🎪 You\'re Invited!</h1>
            <p>Join us for a special event</p>
        </div>
        <div class="details">
            <h2>Annual Networking Event 2025</h2>
            <p>Dear {{ first_name }},</p>
            <p>We cordially invite you to our exclusive networking event. This is a great opportunity to connect with industry leaders and like-minded professionals.</p>
            <p><strong>📅 Date:</strong> March 15, 2025</p>
            <p><strong>⏰ Time:</strong> 6:00 PM - 9:00 PM</p>
            <p><strong>📍 Location:</strong> Grand Convention Center</p>
            <p><strong>🎯 Dress Code:</strong> Business Formal</p>
            <center><a href="#" class="button">RSVP Now</a></center>
        </div>
    </div>
</body>
</html>''',
                'text_content': 'Hi {{ first_name }},\n\nYou\'re invited to our Annual Networking Event!\n\nDate: March 15, 2025\nTime: 6:00 PM\nLocation: Grand Convention Center\n\nPlease RSVP!'
            },
        ]

        templates = []
        for template_data in templates_data:
            template, created = EmailTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults={
                    'subject': template_data['subject'],
                    'html_content': template_data['html_content'],
                    'text_content': template_data['text_content'],
                    'is_active': True
                }
            )
            templates.append(template)
            if created:
                self.stdout.write(f'  Created: {template.name}')

        # Create Campaigns
        self.stdout.write('Creating campaigns...')

        # Regular campaigns
        for i in range(3):
            status = ['draft', 'scheduled', 'sent'][i]
            campaign = Campaign.objects.create(
                name=f'{random.choice(["Spring Sale", "Summer Promotion", "Fall Event", "Winter Special"])} {2025 + i}',
                email_template=random.choice(templates),
                email_list=random.choice(email_lists),
                status=status,
                created_by=admin_user,
                scheduled_at=timezone.now() + timedelta(days=random.randint(1, 30)) if status == 'scheduled' else None,
                sent_at=timezone.now() - timedelta(days=random.randint(1, 10)) if status == 'sent' else None
            )

            # Create email logs for sent campaigns
            if status == 'sent':
                subscribers_list = list(campaign.email_list.subscribers.filter(is_active=True)[:20])
                for subscriber in subscribers_list:
                    log = EmailLog.objects.create(
                        campaign=campaign,
                        subscriber=subscriber,
                        status='sent',
                        sent_at=timezone.now() - timedelta(hours=random.randint(1, 100))
                    )

                    # Create analytics
                    if random.random() > 0.3:  # 70% chance of open
                        EmailAnalytics.objects.create(
                            email_log=log,
                            opened_at=timezone.now() - timedelta(hours=random.randint(1, 50)),
                            click_count=random.randint(0, 5),
                            clicked_at=timezone.now() - timedelta(hours=random.randint(1, 30)) if random.random() > 0.5 else None
                        )

            self.stdout.write(f'  Created: {campaign.name}')

        # A/B Test Campaign
        ab_campaign = Campaign.objects.create(
            name='A/B Test: Welcome Email Optimization',
            email_template=templates[0],
            email_list=email_lists[0],
            status='sent',
            is_ab_test=True,
            ab_test_variant_a=templates[0],
            ab_test_variant_b=templates[1],
            ab_test_split_percentage=50,
            ab_test_winner=None,
            created_by=admin_user,
            sent_at=timezone.now() - timedelta(days=5)
        )

        # Create email logs for A/B test
        ab_subscribers = list(ab_campaign.email_list.subscribers.filter(is_active=True)[:30])
        for i, subscriber in enumerate(ab_subscribers):
            variant = 'A' if i < 15 else 'B'
            log = EmailLog.objects.create(
                campaign=ab_campaign,
                subscriber=subscriber,
                status='sent',
                variant=variant,
                sent_at=timezone.now() - timedelta(days=5, hours=random.randint(1, 24))
            )

            # Create analytics with different rates for variants
            open_chance = 0.8 if variant == 'A' else 0.6
            if random.random() < open_chance:
                EmailAnalytics.objects.create(
                    email_log=log,
                    opened_at=timezone.now() - timedelta(days=4, hours=random.randint(1, 24)),
                    click_count=random.randint(0, 3),
                    clicked_at=timezone.now() - timedelta(days=3, hours=random.randint(1, 24)) if random.random() > 0.6 else None
                )

        self.stdout.write(f'  Created: {ab_campaign.name} (A/B Test)')

        # Draft campaigns
        for i in range(2):
            campaign = Campaign.objects.create(
                name=f'Draft Campaign {i + 1}',
                email_template=random.choice(templates),
                email_list=random.choice(email_lists),
                status='draft',
                created_by=admin_user
            )
            self.stdout.write(f'  Created: {campaign.name}')

        self.stdout.write(self.style.SUCCESS('\n✅ Dummy data populated successfully!'))
        self.stdout.write('\nSummary:')
        self.stdout.write(f'  Email Lists: {EmailList.objects.count()}')
        self.stdout.write(f'  Subscribers: {Subscriber.objects.count()}')
        self.stdout.write(f'  Templates: {EmailTemplate.objects.count()}')
        self.stdout.write(f'  Campaigns: {Campaign.objects.count()}')
        self.stdout.write(f'  Email Logs: {EmailLog.objects.count()}')
        self.stdout.write(f'  Analytics: {EmailAnalytics.objects.count()}')
