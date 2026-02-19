from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from jobs.models import (
    Job, JobCategory, JobApplication, SavedJob, Skill, CandidateSkill,
    WorkExperience, Education, JobMatch, CandidateRecommendation,
    Notification, InterviewQuestion, InterviewSession, InterviewResponse
)
from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Populate database with comprehensive dummy data for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting dummy data population...'))

        # Create interview questions
        self.create_interview_questions()

        # Create sample skills
        self.create_skills()

        # Create sample interview sessions with responses
        self.create_interview_sessions()

        # Create saved jobs
        self.create_saved_jobs()

        # Create notifications
        self.create_notifications()

        # Create job matches and recommendations
        self.create_matches_and_recommendations()

        self.stdout.write(self.style.SUCCESS('[OK] Dummy data population complete!'))

    def create_interview_questions(self):
        """Create interview questions for different categories"""
        self.stdout.write('Creating interview questions...')

        questions_data = [
            # Technical Questions
            {
                'question_type': 'technical',
                'difficulty': 'medium',
                'question': 'Explain your experience with RESTful APIs and how you have implemented them in your projects.',
                'expected_keywords': ['REST', 'API', 'HTTP', 'endpoint', 'JSON', 'GET', 'POST', 'implementation'],
                'max_score': 10,
                'sample_answer': 'I have extensive experience building RESTful APIs using frameworks like Django REST Framework and Express.js. I follow REST principles including proper HTTP methods, status codes, and resource-based URLs. In my last project, I implemented a complete API with authentication, pagination, and error handling.'
            },
            {
                'question_type': 'technical',
                'difficulty': 'hard',
                'question': 'Describe your approach to database optimization and how you handle slow queries.',
                'expected_keywords': ['index', 'query', 'optimization', 'performance', 'database', 'SQL', 'explain', 'analysis'],
                'max_score': 10,
                'sample_answer': 'I start by analyzing slow queries using EXPLAIN and profiling tools. Common optimization strategies include adding appropriate indexes, rewriting queries to avoid N+1 problems, using JOINs efficiently, and implementing caching strategies. I also consider database denormalization for read-heavy workloads.'
            },
            {
                'question_type': 'technical',
                'difficulty': 'easy',
                'question': 'What version control systems have you used and describe your branching strategy.',
                'expected_keywords': ['Git', 'version control', 'branch', 'merge', 'pull request', 'workflow', 'commit'],
                'max_score': 10,
                'sample_answer': 'I use Git daily for version control. My preferred workflow is Git Flow with feature branches for development, develop branch for integration, and main for production. I regularly create pull requests for code review before merging.'
            },

            # Behavioral Questions
            {
                'question_type': 'behavioral',
                'difficulty': 'medium',
                'question': 'Tell me about a time you had a conflict with a team member. How did you resolve it?',
                'expected_keywords': ['conflict', 'resolve', 'communication', 'team', 'understand', 'compromise', 'professional'],
                'max_score': 10,
                'sample_answer': 'I had a disagreement with a colleague about the technical approach for a feature. I scheduled a private meeting to understand their perspective, explained my reasoning, and we found a middle ground that incorporated both ideas. This actually led to a better solution.'
            },
            {
                'question_type': 'behavioral',
                'difficulty': 'medium',
                'question': 'Describe a situation where you had to learn a new technology quickly to complete a project.',
                'expected_keywords': ['learn', 'technology', 'quickly', 'research', 'practice', 'documentation', 'adapt'],
                'max_score': 10,
                'sample_answer': 'In my previous role, we needed to implement real-time features using WebSocket. I had no prior experience, so I spent my weekends learning the technology, built a proof of concept, and successfully implemented it within two weeks.'
            },

            # Situational Questions
            {
                'question_type': 'situational',
                'difficulty': 'medium',
                'question': 'You discover a critical bug in production just before a deadline. What do you do?',
                'expected_keywords': ['bug', 'deadline', 'prioritize', 'communicate', 'fix', 'team', 'transparent'],
                'max_score': 10,
                'sample_answer': 'I would immediately assess the severity and impact, communicate with stakeholders about the issue, and propose options. If critical, I would recommend delaying the release to fix it. If minor, I might document it for a patch release while meeting the deadline.'
            },
            {
                'question_type': 'situational',
                'difficulty': 'hard',
                'question': 'Your manager wants you to implement a feature you believe is technically flawed. How do you handle this?',
                'expected_keywords': ['communicate', 'explain', 'alternative', 'compromise', 'professional', 'concerns', 'evidence'],
                'max_score': 10,
                'sample_answer': 'I would schedule a meeting to discuss my concerns respectfully, providing technical evidence and suggesting alternatives. If they still want to proceed, I would document my concerns but implement it to the best of my ability, ensuring it\'s as robust as possible.'
            },

            # Experience Questions
            {
                'question_type': 'experience',
                'difficulty': 'easy',
                'question': 'Walk me through your most challenging project and what made it challenging.',
                'expected_keywords': ['project', 'challenging', 'challenge', 'overcome', 'solution', 'learned', 'result'],
                'max_score': 10,
                'sample_answer': 'My most challenging project was building a real-time analytics dashboard processing millions of events daily. The challenges were handling high throughput, data accuracy, and real-time updates. I implemented a distributed architecture with message queues and optimized database queries.'
            },
            {
                'question_type': 'experience',
                'difficulty': 'medium',
                'question': 'What has been your biggest professional failure and what did you learn from it?',
                'expected_keywords': ['failure', 'learn', 'mistake', 'improve', 'reflect', 'growth', 'experience'],
                'max_score': 10,
                'sample_answer': 'Early in my career, I didn\'t communicate clearly about timeline risks, leading to a missed deadline. I learned the importance of proactive communication and under-promising while over-delivering. Now I always provide regular updates and raise concerns early.'
            },
            {
                'question_type': 'experience',
                'difficulty': 'easy',
                'question': 'Why do you want to work for our company specifically?',
                'expected_keywords': ['company', 'interested', 'mission', 'values', 'grow', 'contribute', 'culture'],
                'max_score': 10,
                'sample_answer': 'I admire your company\'s innovative approach to solving industry problems. Your focus on work-life balance and professional development aligns with my values. I believe my skills would be a great fit for your team and I\'m excited about the projects you\'re working on.'
            },

            # MCQ Questions
            {
                'question_type': 'mcq',
                'difficulty': 'easy',
                'question': 'What does HTTP stand for?',
                'choices': ['HyperText Transfer Protocol', 'HighText Transfer Protocol', 'HyperText Transmission Protocol', 'HighText Transmission Protocol'],
                'correct_answer': 'HyperText Transfer Protocol',
                'max_score': 10,
                'expected_keywords': ['HTTP', 'protocol', 'transfer'],
            },
            {
                'question_type': 'mcq',
                'difficulty': 'medium',
                'question': 'Which of the following is NOT a NoSQL database?',
                'choices': ['MongoDB', 'PostgreSQL', 'Redis', 'Cassandra'],
                'correct_answer': 'PostgreSQL',
                'max_score': 10,
                'expected_keywords': ['NoSQL', 'database', 'SQL', 'PostgreSQL'],
            },
            {
                'question_type': 'mcq',
                'difficulty': 'medium',
                'question': 'What is the time complexity of binary search?',
                'choices': ['O(n)', 'O(log n)', 'O(n log n)', 'O(1)'],
                'correct_answer': 'O(log n)',
                'max_score': 10,
                'expected_keywords': ['binary', 'search', 'complexity', 'algorithm'],
            },
        ]

        # Get or create categories
        tech_category, _ = JobCategory.objects.get_or_create(
            name='Technology',
            defaults={'description': 'Software development and IT jobs'}
        )

        for q in questions_data:
            InterviewQuestion.objects.get_or_create(
                question=q['question'],
                defaults={
                    'category': tech_category,
                    'question_type': q['question_type'],
                    'difficulty': q['difficulty'],
                    'expected_keywords': q['expected_keywords'],
                    'sample_answer': q.get('sample_answer', ''),
                    'max_score': q['max_score'],
                    'choices': q.get('choices', []),
                    'correct_answer': q.get('correct_answer', ''),
                    'is_active': True
                }
            )

        self.stdout.write(f'  [OK] Created {len(questions_data)} interview questions')

    def create_skills(self):
        """Create sample skills"""
        self.stdout.write('Creating skills...')

        skills = [
            # Programming Languages
            'Python', 'JavaScript', 'Java', 'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Swift', 'Kotlin',
            'TypeScript', 'Rust', 'Scala', 'R', 'MATLAB', 'Perl', 'Shell', 'SQL', 'HTML', 'CSS',

            # Frameworks & Libraries
            'Django', 'Flask', 'FastAPI', 'React', 'Angular', 'Vue.js', 'Node.js', 'Express',
            'Spring Boot', 'ASP.NET', 'Laravel', 'Rails', 'jQuery', 'Bootstrap', 'TensorFlow',

            # Databases
            'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Oracle', 'SQL Server',
            'SQLite', 'Cassandra', 'DynamoDB', 'Firebase',

            # Cloud & DevOps
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'Git', 'CI/CD',
            'Terraform', 'Ansible', 'Linux', 'Nginx', 'Apache',

            # Other
            'Machine Learning', 'Data Science', 'API Design', 'Microservices', 'Agile',
            'Scrum', 'Project Management', 'Leadership', 'Communication', 'Problem Solving'
        ]

        tech_category = JobCategory.objects.filter(name='Technology').first()

        skill_objects = {}
        for skill_name in skills:
            skill, created = Skill.objects.get_or_create(
                name=skill_name,
                defaults={'category': tech_category, 'description': f'{skill_name} skill'}
            )
            skill_objects[skill_name] = skill

        self.stdout.write(f'  [OK] Created {len(skills)} skills')

        # Create candidate skills for job seekers
        self.create_candidate_skills(skill_objects)

    def create_interview_sessions(self):
        """Create sample interview sessions"""
        self.stdout.write('Creating interview sessions...')

        # Get users
        job_seekers = UserProfile.objects.filter(user_type='job_seeker')[:3]
        jobs = Job.objects.filter(status='active')[:3]
        questions = list(InterviewQuestion.objects.all()[:5])

        if not job_seekers.exists() or not jobs.exists():
            self.stdout.write(self.style.WARNING('  [!] No job seekers or jobs found. Skipping interview sessions.'))
            return

        for profile in job_seekers:
            for job in jobs:
                # Create interview session
                session, created = InterviewSession.objects.get_or_create(
                    job=job,
                    candidate=profile.user,
                    defaults={
                        'status': 'completed',
                        'total_score': 75,
                        'max_score': 100,
                        'percentage': 75.00,
                        'feedback': 'Good performance overall. Strong technical skills demonstrated.',
                        'completed_at': timezone.now() - timedelta(days=1),
                        'time_limit_minutes': 30
                    }
                )

                if created:
                    # Add responses for each question
                    for question in questions:
                        score = max(5, min(10, 7 + (hash(session.id + question.id) % 4)))
                        InterviewResponse.objects.create(
                            interview_session=session,
                            question=question,
                            answer=f"This is a sample answer to the question: {question.question[:50]}... I have experience with this topic and can demonstrate my knowledge through practical examples.",
                            score=score,
                            max_score=10,
                            feedback="Good answer with relevant details provided.",
                            keywords_found=question.expected_keywords[:3],
                            time_taken_seconds=120 + (hash(question.id) % 180)
                        )

        self.stdout.write(f'  [OK] Created interview sessions')

    def create_saved_jobs(self):
        """Create sample saved jobs for job seekers"""
        self.stdout.write('Creating saved jobs...')

        # Get job seekers and active jobs
        job_seekers = UserProfile.objects.filter(user_type='job_seeker')
        active_jobs = Job.objects.filter(status='active')

        if not job_seekers.exists() or not active_jobs.exists():
            self.stdout.write(self.style.WARNING('  [!] No job seekers or jobs found. Skipping saved jobs.'))
            return

        saved_count = 0
        for profile in job_seekers:
            # Save 3-5 random jobs for each job seeker
            user_jobs = active_jobs.order_by('?')[:5]
            for job in user_jobs:
                saved_job, created = SavedJob.objects.get_or_create(
                    user=profile.user,
                    job=job
                )
                if created:
                    saved_count += 1

        self.stdout.write(f'  [OK] Created {saved_count} saved jobs')

    def create_candidate_skills(self, skill_objects):
        """Create sample candidate skills for job seekers"""
        self.stdout.write('Creating candidate skills...')

        # Common skill combinations for different profiles
        skill_profiles = {
            'fullstack': ['Python', 'JavaScript', 'Django', 'React', 'SQL', 'Git', 'API Design', 'Agile'],
            'frontend': ['JavaScript', 'React', 'HTML', 'CSS', 'TypeScript', 'Angular', 'Bootstrap', 'Git'],
            'backend': ['Python', 'Django', 'Flask', 'FastAPI', 'PostgreSQL', 'Redis', 'Docker', 'API Design'],
            'devops': ['Docker', 'Kubernetes', 'Jenkins', 'Git', 'CI/CD', 'Linux', 'AWS', 'Ansible', 'Terraform'],
            'data': ['Python', 'SQL', 'PostgreSQL', 'Machine Learning', 'Data Science', 'TensorFlow', 'R'],
            'mobile': ['Swift', 'Kotlin', 'React', 'JavaScript', 'Mobile Development'],
            'general': ['Python', 'JavaScript', 'SQL', 'Git', 'Agile', 'Scrum', 'Communication', 'Problem Solving']
        }

        levels = ['beginner', 'intermediate', 'advanced', 'expert']

        job_seekers = UserProfile.objects.filter(user_type='job_seeker')[:5]

        skills_count = 0
        for idx, profile in enumerate(job_seekers):
            # Assign a skill profile based on index
            profile_type = list(skill_profiles.keys())[idx % len(skill_profiles)]
            user_skills = skill_profiles[profile_type]

            for skill_name in user_skills:
                if skill_name in skill_objects:
                    CandidateSkill.objects.get_or_create(
                        user_profile=profile,
                        skill=skill_objects[skill_name],
                        defaults={
                            'level': levels[idx % len(levels)],
                            'years_of_experience': 1 + (idx * 2),
                            'verified': True
                        }
                    )
                    skills_count += 1

        self.stdout.write(f'  [OK] Created {skills_count} candidate skills')

    def create_notifications(self):
        """Create sample notifications"""
        self.stdout.write('Creating notifications...')

        users = User.objects.all()[:5]

        notification_types = [
            ('job_application', 'New Job Application', 'A new candidate has applied for your job posting.', '/jobs/1/applicants/'),
            ('job_recommendation', 'New Job Recommendation', 'Based on your profile, we found a job match for you!', '/jobs/1/'),
            ('application_status', 'Application Status Update', 'Your application status has been updated to "Reviewed".', '/applications/'),
            ('interview_invitation', 'Interview Invitation', 'You have been invited for an interview!', '/interview/1/'),
        ]

        for user in users:
            for notif_type, title, message, link in notification_types:
                Notification.objects.get_or_create(
                    recipient=user,
                    notification_type=notif_type,
                    title=title,
                    defaults={
                        'message': message,
                        'link': link,
                        'is_read': False
                    }
                )

        self.stdout.write(f'  [OK] Created notifications')

    def create_matches_and_recommendations(self):
        """Create job matches and candidate recommendations"""
        self.stdout.write('Creating matches and recommendations...')

        # Get active jobs and users
        jobs = Job.objects.filter(status='active')
        job_seekers = UserProfile.objects.filter(user_type='job_seeker')

        for job in jobs:
            for profile in job_seekers[:3]:
                # Create job matches
                JobMatch.objects.get_or_create(
                    job=job,
                    candidate=profile.user,
                    defaults={
                        'match_score': 65 + (hash(job.id + profile.id) % 30),
                        'match_reasons': '{"skills": "Python, Django match", "experience": "3 years relevant experience", "location": "Same city"}'
                    }
                )

                # Create recommendations
                CandidateRecommendation.objects.get_or_create(
                    user=profile.user,
                    job=job,
                    defaults={
                        'score': 70 + (hash(profile.id + job.id) % 25),
                        'reason': f"Based on your skills in Python and Django, this {job.title} position is a great match for your profile.",
                        'status': 'new'
                    }
                )

        self.stdout.write(f'  [OK] Created job matches and recommendations')
