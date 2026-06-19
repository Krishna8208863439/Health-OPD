#!/bin/bash
# ============================================================
#  HealthCare Plus — PythonAnywhere Setup for KD3114
#  Run this in PythonAnywhere Bash console:
#    bash ~/Health-OPD/"Smart_Healthcare_System (2)"/Smart_Healthcare_System/Enhanced_Healthcare_System/setup_pa.sh
# ============================================================

set -e

# IMPORTANT: Username is KD3114 (uppercase) on PythonAnywhere
USERNAME="KD3114"
REPO_URL="https://github.com/Krishna8208863439/Health-OPD.git"
REPO_DIR="/home/$USERNAME/Health-OPD"
APP_DIR="$REPO_DIR/Smart_Healthcare_System (2)/Smart_Healthcare_System/Enhanced_Healthcare_System"

# PythonAnywhere WSGI file always uses lowercase in the filename
WSGI_FILE="/var/www/kd3114_pythonanywhere_com_wsgi.py"

echo ""
echo "========================================================"
echo "  HealthCare Plus — PythonAnywhere Deploy for $USERNAME"
echo "========================================================"

# Step 1: Clone or update repo
echo ""
echo "[1/5] Setting up GitHub repo..."
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
echo "[2/5] Installing Python packages (this may take 2-3 minutes)..."
pip3.12 install --user --quiet \
    flask==3.0.0 \
    flask-login==0.6.3 \
    werkzeug==3.0.1 \
    "pandas>=1.5" \
    scikit-learn \
    reportlab \
    "numpy<2.0" \
    gunicorn \
    requests
echo "  Done."

# Step 3: Create required folders
echo ""
echo "[3/5] Creating directories..."
mkdir -p "$APP_DIR/static/reports"
mkdir -p "$APP_DIR/static/assets"
chmod 755 "$APP_DIR/static/reports"
echo "  Done."

# Step 4: Write WSGI file with correct UPPERCASE username path
echo ""
echo "[4/5] Writing WSGI config (with correct KD3114 uppercase path)..."
cat > "$WSGI_FILE" << EOF
import sys
import os

# IMPORTANT: username is KD3114 (uppercase) on this PythonAnywhere account
project_home = '/home/KD3114/Health-OPD/Smart_Healthcare_System (2)/Smart_Healthcare_System/Enhanced_Healthcare_System'

if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.chdir(project_home)

from app import app as application
EOF

echo "  WSGI written to: $WSGI_FILE"

# Step 5: Reload web app
echo ""
echo "[5/5] Reloading web app..."
touch "$WSGI_FILE"
echo "  Done."

echo ""
echo "========================================================"
echo "  DONE! Your app is live at:"
echo "  https://kd3114.pythonanywhere.com"
echo ""
echo "  Food Scanner: https://kd3114.pythonanywhere.com/food-scanner"
echo ""
echo "  NOTE: To enable Gemini AI food recognition, go to:"
echo "  Web tab -> Environment variables -> Add GEMINI_API_KEY"
echo "========================================================"
