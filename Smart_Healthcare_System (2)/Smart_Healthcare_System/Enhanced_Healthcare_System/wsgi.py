import sys
import os

# PythonAnywhere path for account KD3114
# Username is case-sensitive: KD3114 (uppercase)
project_home = '/home/KD3114/Health-OPD/Smart_Healthcare_System (2)/Smart_Healthcare_System/Enhanced_Healthcare_System'

if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Must chdir so SQLite DB and relative imports resolve correctly
os.chdir(project_home)

from app import app as application  # noqa
