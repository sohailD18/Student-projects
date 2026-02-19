"""
OptiFlow - AI-Based Business Process Optimizer
Custom Management Command to Seed Database with Dummy Data

Run with: python manage.py seed_db
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random
import uuid

from core.models import BusinessProcess, ProcessStep, OperationalData, Recommendation


class Command(BaseCommand):
    help = 'Seeds the database with dummy data for testing and demonstration'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        # Clear existing data
        self.stdout.write('Clearing existing data...')
        OperationalData.objects.all().delete()
        Recommendation.objects.all().delete()
        ProcessStep.objects.all().delete()
        BusinessProcess.objects.all().delete()

        # Create Business Processes
        processes_data = [
            {
                'name': 'Order Processing',
                'description': 'Complete order fulfillment workflow from order receipt to delivery',
                'target_cycle_time': 120,
                'steps': [
                    ('Order Verification', 'manual', 10),
                    ('Payment Processing', 'automated', 5),
                    ('Inventory Check', 'automated', 3),
                    ('Picking & Packing', 'manual', 30),
                    ('Quality Check', 'manual', 15),
                    ('Shipping Label Generation', 'automated', 2),
                    ('Dispatch', 'manual', 20),
                ]
            },
            {
                'name': 'Customer Onboarding',
                'description': 'New customer registration and account setup process',
                'target_cycle_time': 60,
                'steps': [
                    ('Account Registration', 'manual', 5),
                    ('Email Verification', 'automated', 2),
                    ('Profile Setup', 'manual', 10),
                    ('Document Upload', 'manual', 15),
                    ('KYC Verification', 'manual', 25),
                    ('Account Activation', 'automated', 1),
                ]
            },
            {
                'name': 'Invoice Approval',
                'description': 'Invoice processing and approval workflow',
                'target_cycle_time': 45,
                'steps': [
                    ('Invoice Receipt', 'manual', 3),
                    ('Data Entry', 'manual', 8),
                    ('Validation Check', 'automated', 2),
                    ('Manager Approval', 'approval', 20),
                    ('Payment Processing', 'automated', 5),
                    ('Record Update', 'automated', 2),
                ]
            },
            {
                'name': 'Software Development Lifecycle',
                'description': 'Complete software development and deployment process',
                'target_cycle_time': 480,
                'steps': [
                    ('Requirement Analysis', 'manual', 60),
                    ('Design', 'manual', 90),
                    ('Development', 'manual', 180),
                    ('Code Review', 'manual', 45),
                    ('Testing', 'manual', 60),
                    ('Deployment', 'automated', 15),
                    ('Documentation', 'manual', 30),
                ]
            },
            {
                'name': 'Employee Leave Request',
                'description': 'Employee leave application and approval process',
                'target_cycle_time': 30,
                'steps': [
                    ('Leave Application', 'manual', 5),
                    ('Manager Review', 'approval', 15),
                    ('HR Verification', 'manual', 5),
                    ('Leave Balance Update', 'automated', 1),
                    ('Notification', 'automated', 1),
                ]
            }
        ]

        created_processes = []
        for proc_data in processes_data:
            steps_info = proc_data.pop('steps')
            process = BusinessProcess.objects.create(**proc_data)
            created_processes.append((process, steps_info))
            self.stdout.write(f'Created process: {process.name}')

        # Create Process Steps
        all_steps = []
        for process, steps_info in created_processes:
            for order, (name, step_type, estimated) in enumerate(steps_info, 1):
                step = ProcessStep.objects.create(
                    process=process,
                    name=name,
                    step_order=order,
                    step_type=step_type,
                    estimated_duration=estimated,
                    description=f'{name} step in {process.name} workflow'
                )
                all_steps.append(step)
            self.stdout.write(f'Created {len(steps_info)} steps for {process.name}')

        # Generate Operational Data
        self.stdout.write('Generating operational data...')
        statuses = ['completed', 'completed', 'completed', 'completed', 'failed', 'pending']
        priorities = ['low', 'medium', 'medium', 'high', 'critical']

        for process in created_processes:
            for _ in range(200):  # 200 executions per process
                run_id = f'RUN-{uuid.uuid4().hex[:8].upper()}'

                # Get a random step
                step = random.choice(all_steps)

                # Generate timing
                base_time = step.estimated_duration or 10

                # Add some variance (sometimes create bottlenecks)
                if random.random() < 0.15:  # 15% chance of bottleneck
                    execution_time = base_time * random.uniform(2.5, 5.0)
                else:
                    execution_time = base_time * random.uniform(0.7, 1.5)

                status = random.choices(
                    statuses,
                    weights=[70, 10, 5, 5, 5, 5],
                    k=1
                )[0]

                start_time = timezone.now() - timedelta(days=random.randint(1, 90))
                end_time = start_time + timedelta(minutes=execution_time)

                if status == 'completed':
                    log = OperationalData.objects.create(
                        process=process[0],
                        step=step,
                        run_id=run_id,
                        status=status,
                        priority=random.choice(priorities),
                        start_time=start_time,
                        end_time=end_time,
                        assigned_to=random.choice(['System', 'John Doe', 'Jane Smith', 'Mike Johnson', 'Sarah Wilson']),
                        notes=random.choice([
                            'Processed without issues',
                            'Standard execution',
                            'Required manual intervention',
                            'Completed within SLA',
                            '',
                            '',
                        ])
                    )
                else:
                    log = OperationalData.objects.create(
                        process=process[0],
                        step=step,
                        run_id=run_id,
                        status=status,
                        priority=random.choice(priorities),
                        start_time=start_time,
                        assigned_to=random.choice(['System', 'John Doe', 'Jane Smith'])
                    )

        self.stdout.write(self.style.SUCCESS(f'Created {OperationalData.objects.count()} operational logs'))

        # Generate some recommendations
        self.stdout.write('Generating recommendations...')

        recommendations_data = [
            {
                'title': 'Optimize Order Verification Step',
                'category': 'automation',
                'description': 'The Order Verification step shows high variability in execution times. Automating this step could significantly reduce the average cycle time.',
                'recommendation': 'Implement automated order verification rules to reduce manual review time by 60%.',
                'priority': 'high',
                'current_value': 25.0,
                'target_value': 10.0,
                'potential_savings': 15.0,
                'impact_score': 75
            },
            {
                'title': 'Manager Approval Bottleneck',
                'category': 'bottleneck',
                'description': 'Manager Approval step exceeds average time by 150% during peak hours. This is the primary bottleneck in the Invoice Approval process.',
                'recommendation': '1. Implement delegated approval authority\n2. Set up automated approval for amounts under $500\n3. Create approval queues with load balancing',
                'priority': 'critical',
                'current_value': 50.0,
                'target_value': 20.0,
                'potential_savings': 30.0,
                'impact_score': 90
            },
            {
                'title': 'Code Review Process Enhancement',
                'category': 'process',
                'description': 'Code Review times vary significantly between team members. Standardization could improve consistency.',
                'recommendation': '1. Create code review checklist\n2. Implement pair rotation\n3. Use automated code analysis tools',
                'priority': 'medium',
                'current_value': 55.0,
                'target_value': 35.0,
                'potential_savings': 20.0,
                'impact_score': 60
            },
            {
                'title': 'KYC Verification Automation',
                'category': 'automation',
                'description': 'KYC Verification is entirely manual. Integrating with external verification services could reduce time by 70%.',
                'recommendation': 'Integrate with automated KYC verification services and implement document OCR processing.',
                'priority': 'high',
                'current_value': 30.0,
                'target_value': 9.0,
                'potential_savings': 21.0,
                'impact_score': 85
            },
            {
                'title': 'Picking & Packing Efficiency',
                'category': 'performance',
                'description': 'Picking & Packing shows 40% deviation from estimated time during high-volume periods.',
                'recommendation': '1. Optimize warehouse layout\n2. Implement batch picking for similar items\n3. Add more pickers during peak hours',
                'priority': 'medium',
                'current_value': 42.0,
                'target_value': 30.0,
                'potential_savings': 12.0,
                'impact_score': 65
            }
        ]

        for i, rec_data in enumerate(recommendations_data):
            process = created_processes[i % len(created_processes)][0]
            step = all_steps[i % len(all_steps)]

            Recommendation.objects.create(
                process=process,
                step=step,
                **rec_data
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(recommendations_data)} recommendations'))

        # Summary
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(f'Business Processes: {BusinessProcess.objects.count()}')
        self.stdout.write(f'Process Steps: {ProcessStep.objects.count()}')
        self.stdout.write(f'Operational Logs: {OperationalData.objects.count()}')
        self.stdout.write(f'Recommendations: {Recommendation.objects.count()}')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('You can now run the server and visit the dashboard!'))
        self.stdout.write('Command: python manage.py runserver')
        self.stdout.write('URL: http://127.0.0.1:8000/')
