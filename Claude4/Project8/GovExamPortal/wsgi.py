"""
WSGI config for GovExamPortal project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GovExamPortal.settings')

application = get_wsgi_application()
