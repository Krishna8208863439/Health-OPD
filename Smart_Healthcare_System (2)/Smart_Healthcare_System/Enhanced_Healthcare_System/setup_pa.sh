#!/bin/bash
# ============================================================
#  HealthCare Plus — Complete PythonAnywhere Setup for kd3114
#  Run from PythonAnywhere Bash console:
#    bash ~/Health-OPD/"Smart_Healthcare_System (2)"/Smart_Healthcare_System/Enhanced_Healthcare_System/setup_pa.sh
#  OR paste commands one by one below
# ============================================================

set -e
USERNAME="kd3114"
REPO_URL="https://github.com/Krishna8208863439/Health-OPD.git"
REPO_DIR="/home/$USERNAME/Health-OPD"
APP_DIR="$REPO_DIR/Smart_Healthcare_System (2)/Smart_Healthcare_System/Enhanced_Healthcare_System"
WSGI_FILE="/var/www/${USERNAME}_pythonanywhere_com_wsgi.py"

echo ""
echo "========================================================"
echo "  HealthCare Plus — PythonAnywhere Deploy for $USERNAME"
echo "========================================================"

# Step 1: Clone or update repo
echo ""
echo "[1/4] Setting up GitHub repo..."
if [ -d "$REPO_DIR/.git" ]; then
    echo "  Updating existing repo..."
    cd "$REPO_DIR"
    git fetch --all
    git reset --hard origin/main
    git pull origin main
else
    echo "  Cloning repo..."
    cd "/home/$USERNAME"
    git clone "$REPO_URL" Health-OPD
fi
echo "  Done."

# Step 2: Install all packages
echo ""
echo "[2/4] Installing Python packages (this may take 2-3 minutes)..."
pip3.12 install --user --quiet \
    flask==3.0.0 \
    flask-login==0.6.3 \
    werkzeug==3.0.1 \
    "pandas>=1.5" \
    scikit-learn \
    reportlab \
    "numpy<2.0" \
    gunicorn
echo "  Done."

# Step 3: Create required folders
echo ""
echo "[3/4] Creating directories..."
mkdir -p "$APP_DIR/static/reports"
mkdir -p "$APP_DIR/static/assets"
chmod 755 "$APP_DIR/static/reports"
echo "  Done."

# Step 4: Write WSGI file
echo ""
echo "[4/4] Writing WSGI config..."
cat > "$WSGI_FILE" << EOF
import sys
import os

project_home = '/home/$USERNAME/Health-OPD/Smart_Healthcare_System (2)/Smart_Healthcare_System/Enhanced_Healthcare_System'

if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.chdir(project_home)

from app import app as application
EOF

echo "  WSGI written to: $WSGI_FILE"
echo ""
echo "========================================================"
echo "  DONE! Now go to:"
echo "  https://www.pythonanywhere.com/user/$USERNAME/webapps/"
echo "  and click RELOAD to start the app."
echo ""
echo "  Live URL: https://$USERNAME.pythonanywhere.com"
echo "========================================================"
