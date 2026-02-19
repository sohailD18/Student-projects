"""
App configuration for Route Planner
"""
from django.apps import AppConfig


class RoutePlannerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'route_optimizer.route_planner'
    verbose_name = 'Route Planner'
