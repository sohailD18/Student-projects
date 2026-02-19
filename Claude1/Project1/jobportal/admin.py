"""
Admin Panel Configuration
Customizes Django admin to use custom templates
"""

from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required

# Customize admin site
admin.site.site_header = "JobPortal Administration"
admin.site.site_title = "JobPortal Admin"
admin.site.index_title = "Welcome to JobPortal Administration"

# Unregister default User model to customize it
# from django.contrib.auth.models import User
# admin.site.unregister(User)
