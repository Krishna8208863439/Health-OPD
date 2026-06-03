#!/bin/bash

# Exit on error
set -e

echo "=========================================================="
echo "🏥 Smart Healthcare System: PythonAnywhere Auto-Setup 🏥"
echo "=========================================================="

# 1. Clean up previous failed attempts and free up space
echo "Deactivating and deleting previous virtualenv 'healthcare-env' to free space..."
# Check if deactivate is available and run it
if declare -f deactivate >/dev/null; then
    deactivate || true
fi
rm -rf ~/.virtualenvs/healthcare-env || true

echo "Purging pip cache to reclaim disk space..."
pip cache purge || true

# 2. Create virtual environment with system site packages enabled using direct virtualenv command
# This bypasses virtualenvwrapper initialization issues and is 100% reliable.
echo "[1/3] Creating virtualenv at ~/.virtualenvs/healthcare-env..."
mkdir -p ~/.virtualenvs
virtualenv --python=/usr/bin/python3.10 --system-site-packages ~/.virtualenvs/healthcare-env

# 3. Activate the new virtual environment
echo "Activating virtualenv..."
source ~/.virtualenvs/healthcare-env/bin/activate

# 4. Install lightweight dependencies
echo "[2/3] Installing lightweight dependencies..."
pip install --no-cache-dir Flask-Login==0.6.3 reportlab==4.0.7

# 5. Generate the logo
echo "[3/3] Generating hospital logo..."
python create_logo.py

echo "=========================================================="
echo "✅ Auto-Setup Completed Successfully!"
echo "=========================================================="
echo ""
echo "Next Steps to launch your web application:"
echo "1. Go to the PythonAnywhere 'Web' tab."
echo "2. Click 'Add a new web app', choose 'Manual Configuration' and 'Python 3.10'."
echo "3. Set the 'Virtualenv' path to: /home/<your-username>/.virtualenvs/healthcare-env"
echo "4. Update the WSGI configuration file (link in Web tab) with this content:"
echo "----------------------------------------------------------"
echo "import sys"
echo "import os"
echo "project_home = '/home/<your-username>/Smart_Healthcare_System/Smart_Healthcare_System (2)/Smart_Healthcare_System/Professional_Healthcare_System'"
echo "if project_home not in sys.path:"
echo "    sys.path.insert(0, project_home)"
echo "from app import app as application"
echo "----------------------------------------------------------"
echo "5. Click 'Reload' on the Web tab, and your app will be live!"
echo "=========================================================="
