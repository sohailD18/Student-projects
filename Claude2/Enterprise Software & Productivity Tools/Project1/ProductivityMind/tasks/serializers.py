"""
ProductivityMind - API Serializers

Serializers for converting Django models to JSON format.
Built without Django REST Framework - using manual serialization.
"""
from django.utils import timezone
from datetime import timedelta
from .models import (
    Task, Project, ProjectMember, Tag, Category,
    WorkLog, UserProfile, TaskDependency
)


class BaseSerializer:
    """Base serializer class with common methods"""

    @staticmethod
    def serialize_datetime(dt):
        """Serialize datetime to ISO format string"""
        if dt:
            return dt.isoformat()
        return None

    @staticmethod
    def serialize_decimal(value):
        """Serialize decimal to float"""
        if value is not None:
            return float(value)
        return None

    @staticmethod
    def _serialize_performers(performers):
        """Serialize list of top performers (shared method)"""
        result = []
        for performer in performers:
            # Handle None values for hours_logged
            hours = getattr(performer, 'hours_logged', None)
            if hours is None:
                hours = 0
            else:
                hours = float(hours)

            result.append({
                'id': performer.id,
                'username': performer.username,
                'first_name': performer.first_name or '',
                'last_name': performer.last_name or '',
                'tasks_completed': getattr(performer, 'tasks_completed', 0) or 0,
                'hours_logged': hours,
            })
        return result


class TaskSerializer(BaseSerializer):
    """Serializer for Task model"""

    @classmethod
    def serialize(cls, task):
        """Serialize a single task"""
        return {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.get_status_display(),
            'status_code': task.status,
            'priority': task.get_priority_display(),
            'priority_code': task.priority,
            'project': cls._serialize_project(task.project),
            'assignee': cls._serialize_assignee(task.assignee),
            'created_at': cls.serialize_datetime(task.created_at),
            'updated_at': cls.serialize_datetime(task.updated_at),
            'due_date': cls.serialize_datetime(task.due_date),
            'completed_at': cls.serialize_datetime(task.completed_at),
            'estimated_hours': cls.serialize_decimal(task.estimated_hours),
            'actual_hours': cls.serialize_decimal(task.actual_hours),
            'tags': cls._serialize_tags(task.tags.all()),
            'category': cls._serialize_category(task.category),
            'smart_priority_score': task.smart_priority_score,
            'is_at_risk': task.is_at_risk,
            'risk_level': task.get_risk_level_display(),
            'risk_level_code': task.risk_level,
            'is_overdue': task.is_overdue,
            'days_until_due': task.days_until_due,
            'blocking_count': task.blocking_count,
            'blocked_by_count': task.blocked_by_count,
            'can_start': task.can_start,
            'completion_percentage': task.completion_percentage,
            'blocked_by': cls._serialize_dependencies(task.blocked_by.all()),
            'blocking': cls._serialize_dependencies(task.blocking.all()),
        }

    @classmethod
    def serialize_list(cls, tasks):
        """Serialize a list of tasks"""
        return [cls.serialize(task) for task in tasks]

    @staticmethod
    def _serialize_project(project):
        if not project:
            return None
        return {
            'id': project.id,
            'name': project.name,
            'progress': project.progress_percentage,
        }

    @staticmethod
    def _serialize_assignee(user):
        if not user:
            return None
        return {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }

    @staticmethod
    def _serialize_tags(tags):
        return [{'id': tag.id, 'name': tag.name, 'color': tag.color} for tag in tags]

    @staticmethod
    def _serialize_category(category):
        if not category:
            return None
        return {
            'id': category.id,
            'name': category.name,
            'icon': category.icon,
        }

    @staticmethod
    def _serialize_dependencies(tasks):
        return [{'id': t.id, 'title': t.title, 'status': t.get_status_display()} for t in tasks]

    @classmethod
    def deserialize(cls, data):
        """
        Deserialize JSON data to task fields.
        Returns a dict of fields that can be used to create/update a task.
        """
        fields = {}

        if 'title' in data:
            fields['title'] = data['title']
        if 'description' in data:
            fields['description'] = data.get('description', '')
        if 'status' in data:
            fields['status'] = data['status']
        if 'priority' in data:
            fields['priority'] = data['priority']
        if 'estimated_hours' in data:
            fields['estimated_hours'] = data['estimated_hours']
        if 'due_date' in data and data['due_date']:
            from django.utils.dateparse import parse_datetime
            fields['due_date'] = parse_datetime(data['due_date'])

        return fields


class ProjectSerializer(BaseSerializer):
    """Serializer for Project model"""

    @classmethod
    def serialize(cls, project):
        """Serialize a single project"""
        return {
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'created_at': cls.serialize_datetime(project.created_at),
            'updated_at': cls.serialize_datetime(project.updated_at),
            'total_tasks': project.total_tasks,
            'completed_tasks': project.completed_tasks,
            'progress_percentage': project.progress_percentage,
            'members': cls._serialize_members(project.projectmember_set.all()),
        }

    @classmethod
    def serialize_list(cls, projects):
        """Serialize a list of projects"""
        return [cls.serialize(project) for project in projects]

    @staticmethod
    def _serialize_members(members):
        return [{
            'id': m.user.id,
            'username': m.user.username,
            'role': m.get_role_display(),
            'joined_at': BaseSerializer.serialize_datetime(m.joined_at),
        } for m in members]


