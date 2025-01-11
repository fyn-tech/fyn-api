"""
WSGI config for fyn-api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import sys

# Add the project directory to the Python path
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

def load_eb_environment_variables():
    """Load Elastic Beanstalk environment variables from file"""
    eb_env_file = '/opt/elasticbeanstalk/deployment/env'
    try:
        if os.path.exists(eb_env_file):
            with open(eb_env_file) as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        os.environ.setdefault(key, value)
    except Exception as e:
        print(f"Error loading environment variables: {e}", file=sys.stderr)

# Load environment variables before any Django imports
load_eb_environment_variables()

# Now import Django WSGI application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fyn-api.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()