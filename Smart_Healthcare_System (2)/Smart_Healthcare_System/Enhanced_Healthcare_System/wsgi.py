import sys
import os

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/Health-OPD/Smart_Healthcare_System (2)/Smart_Healthcare_System (2)/Smart_Healthcare_System/Enhanced_Healthcare_System'

if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set working directory so relative paths (Health.csv, healthcare.db) work
os.chdir(project_home)

from app import app as application
