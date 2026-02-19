from django.core.management.base import BaseCommand
from jobs.models import Skill, JobCategory


class Command(BaseCommand):
    help = 'Load common skills into the database'

    def handle(self, *args, **options):
        # Common technical skills organized by category
        skills_data = {
            'Programming Languages': [
                'Python', 'Java', 'JavaScript', 'C++', 'C#', 'PHP', 'Ruby', 'Go',
                'Swift', 'Kotlin', 'Rust', 'TypeScript', 'Scala', 'Perl', 'R', 'MATLAB'
            ],
            'Web Development': [
                'HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Django', 'Flask',
                'Express.js', 'Next.js', 'jQuery', 'Bootstrap', 'Tailwind CSS', 'SASS',
                'RESTful APIs', 'GraphQL', 'WebSocket', 'JSON', 'XML'
            ],
            'Data Science & AI': [
                'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Keras',
                'Scikit-learn', 'Pandas', 'NumPy', 'Data Analysis', 'SQL', 'MongoDB',
                'PostgreSQL', 'MySQL', 'Data Visualization', 'Tableau', 'Power BI', 'NLP',
                'Computer Vision', 'Statistics', 'A/B Testing'
            ],
            'Cloud & DevOps': [
                'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Jenkins',
                'CI/CD', 'Git', 'GitHub', 'GitLab', 'Linux', 'Bash', 'Terraform',
                'Ansible', 'Microservices', 'Serverless', 'Monitoring'
            ],
            'Mobile Development': [
                'iOS', 'Android', 'React Native', 'Flutter', 'Swift', 'Kotlin',
                'Mobile UI', 'App Store', 'Play Store', 'Xamarin', 'Ionic'
            ],
            'Design': [
                'UI/UX Design', 'Figma', 'Adobe XD', 'Sketch', 'Photoshop', 'Illustrator',
                'Wireframing', 'Prototyping', 'User Research', 'Visual Design', 'Responsive Design'
            ],
            'Project Management': [
                'Agile', 'Scrum', 'Kanban', 'Jira', 'Project Management', 'Team Leadership',
                'Stakeholder Management', 'Risk Management', 'Product Management'
            ],
            'Marketing': [
                'Digital Marketing', 'SEO', 'SEM', 'Content Marketing', 'Social Media',
                'Email Marketing', 'Google Analytics', 'Facebook Ads', 'Copywriting',
                'Brand Management', 'Marketing Strategy'
            ],
            'Business': [
                'Business Analysis', 'Financial Analysis', 'Excel', 'PowerPoint',
                'Strategic Planning', 'Business Development', 'Sales', 'CRM',
                'Negotiation', 'Presentation Skills'
            ],
            'Soft Skills': [
                'Communication', 'Leadership', 'Problem Solving', 'Teamwork',
                'Time Management', 'Critical Thinking', 'Creativity', 'Adaptability',
                'Emotional Intelligence', 'Decision Making'
            ]
        }

        created_count = 0
        skipped_count = 0

        for category_name, skills in skills_data.items():
            # Get or create category
            category, _ = JobCategory.objects.get_or_create(
                name=category_name,
                defaults={'description': f'{category_name} skills'}
            )

            for skill_name in skills:
                # Create skill if it doesn't exist
                skill, created = Skill.objects.get_or_create(
                    name=skill_name,
                    defaults={'category': category}
                )

                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Created skill: {skill_name}'))
                else:
                    skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully loaded {created_count} skills. '
                f'{skipped_count} skills already existed.'
            )
        )
