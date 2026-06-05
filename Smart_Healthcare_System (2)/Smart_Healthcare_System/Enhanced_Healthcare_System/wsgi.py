import sys
import os

project = '/home/Krishna8208863439/Health-OPD/Smart_Healthcare_System (2)/Smart_Healthcare_System/Enhanced_Healthcare_System'
if project not in sys.path:
    sys.path.insert(0, project)

os.chdir(project)

from app import app as application
