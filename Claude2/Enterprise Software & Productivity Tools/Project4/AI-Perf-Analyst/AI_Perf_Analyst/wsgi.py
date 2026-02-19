"""
WSGI config for AI_Perf_Analyst project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AI_Perf_Analyst.settings')

application = get_wsgi_application()
