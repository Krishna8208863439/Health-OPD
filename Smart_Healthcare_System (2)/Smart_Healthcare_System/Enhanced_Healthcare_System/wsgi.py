import sys
import os
import getpass

user = getpass.getuser()
project = f'/home/{user}/Health-OPD/Smart_Healthcare_System (2)/Smart_Healthcare_System/Enhanced_Healthcare_System'

if project not in sys.path:
    sys.path.insert(0, project)

os.chdir(project)

from app import app as application
