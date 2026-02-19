from django.apps import AppConfig


class DealsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'deals'
    verbose_name = 'Deals Management'

    def ready(self):
        # Import template tags to register them
        import deals.templatetags.deals_filters
