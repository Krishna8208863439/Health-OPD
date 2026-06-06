#!/bin/bash

# Exit on error
set -e

echo "=========================================================="
echo "🏥 Smart Healthcare System (Enhanced): PythonAnywhere Setup 🏥"
echo "=========================================================="

# 1. Clean up previous virtualenv to free space
echo "Deactivating and deleting previous virtualenv 'healthcare-env' to free space..."
if declare -f deactivate >/dev/null; then
    deactivate || true
fi
rm -rf ~/.virtualenvs/healthcare-env || true

echo "Purging pip cache to reclaim disk space..."
pip cache purge || true

# 2. Create virtual environment with system site packages enabled
# This enables pre-installed heavy dependencies like pandas, numpy, scikit-learn.
echo "[1/2] Creating virtualenv at ~/.virtualenvs/healthcare-env using python3.10..."
mkdir -p ~/.virtualenvs
virtualenv --python=/usr/bin/python3.10 --system-site-packages ~/.virtualenvs/healthcare-env

# 3. Activate the virtual environment
echo "Activating virtualenv..."
source ~/.virtualenvs/healthcare-env/bin/activate

# 4. Install lightweight dependencies not pre-installed or matching specific versions
echo "[2/2] Installing lightweight dependencies..."
pip install --no-cache-dir Flask-Login==0.6.3 reportlab==4.0.8

echo "=========================================================="
echo "✅ Auto-Setup Completed Successfully!"
echo "=========================================================="
echo ""
echo "Next Steps to launch your web application:"
echo "1. Go to the PythonAnywhere 'Web' tab."
echo "2. Click 'Add a new web app' (or configure your existing one):"
echo "   - Choose 'Manual Configuration' (do NOT choose Flask, choose Manual Configuration)."
echo "   - Choose 'Python 3.10'."
echo "3. In the Web tab configuration:"
echo "   - Set the 'Source code' directory to:"
echo "     /home/$USER/Health-OPD/Smart_Healthcare_System (2)/Smart_Healthcare_System/Enhanced_Healthcare_System"
echo "   - Set the 'Working directory' to:"
echo "     /home/$USER/Health-OPD/Smart_Healthcare_System (2)/Smart_Healthcare_System/Enhanced_Healthcare_System"
echo "   - Set the 'Virtualenv' path to:"
echo "     /home/$USER/.virtualenvs/healthcare-env"
echo "4. Update the PythonAnywhere WSGI configuration file (click the link under the WSGI configuration file section in the Web tab) to exactly match:"
echo "----------------------------------------------------------"
echo "import sys"
echo "import os"
echo "import getpass"
echo ""
echo "user = getpass.getuser()"
echo "project = f'/home/{user}/Health-OPD/Smart_Healthcare_System (2)/Smart_Healthcare_System/Enhanced_Healthcare_System'"
echo "if project not in sys.path:"
echo "    sys.path.insert(0, project)"
echo "os.chdir(project)"
echo "from app import app as application"
echo "----------------------------------------------------------"
echo "5. Click 'Reload' on the Web tab, and your app will be live!"
echo "=========================================================="
