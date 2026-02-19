"""
App Configuration for Traffic App

This module contains the configuration class for the traffic_app.
"""

from django.apps import AppConfig


class TrafficAppConfig(AppConfig):
    """
    Configuration class for traffic_app.

    Attributes:
        default_auto_field: The default type for auto-generated primary keys
        name: The name of the app
        verbose_name: Human-readable name for the app
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'traffic_app'
    verbose_name = 'Traffic Prediction System'
