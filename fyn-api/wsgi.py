"""
WSGI config for fyn-api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

eb_env_file = '/opt/elasticbeanstalk/deployment/env'
if os.path.exists(eb_env_file):
    with open(eb_env_file) as f:
        for line in f:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
                
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fyn-api.settings')

application = get_wsgi_application()
