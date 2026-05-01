"""
WSGI config for AI Idea Validator project.
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

# Add the parent directory to Python path so 'config' can be found
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'idea_validator.config.settings')

application = get_wsgi_application()
