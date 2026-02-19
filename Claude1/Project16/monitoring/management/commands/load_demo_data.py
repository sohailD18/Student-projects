from django.core.management.base import BaseCommand
from monitoring.models import Student, Exam, Question, Choice
import random


class Command(BaseCommand):
    help = 'Load demo data for EduProctor system'

    def handle(self, *args, **kwargs):
        self.stdout.write('Loading demo data...')

        # Create demo students
        students_data = [
            {'name': 'John Smith', 'student_id': 'STU001'},
            {'name': 'Emily Johnson', 'student_id': 'STU002'},
            {'name': 'Michael Brown', 'student_id': 'STU003'},
            {'name': 'Sarah Davis', 'student_id': 'STU004'},
            {'name': 'David Wilson', 'student_id': 'STU005'},
            {'name': 'Jessica Martinez', 'student_id': 'STU006'},
            {'name': 'Chris Taylor', 'student_id': 'STU007'},
            {'name': 'Amanda Anderson', 'student_id': 'STU008'},
        ]

        for student_data in students_data:
            student, created = Student.objects.get_or_create(
                student_id=student_data['student_id'],
                defaults={'name': student_data['name']}
            )
            if created:
                self.stdout.write(f'Created student: {student.name}')

        # Create demo exams
        exams_data = [
            {
                'subject': 'Python Programming Fundamentals',
                'duration': 30,
                'instructions': 'Answer all questions carefully. No external resources allowed.',
                'passing_score': 60,
                'questions': [
                    {
                        'question': 'What is the correct file extension for Python files?',
                        'choices': ['.python', '.py', '.pt', '.pyt'],
                        'correct': '.py'
                    },
                    {
                        'question': 'Which keyword is used to define a function in Python?',
                        'choices': ['function', 'def', 'func', 'define'],
                        'correct': 'def'
                    },
                    {
                        'question': 'What is the output of print(2 ** 3)?',
                        'choices': ['6', '8', '9', '5'],
                        'correct': '8'
                    },
                    {
                        'question': 'Which data type is immutable in Python?',
                        'choices': ['List', 'Dictionary', 'Tuple', 'Set'],
                        'correct': 'Tuple'
                    },
                    {
                        'question': 'What does the len() function do?',
                        'choices': ['Returns length', 'Returns type', 'Returns value', 'Returns memory'],
                        'correct': 'Returns length'
                    }
                ]
            },
            {
                'subject': 'Data Structures and Algorithms',
                'duration': 45,
                'instructions': 'This test covers basic data structures and algorithm analysis.',
                'passing_score': 50,
                'questions': [
                    {
                        'question': 'What is the time complexity of binary search?',
                        'choices': ['O(n)', 'O(log n)', 'O(n²)', 'O(1)'],
                        'correct': 'O(log n)'
                    },
                    {
                        'question': 'Which data structure uses LIFO?',
                        'choices': ['Queue', 'Stack', 'Array', 'Tree'],
                        'correct': 'Stack'
                    },
                    {
                        'question': 'What is a linked list?',
                        'choices': ['Linear data structure', 'Non-linear structure', 'Graph type', 'Tree type'],
                        'correct': 'Linear data structure'
                    },
                    {
                        'question': 'What is the worst-case time complexity of quicksort?',
                        'choices': ['O(n)', 'O(n log n)', 'O(n²)', 'O(log n)'],
                        'correct': 'O(n²)'
                    },
                    {
                        'question': 'Which traversal visits root first?',
                        'choices': ['Inorder', 'Preorder', 'Postorder', 'Level order'],
                        'correct': 'Preorder'
                    }
                ]
            },
            {
                'subject': 'Web Development Basics',
                'duration': 25,
                'instructions': 'Test your knowledge of HTML, CSS, and JavaScript fundamentals.',
                'passing_score': 40,
                'questions': [
                    {
                        'question': 'What does HTML stand for?',
                        'choices': ['Hyper Text Markup Language', 'High Tech Modern Language', 'Hyper Transfer Markup Language', 'Home Tool Markup Language'],
                        'correct': 'Hyper Text Markup Language'
                    },
                    {
                        'question': 'Which CSS property changes text color?',
                        'choices': ['text-color', 'font-color', 'color', 'text-style'],
                        'correct': 'color'
                    },
                    {
                        'question': 'What symbol is used for ID selectors in CSS?',
                        'choices': ['.', '#', '@', '*'],
                        'correct': '#'
                    },
                    {
                        'question': 'Which keyword declares a variable in JavaScript?',
                        'choices': ['variable', 'var', 'v', 'declare'],
                        'correct': 'var'
                    },
                    {
                        'question': 'What is the purpose of the <alt> attribute in images?',
                        'choices': ['Animation', 'Alternative text', 'Alignment', 'Audio'],
                        'correct': 'Alternative text'
                    }
                ]
            },
            {
                'subject': 'Database Management Systems',
                'duration': 35,
                'instructions': 'This exam covers SQL and database concepts.',
                'passing_score': 55,
                'questions': [
                    {
                        'question': 'What does SQL stand for?',
                        'choices': ['Structured Query Language', 'Simple Query Language', 'Standard Query Language', 'Structured Question Language'],
                        'correct': 'Structured Query Language'
                    },
                    {
                        'question': 'Which command retrieves data from a database?',
                        'choices': ['GET', 'FETCH', 'SELECT', 'RETRIEVE'],
                        'correct': 'SELECT'
                    },
                    {
                        'question': 'What is a primary key?',
                        'choices': ['First column', 'Unique identifier', 'Foreign key', 'Index'],
                        'correct': 'Unique identifier'
                    },
                    {
                        'question': 'Which JOIN returns all records from both tables?',
                        'choices': ['INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'FULL OUTER JOIN'],
                        'correct': 'FULL OUTER JOIN'
                    },
                    {
                        'question': 'What command deletes a table?',
                        'choices': ['REMOVE', 'DELETE', 'DROP', 'CLEAR'],
                        'correct': 'DROP'
                    }
                ]
            }
        ]

        for exam_data in exams_data:
            # Create exam
            exam, created = Exam.objects.get_or_create(
                subject=exam_data['subject'],
                defaults={
                    'duration': exam_data['duration'],
                    'instructions': exam_data['instructions'],
                    'passing_score': exam_data['passing_score'],
                    'created_by': 'System'
                }
            )

            if created:
                self.stdout.write(f'Created exam: {exam.subject}')

                # Create questions for this exam
                for idx, q_data in enumerate(exam_data['questions'], start=1):
                    question = Question.objects.create(
                        exam=exam,
                        question_text=q_data['question'],
                        order=idx
                    )

                    # Create choices
                    for c_idx, choice_text in enumerate(q_data['choices'], start=1):
                        is_correct = (choice_text == q_data['correct'])
                        Choice.objects.create(
                            question=question,
                            choice_text=choice_text,
                            is_correct=is_correct,
                            order=c_idx
                        )

                self.stdout.write(f'  - Added {len(exam_data["questions"])} questions')
            else:
                self.stdout.write(f'Exam already exists: {exam.subject}')

        self.stdout.write(self.style.SUCCESS('Demo data loaded successfully!'))
        self.stdout.write('\nDemo Credentials:')
        self.stdout.write('  Students: STU001 - STU008')
        self.stdout.write('  Password: Any name matching the student ID')
