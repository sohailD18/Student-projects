from django.db import migrations


def create_initial_badges(apps, schema_editor):
    Badge = apps.get_model('gamification', 'Badge')
    badges = [
        {
            'name': 'Helpful Neighbor',
            'description': 'Completed 5 tasks',
            'badge_type': 'tasks_completed',
            'requirement_value': 5,
            'icon_name': 'fa-hands-helping',
        },
        {
            'name': 'Community Builder',
            'description': 'Completed 25 tasks',
            'badge_type': 'tasks_completed',
            'requirement_value': 25,
            'icon_name': 'fa-users',
        },
        {
            'name': 'Super Helper',
            'description': 'Completed 50 tasks',
            'badge_type': 'tasks_completed',
            'requirement_value': 50,
            'icon_name': 'fa-star',
        },
        {
            'name': 'Time Keeper',
            'description': 'Earned 10 hours',
            'badge_type': 'hours_earned',
            'requirement_value': 10,
            'icon_name': 'fa-clock',
        },
        {
            'name': 'Time Lord',
            'description': 'Earned 50 hours',
            'badge_type': 'hours_earned',
            'requirement_value': 50,
            'icon_name': 'fa-crown',
        },
        {
            'name': 'Century Club',
            'description': 'Earned 100 hours',
            'badge_type': 'hours_earned',
            'requirement_value': 100,
            'icon_name': 'fa-trophy',
        },
        {
            'name': 'First Review',
            'description': 'Gave your first review',
            'badge_type': 'reviews_given',
            'requirement_value': 1,
            'icon_name': 'fa-comment-dots',
        },
        {
            'name': 'Feedback Champion',
            'description': 'Gave 10 reviews',
            'badge_type': 'reviews_given',
            'requirement_value': 10,
            'icon_name': 'fa-thumbs-up',
        },
        {
            'name': 'Voice of the Community',
            'description': 'Gave 50 reviews',
            'badge_type': 'reviews_given',
            'requirement_value': 50,
            'icon_name': 'fa-bullhorn',
        },
    ]

    for badge_data in badges:
        Badge.objects.create(**badge_data)


class Migration(migrations.Migration):
    dependencies = [
        ('gamification', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_badges),
    ]
