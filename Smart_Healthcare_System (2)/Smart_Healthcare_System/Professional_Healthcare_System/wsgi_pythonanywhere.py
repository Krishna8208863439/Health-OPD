import sys
import os

# Path to your project directory on PythonAnywhere
project_home = '/home/kd3114/Health-OPD/Smart_Healthcare_System (2)/Smart_Healthcare_System/Professional_Healthcare_System'

if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set working directory so relative paths (DB, CSV, etc.) resolve correctly
os.chdir(project_home)

from app import app as application
