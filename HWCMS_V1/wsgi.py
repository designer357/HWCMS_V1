"""
WSGI config for HWCMS_V1 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os,sys
reload(sys)

sys.setdefaultencoding('utf8')

proj = os.path.dirname(__file__)
projs = os.path.dirname(proj)
if projs not in sys.path:
    sys.path.append(proj)
    sys.path.append(projs)
sys.path.append('/Library/WebServer/Documents/HWCMS_V1')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HWCMS_V1.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()