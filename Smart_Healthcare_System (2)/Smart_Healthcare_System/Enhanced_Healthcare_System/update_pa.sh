#!/bin/bash
# ============================================================
#  HealthCare Plus – PythonAnywhere UPDATE Script for kd3114
#  Run this in the PythonAnywhere Bash console to pull latest
#  code and reload the web app.
#
#  HOW TO USE:
#   1. Open PythonAnywhere Bash console for kd3114
#   2. Run:  bash ~/update_app.sh
# ============================================================

set -e

USERNAME="kd3114"
REPO_DIR="/home/$USERNAME/Health-OPD"
APP_DIR="$REPO_DIR/Smart_Healthcare_System (2)/Smart_Healthcare_System/Enhanced_Healthcare_System"

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
echo "[✓] Latest code pulled from GitHub (feat: food scanner improvements)"
echo ""
echo "  Changes in this update:"
echo "  - Food scanner now ONLY scans food items"
echo "  - Non-food images are rejected with a clear error"
echo "  - Good/Bad/Caution health verdict shown after scan"
echo "  - Gemini AI vision used for accurate food identification"
echo ""

# Ensure static dirs exist
mkdir -p "$APP_DIR/static/reports"
mkdir -p "$APP_DIR/static/assets"

echo "[✓] Directories verified"

# Touch wsgi to trigger reload
touch /var/www/${USERNAME}_pythonanywhere_com_wsgi.py

echo "[✓] Web app reloaded"
echo ""
echo "=============================================="
echo "  DONE! App is live at:"
echo "  https://$USERNAME.pythonanywhere.com"
echo ""
echo "  Food Scanner: https://$USERNAME.pythonanywhere.com/food-scanner"
echo "=============================================="
