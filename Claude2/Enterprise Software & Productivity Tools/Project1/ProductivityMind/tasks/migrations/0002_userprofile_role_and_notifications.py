# Generated migration for UserProfile model updates

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='role',
            field=models.CharField(
                choices=[('admin', 'Administrator'), ('manager', 'Project Manager'), ('team_lead', 'Team Lead'), ('member', 'Team Member'), ('viewer', 'Viewer')],
                default='member',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='email_notifications',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='deadline_reminders',
            field=models.BooleanField(default=True),
        ),
    ]
