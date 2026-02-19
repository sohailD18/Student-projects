"""
Simple test script to diagnose dashboard API issues
Run with: python test_dashboard.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'productivity_core.settings')
django.setup()

from tasks.models import Task, User, Project, UserProfile
from tasks.ai_engine import ProductivityAnalytics, TaskPrioritizationEngine, RiskPredictionEngine

print("=== Dashboard Diagnostics ===\n")

# Check database
print("1. Checking database...")
print(f"   - Users: {User.objects.count()}")
print(f"   - Tasks: {Task.objects.count()}")
print(f"   - Projects: {Project.objects.count()}")
print(f"   - UserProfiles: {UserProfile.objects.count()}")

# Check for users without profiles
users_without_profiles = User.objects.filter(profile__isnull=True)
if users_without_profiles.exists():
    print(f"\n⚠️ WARNING: {users_without_profiles.count()} user(s) without profiles:")
    for user in users_without_profiles:
        print(f"   - Creating profile for user: {user.username}")
        UserProfile.objects.create(user=user)
else:
    print("\n✓ All users have profiles")

# Test analytics engine
print("\n2. Testing analytics engine...")
try:
    analytics = ProductivityAnalytics()
    status_dist = analytics.get_status_distribution()
    print(f"   ✓ Status distribution: {status_dist}")
except Exception as e:
    print(f"   ✗ Error getting status distribution: {e}")

try:
    trend = analytics.get_task_completion_trend(days=30)
    print(f"   ✓ Completion trend: {len(trend)} data points")
except Exception as e:
    print(f"   ✗ Error getting completion trend: {e}")

try:
    performers = list(analytics.get_top_performers(limit=10, days=30))
    print(f"   ✓ Top performers: {len(performers)} found")
    for p in performers[:3]:
        print(f"      - {p.username}: {p.tasks_completed} tasks, {p.hours_logged}h")
except Exception as e:
    print(f"   ✗ Error getting top performers: {e}")

try:
    bottlenecks = list(analytics.get_bottleneck_tasks(limit=10))
    print(f"   ✓ Bottleneck tasks: {len(bottlenecks)} found")
except Exception as e:
    print(f"   ✗ Error getting bottlenecks: {e}")

# Test priority engine
print("\n3. Testing priority engine...")
try:
    priority_engine = TaskPrioritizationEngine()
    prioritized = list(priority_engine.get_prioritized_tasks(limit=5))
    print(f"   ✓ Prioritized tasks: {len(prioritized)} found")
except Exception as e:
    print(f"   ✗ Error getting prioritized tasks: {e}")

# Test risk engine
print("\n4. Testing risk engine...")
try:
    risk_engine = RiskPredictionEngine()
    at_risk = list(risk_engine.get_at_risk_tasks(min_risk='high'))
    print(f"   ✓ At-risk tasks: {len(at_risk)} found")
except Exception as e:
    print(f"   ✗ Error getting at-risk tasks: {e}")

# Test reports data
print("\n5. Testing reports data generation...")
try:
    from django.db.models import Sum, Avg, F
    from datetime import timedelta

    days = 30
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)

    completed_tasks = Task.objects.filter(
        status='done',
        completed_at__gte=start_date,
        completed_at__lte=end_date
    )

    total_completed = completed_tasks.count()
    total_hours = completed_tasks.aggregate(total=Sum('actual_hours'))['total'] or 0

    on_time_count = completed_tasks.filter(completed_at__lte=F('due_date')).count()
    on_time_rate = (on_time_count / total_completed * 100) if total_completed > 0 else 0

    avg_completion = completed_tasks.aggregate(avg=Avg('actual_hours'))['avg'] or 0

    print(f"   ✓ Reports summary generated:")
    print(f"      - Completed tasks: {total_completed}")
    print(f"      - Total hours: {total_hours}")
    print(f"      - On-time rate: {on_time_rate:.1f}%")
    print(f"      - Avg completion: {avg_completion}h")
except Exception as e:
    print(f"   ✗ Error generating reports: {e}")

print("\n=== Diagnostics Complete ===")
print("\nIf all tests passed, the dashboard should work correctly.")
print("If you see errors, check the Django logs for more details.")
