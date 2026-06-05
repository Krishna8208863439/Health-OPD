"""
WSGI entry point for PythonAnywhere deployment.
PythonAnywhere looks for a variable named 'application'.
"""
import sys
import os

# ── Add the project directory to Python path ──────────────────────────────────
project_home = '/home/Krishna8208863439/Health-OPD/Smart_Healthcare_System (2)/Smart_Healthcare_System/Enhanced_Healthcare_System'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# ── Change working directory so relative paths (healthcare.db, Health.csv) work
os.chdir(project_home)

# ── Import the Flask app ──────────────────────────────────────────────────────
from app import app as application  # noqa: F401
