# ==============================================================================
# HealthPredict AI — WSGI Configuration for PythonAnywhere
# File Location on PythonAnywhere: /var/www/kd3114_pythonanywhere_com_wsgi.py
# ==============================================================================

import sys
import os

# Project root path (where app.py is located)
project_home = '/home/kd3114/Health-OPD/backend'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment
os.environ['FLASK_ENV'] = 'production'
os.environ['DEBUG'] = 'False'

# Import the Flask application instance
from app import app as application
