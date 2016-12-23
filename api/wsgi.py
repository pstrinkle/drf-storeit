"""
WSGI config for image_app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# XXX: make this .prod for using as production
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "drive_app.settings")

application = get_wsgi_application()
