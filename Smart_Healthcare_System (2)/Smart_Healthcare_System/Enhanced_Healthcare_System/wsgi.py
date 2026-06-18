import sys
import os

# Exact path on PythonAnywhere for kd3114
# Repo cloned as: /home/kd3114/Health-OPD
# App lives at:   /home/kd3114/Health-OPD/Smart_Healthcare_System (2)/Smart_Healthcare_System/Enhanced_Healthcare_System

project_home = '/home/kd3114/Health-OPD/Smart_Healthcare_System (2)/Smart_Healthcare_System/Enhanced_Healthcare_System'

if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Must chdir so SQLite DB and relative imports resolve correctly
os.chdir(project_home)

from app import app as application  # noqa
