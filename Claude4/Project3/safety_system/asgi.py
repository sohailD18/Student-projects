"""
ASGI config for AI-Enabled Worker Safety System.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safety_system.settings')

application = get_asgi_application()
