"""
WSGI config for dynamic_pricing project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dynamic_pricing.settings')

application = get_wsgi_application()
