from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'
    verbose_name = 'ProductivityMind Tasks'

    def ready(self):
        """
        Import signals when the app is ready
        """
        import tasks.signals
