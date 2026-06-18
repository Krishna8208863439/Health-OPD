#!/bin/bash
# =============================================================
#  HealthCare Plus — PythonAnywhere Setup Script for kd3114
#  Run this in the PythonAnywhere Bash console:
#    bash setup_pa.sh
# =============================================================

set -e
USERNAME="kd3114"
REPO="https://github.com/Krishna8208863439/Health-OPD.git"
HOME_DIR="/home/$USERNAME"
REPO_DIR="$HOME_DIR/Health-OPD"
APP_DIR="$REPO_DIR/Smart_Healthcare_System (2)/Smart_Healthcare_System/Enhanced_Healthcare_System"
DOMAIN="${USERNAME}.pythonanywhere.com"

echo ""
echo "======================================================"
echo "  HealthCare Plus — PythonAnywhere Deploy"
echo "  Account : $USERNAME"
echo "  Domain  : https://$DOMAIN"
echo "======================================================"
echo ""

# ── Step 1: Clone or update repo ──────────────────────────
echo "[1/5] Syncing GitHub repo..."
if [ -d "$REPO_DIR/.git" ]; then
    echo "  Repo exists — pulling latest..."
    cd "$REPO_DIR"
    git pull origin main
else
    echo "  Cloning fresh..."
    cd "$HOME_DIR"
    git clone "$REPO" Health-OPD
fi
echo "  ✅ Repo ready"

# ── Step 2: Install dependencies ──────────────────────────
echo ""
echo "[2/5] Installing Python packages..."
cd "$APP_DIR"
pip3.12 install --user \
    flask==3.0.0 \
    flask-login==0.6.3 \
    werkzeug==3.0.1 \
    pandas==2.1.4 \
    scikit-learn==1.3.2 \
    reportlab==4.0.8 \
    numpy==1.26.2 \
    gunicorn==21.2.0
echo "  ✅ Packages installed"

# ── Step 3: Create static/reports directory ───────────────
echo ""
echo "[3/5] Creating required directories..."
mkdir -p "$APP_DIR/static/reports"
mkdir -p "$APP_DIR/static/assets"
chmod 755 "$APP_DIR/static/reports"
echo "  ✅ Directories ready"

# ── Step 4: Write WSGI file ────────────────────────────────
echo ""
echo "[4/5] Writing WSGI config..."
WSGI_PATH="/var/www/${USERNAME}_pythonanywhere_com_wsgi.py"

cat > "$WSGI_PATH" << 'WSGI_EOF'
import sys
import os

project_home = '/home/kd3114/Health-OPD/Smart_Healthcare_System (2)/Smart_Healthcare_System/Enhanced_Healthcare_System'

if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.chdir(project_home)

from app import app as application
WSGI_EOF

echo "  ✅ WSGI file written to $WSGI_PATH"

# ── Step 5: Reload web app ─────────────────────────────────
echo ""
echo "[5/5] Reloading web app..."
touch "$WSGI_PATH"
echo "  ✅ Web app reloaded"

# ── Done ───────────────────────────────────────────────────
echo ""
echo "======================================================"
echo "  ✅ DEPLOYMENT COMPLETE!"
echo ""
echo "  🌐 Live at: https://$DOMAIN"
echo ""
echo "  If it shows errors, check logs at:"
echo "  https://www.pythonanywhere.com/user/$USERNAME/webapps/#tab_id_${USERNAME}_pythonanywhere_com"
echo "======================================================"
echo ""
