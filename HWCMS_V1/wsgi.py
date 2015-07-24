"""
WSGI config for HWCMS_V1 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os,sys
reload(sys)

sys.setdefaultencoding('utf8')

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HWCMS_V1.settings")

application = get_wsgi_application()

