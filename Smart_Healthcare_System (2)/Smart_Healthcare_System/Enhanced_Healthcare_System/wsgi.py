import sys
import os

# ── Project path ──────────────────────────────────────────────────────────────
project = '/home/KD3114/Health-OPD/Smart_Healthcare_System (2)/Smart_Healthcare_System/Enhanced_Healthcare_System'
if project not in sys.path:
    sys.path.insert(0, project)

os.chdir(project)

# ── Add user site-packages (pip install --user goes here) ─────────────────────
user_packages = '/home/KD3114/.local/lib/python3.10/site-packages'
if user_packages not in sys.path:
    sys.path.insert(1, user_packages)

# ── Add system site-packages (PythonAnywhere has pandas/numpy/sklearn here) ───
system_packages = '/usr/lib/python3/dist-packages'
if system_packages not in sys.path:
    sys.path.append(system_packages)

from app import app as application
