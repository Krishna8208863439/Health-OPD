#!/bin/bash
# =========================================================
#  Smart Healthcare System – PythonAnywhere Setup Script
#  Account: kd3114
# =========================================================
set -e

USERNAME="kd3114"
REPO_URL="https://github.com/Krishna8208863439/Health-OPD.git"
REPO_DIR="$HOME/Health-OPD"
PROJECT_DIR="$REPO_DIR/Smart_Healthcare_System (2)/Smart_Healthcare_System/Professional_Healthcare_System"
VENV_DIR="$HOME/.virtualenvs/healthcare-env"

echo "=========================================================="
echo "  Health-OPD – PythonAnywhere Deployment"
echo "=========================================================="

# --- 1. Clone or pull latest code ---------------------------
if [ -d "$REPO_DIR/.git" ]; then
    echo "[1/4] Pulling latest code from GitHub..."
    cd "$REPO_DIR"
    git pull origin main
else
    echo "[1/4] Cloning repository from GitHub..."
    cd "$HOME"
    git clone "$REPO_URL"
fi

# --- 2. Set up virtual environment --------------------------
echo "[2/4] Setting up virtual environment..."
if [ -d "$VENV_DIR" ]; then
    echo "  Removing old venv to free space..."
    rm -rf "$VENV_DIR"
fi
pip cache purge 2>/dev/null || true
mkdir -p "$HOME/.virtualenvs"
virtualenv --python=/usr/bin/python3.10 --system-site-packages "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# --- 3. Install dependencies --------------------------------
echo "[3/4] Installing Python dependencies..."
pip install --no-cache-dir Flask==3.0.0 Flask-Login==0.6.3 reportlab==4.0.7 Werkzeug==3.0.1

# --- 4. Initialise database & generate logo -----------------
echo "[4/4] Initialising database and logo..."
cd "$PROJECT_DIR"
python create_logo.py 2>/dev/null || echo "  (logo generation skipped)"
python -c "from app import init_db; init_db(); print('  DB initialised.')"

echo ""
echo "=========================================================="
echo "  Setup COMPLETE!"
echo ""
echo "  Now do these steps in the PythonAnywhere Web tab:"
echo ""
echo "  1. Go to: https://www.pythonanywhere.com/user/$USERNAME/webapps/"
echo "  2. If no web app exists: 'Add a new web app'"
echo "     -> Manual configuration -> Python 3.10"
echo ""
echo "  3. Set Virtualenv path to:"
echo "     $VENV_DIR"
echo ""
echo "  4. Edit the WSGI file and paste:"
echo "     import sys, os"
echo "     project_home = '$PROJECT_DIR'"
echo "     if project_home not in sys.path:"
echo "         sys.path.insert(0, project_home)"
echo "     from app import app as application"
echo ""
echo "  5. Click Reload."
echo "  6. Visit: https://$USERNAME.pythonanywhere.com"
echo "=========================================================="
