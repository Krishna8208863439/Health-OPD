import sys
import os

# PythonAnywhere path for kd3114
project_home = '/home/kd3114/Health-OPD/Smart_Healthcare_System (2)/Smart_Healthcare_System/Enhanced_Healthcare_System'

if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.chdir(project_home)

from app import app as application  # noqa
