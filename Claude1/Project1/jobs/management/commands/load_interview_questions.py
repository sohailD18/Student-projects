from django.core.management.base import BaseCommand
from jobs.models import InterviewQuestion, JobCategory, Skill


class Command(BaseCommand):
    help = 'Load sample interview questions into the database'

    def handle(self, *args, **options):
        # Sample interview questions organized by type
        questions_data = [
            {
                'question_type': 'technical',
                'difficulty': 'easy',
                'question': 'What programming languages are you most comfortable with?',
                'expected_keywords': ['python', 'java', 'javascript', 'programming', 'coding'],
                'sample_answer': 'I am most comfortable with Python and JavaScript. I have been using Python for 3 years and JavaScript for 2 years in various projects.',
                'choices': [],
                'correct_answer': '',
            },
            {
                'question_type': 'technical',
                'difficulty': 'medium',
                'question': 'Explain the difference between REST and GraphQL APIs.',
                'expected_keywords': ['api', 'rest', 'graphql', 'endpoint', 'query', 'mutation'],
                'sample_answer': 'REST uses multiple endpoints for different resources, while GraphQL uses a single endpoint with flexible queries. REST follows a stateless client-server architecture, while GraphQL allows clients to request exactly the data they need.',
                'choices': [],
                'correct_answer': '',
            },
            {
                'question_type': 'behavioral',
                'difficulty': 'medium',
                'question': 'Tell us about a time you had to work with a difficult team member.',
                'expected_keywords': ['teamwork', 'communication', 'conflict', 'collaborate', 'resolve'],
                'sample_answer': 'I had a team member who was not meeting deadlines. I scheduled a private meeting to understand their challenges and we worked together to create a plan that helped them improve.',
                'choices': [],
                'correct_answer': '',
            },
            {
                'question_type': 'situational',
                'difficulty': 'medium',
                'question': 'How would you handle a situation where you have multiple deadlines approaching?',
                'expected_keywords': ['prioritize', 'manage', 'deadline', 'communicate', 'plan'],
                'sample_answer': 'I would assess all tasks, prioritize based on urgency and importance, communicate with stakeholders if any delays are expected, and focus on completing the most critical tasks first.',
                'choices': [],
                'correct_answer': '',
            },
            {
                'question_type': 'technical',
                'difficulty': 'hard',
                'question': 'Describe your experience with database design and optimization.',
                'expected_keywords': ['database', 'sql', 'optimization', 'index', 'query', 'performance'],
                'sample_answer': 'I have designed normalized databases using PostgreSQL and MySQL. I have experience with query optimization, creating proper indexes, and using EXPLAIN to analyze query performance.',
                'choices': [],
                'correct_answer': '',
            },
            # MCQ Questions
            {
                'question_type': 'mcq',
                'difficulty': 'easy',
                'question': 'What does HTML stand for?',
                'expected_keywords': ['html', 'markup', 'language'],
                'sample_answer': 'HyperText Markup Language',
                'choices': ['HyperText Markup Language', 'High Tech Modern Language', 'HyperTransfer Markup Language', 'Home Tool Markup Language'],
                'correct_answer': 'HyperText Markup Language',
            },
            {
                'question_type': 'mcq',
                'difficulty': 'easy',
                'question': 'Which of the following is NOT a JavaScript framework?',
                'expected_keywords': ['javascript', 'framework', 'library'],
                'sample_answer': 'Python',
                'choices': ['React', 'Angular', 'Python', 'Vue.js'],
                'correct_answer': 'Python',
            },
            {
                'question_type': 'mcq',
                'difficulty': 'medium',
                'question': 'What is the time complexity of binary search?',
                'expected_keywords': ['binary', 'search', 'complexity', 'algorithm'],
                'sample_answer': 'O(log n)',
                'choices': ['O(n)', 'O(log n)', 'O(n²)', 'O(1)'],
                'correct_answer': 'O(log n)',
            },
            {
                'question_type': 'mcq',
                'difficulty': 'medium',
                'question': 'Which HTTP method is typically used to update data?',
                'expected_keywords': ['http', 'method', 'update', 'request'],
                'sample_answer': 'PUT',
                'choices': ['GET', 'POST', 'PUT', 'DELETE'],
                'correct_answer': 'PUT',
            },
            {
                'question_type': 'mcq',
                'difficulty': 'hard',
                'question': 'What is the purpose of a CSS flexbox?',
                'expected_keywords': ['css', 'flexbox', 'layout', 'alignment'],
                'sample_answer': 'To create flexible layouts and align items',
                'choices': [
                    'To add animations to elements',
                    'To create flexible layouts and align items',
                    'To connect to databases',
                    'To write JavaScript functions'
                ],
                'correct_answer': 'To create flexible layouts and align items',
            },
        ]

        created_count = 0
        skipped_count = 0

        for q_data in questions_data:
            # Create question if it doesn't exist
            question, created = InterviewQuestion.objects.get_or_create(
                question=q_data['question'],
                defaults={
                    'question_type': q_data['question_type'],
                    'difficulty': q_data['difficulty'],
                    'expected_keywords': q_data['expected_keywords'],
                    'sample_answer': q_data['sample_answer'],
                    'choices': q_data['choices'],
                    'correct_answer': q_data['correct_answer'],
                    'is_active': True,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {q_data["question"][:50]}...'))
            else:
                skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully loaded {created_count} interview questions. '
                f'{skipped_count} questions already existed.'
            )
        )
