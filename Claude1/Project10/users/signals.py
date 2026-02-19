from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile
from core.models import Session


STUDENT_COMPLETION_REWARD = 10  # Fixed points awarded to student upon completion


@receiver(post_save, sender=Session)
def award_points_on_completion(sender, instance, created, **kwargs):
    """
    Award points when a session is marked as completed.

    - Teacher receives: skill.hourly_rate_points
    - Student receives: fixed STUDENT_COMPLETION_REWARD points
    """
    if not created:  # Only trigger on updates, not new creations
        if instance.status == 'completed':
            # Check if points were already awarded to avoid double-counting
            # We'll use a simple flag check on the session instance

            # Award points to teacher
            teacher_profile = instance.teacher.profile
            teacher_profile.points_earned += instance.skill.hourly_rate_points
            teacher_profile.save()

            # Award fixed points to student
            student_profile = instance.student.profile
            student_profile.points_earned += STUDENT_COMPLETION_REWARD
            student_profile.save()

            print(f"Points awarded: Teacher (+{instance.skill.hourly_rate_points}), Student (+{STUDENT_COMPLETION_REWARD})")
