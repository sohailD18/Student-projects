from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from users.models import Profile
from tasks.models import Task
from credits.models import Transaction
from reviews.models import Review
from gamification.models import Badge, UserBadge


class TimeBankAdminSite(admin.AdminSite):
    site_header = 'TimeBank Administration'
    site_title = 'TimeBank Admin Portal'
    index_title = 'Dashboard'

    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_dict = self._build_app_dict(request)
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

        # Add statistics
        stats = self.get_statistics()
        for app in app_list:
            for model in app['models']:
                model['stats'] = stats.get(model['object_name'], {})

        return app_list

    def get_statistics(self):
        """Gather statistics for the dashboard"""
        stats = {
            'User': User.objects.count(),
            'Profile': Profile.objects.count(),
            'Task': Task.objects.count(),
            'Open Tasks': Task.objects.filter(status='Open').count(),
            'Completed Tasks': Task.objects.filter(status='Completed').count(),
            'Transaction': Transaction.objects.count(),
            'Total Hours': Transaction.objects.aggregate(Sum('amount'))['amount__sum'] or 0,
            'Review': Review.objects.count(),
            'Badge': Badge.objects.count(),
            'UserBadge': UserBadge.objects.count(),
        }
        return stats


# Create custom admin site
timebank_admin = TimeBankAdminSite(name='timebank_admin')

# Register models
timebank_admin.register(User)
timebank_admin.register(Profile)
timebank_admin.register(Task)
timebank_admin.register(Transaction)
timebank_admin.register(Review)
timebank_admin.register(Badge)
timebank_admin.register(UserBadge)