class CategorySerializer(BaseSerializer):
    """Serializer for Category model"""

    @classmethod
    def serialize(cls, category):
        return {
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'icon': category.icon,
            'created_at': cls.serialize_datetime(category.created_at),
        }

    @classmethod
    def serialize_list(cls, categories):
        return [cls.serialize(cat) for cat in categories]


class TagSerializer(BaseSerializer):
    """Serializer for Tag model"""

    @classmethod
    def serialize(cls, tag):
        return {
            'id': tag.id,
            'name': tag.name,
            'color': tag.color,
            'created_at': cls.serialize_datetime(tag.created_at),
        }

    @classmethod
    def serialize_list(cls, tags):
        return [cls.serialize(tag) for tag in tags]


class WorkLogSerializer(BaseSerializer):
    """Serializer for WorkLog model"""

    @classmethod
    def serialize(cls, work_log):
        return {
            'id': work_log.id,
            'task': {
                'id': work_log.task.id,
                'title': work_log.task.title,
            },
            'user': {
                'id': work_log.user.id,
                'username': work_log.user.username,
            },
            'hours': float(work_log.hours),
            'notes': work_log.notes,
            'logged_at': cls.serialize_datetime(work_log.logged_at),
        }

    @classmethod
    def serialize_list(cls, work_logs):
        return [cls.serialize(wl) for wl in work_logs]


class DashboardSerializer(BaseSerializer):
    """Serializer for Dashboard analytics"""

    @classmethod
    def serialize_dashboard(cls, data):
        """Serialize complete dashboard data"""
        return {
            'summary': cls._serialize_summary(data.get('summary', {})),
            'tasks': cls._serialize_task_lists(data.get('tasks', {})),
            'charts': cls._serialize_charts(data.get('charts', {})),
            'risks': cls._serialize_risks(data.get('risks', {})),
            'top_performers': cls._serialize_performers(data.get('top_performers', [])),
        }

    @staticmethod
    def _serialize_summary(summary):
        return {
            'total_tasks': summary.get('total_tasks', 0),
            'completed_tasks': summary.get('completed_tasks', 0),
            'in_progress_tasks': summary.get('in_progress_tasks', 0),
            'todo_tasks': summary.get('todo_tasks', 0),
            'at_risk_tasks': summary.get('at_risk_tasks', 0),
            'overdue_tasks': summary.get('overdue_tasks', 0),
            'total_users': summary.get('total_users', 0),
            'total_projects': summary.get('total_projects', 0),
        }

    @staticmethod
    def _serialize_task_lists(tasks):
        return {
            'prioritized': TaskSerializer.serialize_list(tasks.get('prioritized', [])[:10]),
            'at_risk': TaskSerializer.serialize_list(tasks.get('at_risk', [])[:10]),
            'overdue': TaskSerializer.serialize_list(tasks.get('overdue', [])[:10]),
            'upcoming': TaskSerializer.serialize_list(tasks.get('upcoming', [])[:10]),
        }

    @staticmethod
    def _serialize_charts(charts):
        return {
            'status_distribution': charts.get('status_distribution', {}),
            'completion_trend': charts.get('completion_trend', []),
            'task_volume': charts.get('task_volume', {}),
        }

    @staticmethod
    def _serialize_risks(risks):
        return {
            'bottlenecks': TaskSerializer.serialize_list(risks.get('bottlenecks', [])),
            'upcoming_deadlines': TaskSerializer.serialize_list(risks.get('upcoming_deadlines', [])),
        }


class ReportSerializer(BaseSerializer):
    """Serializer for productivity reports"""

    @classmethod
    def serialize_productivity_report(cls, data):
        """Serialize productivity report"""
        return {
            'period': data.get('period', {}),
            'summary': cls._serialize_report_summary(data.get('summary', {})),
            'top_performers': cls._serialize_performers(data.get('top_performers', [])),
            'bottlenecks': TaskSerializer.serialize_list(data.get('bottlenecks', [])),
            'recommendations': data.get('recommendations', []),
            'metrics': cls._serialize_metrics(data.get('metrics', {})),
        }

    @staticmethod
    def _serialize_report_summary(summary):
        return {
            'total_tasks_completed': summary.get('total_tasks_completed', 0),
            'total_hours_logged': float(summary.get('total_hours_logged', 0)),
            'average_completion_time': float(summary.get('average_completion_time', 0)),
            'on_time_completion_rate': float(summary.get('on_time_completion_rate', 0)),
        }

    @staticmethod
    def _serialize_metrics(metrics):
        return {
            'tasks_by_status': metrics.get('tasks_by_status', {}),
            'tasks_by_priority': metrics.get('tasks_by_priority', {}),
            'completion_by_day': metrics.get('completion_by_day', []),
            'tasks_by_category': metrics.get('tasks_by_category', {}),
        }


class UserProfileSerializer(BaseSerializer):
    """Serializer for UserProfile model"""

    @classmethod
    def serialize(cls, user_profile):
        """Serialize a single user profile"""
        user = user_profile.user
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'bio': user_profile.bio,
            'department': user_profile.department,
            'position': user_profile.position,
            'phone': user_profile.phone,
            'working_hours_per_day': float(user_profile.working_hours_per_day),
            'total_tasks_completed': user_profile.total_tasks_completed,
            'total_hours_logged': float(user_profile.total_hours_logged),
        }

    @classmethod
    def serialize_list(cls, user_profiles):
        """Serialize a list of user profiles"""
        return [cls.serialize(up) for up in user_profiles]
