"""
WSGI entry point for PythonAnywhere deployment.
In PythonAnywhere Web tab, set:
  Source code:   /home/kd3114/Smart_Healthcare_System
  Working dir:   /home/kd3114/Smart_Healthcare_System
  WSGI file:     /home/kd3114/Smart_Healthcare_System/wsgi.py
"""
import sys
import os

# Add the project directory to the path
project_home = '/home/kd3114/Smart_Healthcare_System'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Change to the project directory so SQLite DB path resolves correctly
os.chdir(project_home)

from app import app as application  # noqa
