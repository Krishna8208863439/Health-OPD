#!/bin/bash
# ============================================================
#  HealthCare Plus — Quick Update Script for KD3114
#  Run in PythonAnywhere Bash console:
#    bash ~/Health-OPD/"Smart_Healthcare_System (2)"/Smart_Healthcare_System/Enhanced_Healthcare_System/update_pa.sh
# ============================================================

# IMPORTANT: Username is KD3114 (uppercase)
USERNAME="KD3114"
REPO_DIR="/home/$USERNAME/Health-OPD"
APP_DIR="$REPO_DIR/Smart_Healthcare_System (2)/Smart_Healthcare_System/Enhanced_Healthcare_System"
WSGI_FILE="/var/www/kd3114_pythonanywhere_com_wsgi.py"

echo ""
echo "=============================================="
echo "  HealthCare Plus - Pulling Latest Code"
echo "=============================================="

# Pull latest from GitHub
cd "$REPO_DIR"
git fetch --all
git reset --hard origin/main
git pull origin main

echo ""
echo "[✓] Latest code pulled from GitHub"
echo ""
echo "  Food Scanner Features:"
echo "  - ONLY scans food items (hands/objects rejected)"
echo "  - Good / Bad / Caution health verdict shown"
echo "  - Gemini AI vision for accurate food recognition"
echo ""

# Ensure dirs exist
mkdir -p "$APP_DIR/static/reports"
mkdir -p "$APP_DIR/static/assets"

# Fix WSGI file with correct UPPERCASE username
cat > "$WSGI_FILE" << EOF
import sys
import os

project_home = '/home/KD3114/Health-OPD/Smart_Healthcare_System (2)/Smart_Healthcare_System/Enhanced_Healthcare_System'

if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.chdir(project_home)

from app import app as application
EOF

# Touch to reload
touch "$WSGI_FILE"

echo "[✓] WSGI fixed and web app reloaded"
echo ""
echo "=============================================="
echo "  App is LIVE at:"
echo "  https://kd3114.pythonanywhere.com"
echo "  Food Scanner: /food-scanner"
echo "=============================================="
