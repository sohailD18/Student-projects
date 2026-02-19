from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from jobs.models import Job, JobCategory
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Create sample job listings'

    def handle(self, *args, **kwargs):
        # Get or create a user for the jobs
        user, created = User.objects.get_or_create(
            username='demo_user',
            defaults={
                'email': 'demo@jobportal.com',
                'first_name': 'Demo',
                'last_name': 'User'
            }
        )

        if created:
            user.set_password('demo123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created demo user: demo_user / demo123'))

        # Get categories
        categories = {cat.name: cat for cat in JobCategory.objects.all()}

        # Sample job data
        jobs_data = [
            {
                'title': 'Senior Software Engineer',
                'company': 'TechCorp Inc.',
                'location': 'San Francisco, CA',
                'category': categories.get('Software Development'),
                'job_type': 'full_time',
                'experience_level': 'senior',
                'description': 'We are looking for a Senior Software Engineer to join our dynamic team. You will be responsible for designing and implementing scalable software solutions, mentoring junior developers, and collaborating with cross-functional teams.',
                'requirements': '5+ years of experience in software development\nProficiency in Python, JavaScript, and React\nExperience with cloud platforms (AWS/GCP)\nStrong problem-solving skills\nExcellent communication abilities',
                'salary_min': 120000,
                'salary_max': 180000,
                'is_salary_visible': True,
                'application_deadline': datetime.now().date() + timedelta(days=30),
            },
            {
                'title': 'Data Scientist',
                'company': 'DataDriven Analytics',
                'location': 'New York, NY',
                'category': categories.get('Data Science'),
                'job_type': 'full_time',
                'experience_level': 'mid',
                'description': 'Join our data science team to build machine learning models and drive data-driven decisions. You will work on challenging problems in predictive analytics and natural language processing.',
                'requirements': '3+ years of experience in data science\nStrong Python and SQL skills\nExperience with ML frameworks (TensorFlow, PyTorch)\nKnowledge of statistical analysis\nPhD or Master\'s degree in related field preferred',
                'salary_min': 100000,
                'salary_max': 150000,
                'is_salary_visible': True,
                'application_deadline': datetime.now().date() + timedelta(days=25),
            },
            {
                'title': 'UI/UX Designer',
                'company': 'Creative Studio',
                'location': 'Remote',
                'category': categories.get('Design'),
                'job_type': 'remote',
                'experience_level': 'mid',
                'description': 'We are seeking a talented UI/UX Designer to create beautiful and intuitive user interfaces. You will work closely with product managers and developers to deliver exceptional user experiences.',
                'requirements': '3+ years of UI/UX design experience\nProficiency in Figma and Adobe Creative Suite\nStrong portfolio demonstrating design process\nUnderstanding of user-centered design principles\nExcellent communication skills',
                'salary_min': 80000,
                'salary_max': 120000,
                'is_salary_visible': True,
                'application_deadline': datetime.now().date() + timedelta(days=20),
            },
            {
                'title': 'Marketing Manager',
                'company': 'GrowthHub',
                'location': 'Chicago, IL',
                'category': categories.get('Marketing'),
                'job_type': 'full_time',
                'experience_level': 'senior',
                'description': 'Lead our marketing efforts and drive brand awareness. You will develop and execute marketing strategies across multiple channels to acquire and retain customers.',
                'requirements': '5+ years of marketing experience\nProven track record in digital marketing\nExperience with marketing automation tools\nStrong analytical and leadership skills\nMBA preferred',
                'salary_min': 90000,
                'salary_max': 140000,
                'is_salary_visible': True,
                'application_deadline': datetime.now().date() + timedelta(days=35),
            },
            {
                'title': 'Frontend Developer Intern',
                'company': 'StartUp Labs',
                'location': 'Austin, TX',
                'category': categories.get('Software Development'),
                'job_type': 'internship',
                'experience_level': 'entry',
                'description': 'Join our team as a Frontend Developer Intern and gain hands-on experience building modern web applications. Perfect for students or recent graduates looking to start their career.',
                'requirements': 'Currently pursuing or recently completed CS degree\nBasic knowledge of HTML, CSS, and JavaScript\nEagerness to learn and grow\nGood problem-solving skills\nAbility to work in a team environment',
                'salary_min': 30000,
                'salary_max': 45000,
                'is_salary_visible': False,
                'application_deadline': datetime.now().date() + timedelta(days=15),
            },
            {
                'title': 'Product Manager',
                'company': 'InnovateTech',
                'location': 'Seattle, WA',
                'category': categories.get('Management'),
                'job_type': 'full_time',
                'experience_level': 'senior',
                'description': 'Drive product strategy and roadmap for our SaaS platform. You will work with engineering, design, and business teams to deliver products that delight customers.',
                'requirements': '5+ years of product management experience\nTechnical background preferred\nStrong analytical and communication skills\nExperience with Agile methodologies\nTrack record of shipping successful products',
                'salary_min': 130000,
                'salary_max': 180000,
                'is_salary_visible': True,
                'application_deadline': datetime.now().date() + timedelta(days=40),
            },
        ]

        created_count = 0
        for job_data in jobs_data:
            job, created = Job.objects.get_or_create(
                title=job_data['title'],
                company=job_data['company'],
                defaults={
                    **job_data,
                    'created_by': user,
                    'status': 'active'
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created job: {job.title} at {job.company}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Job already exists: {job.title}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created {created_count} new jobs!')
        )
