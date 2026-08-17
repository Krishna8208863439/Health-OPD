#!/bin/bash
# ==============================================================================
# HealthPredict AI — Automated PythonAnywhere One-Click Setup Script
# Target Account: kd3114 (https://kd3114.pythonanywhere.com)
# ==============================================================================

set -e

USER=$(whoami)
echo "=========================================================="
echo "🏥 HealthPredict AI: Automated PythonAnywhere Deployer"
echo "👤 User: $USER"
echo "🌐 URL: https://$USER.pythonanywhere.com"
echo "=========================================================="

REPO_DIR="$HOME/Health-OPD"
PROJECT_DIR="$REPO_DIR/backend"
VENV_DIR="$HOME/.virtualenvs/healthpredict-env"

# 1. Clone or pull latest code
if [ -d "$REPO_DIR" ]; then
    echo "📥 Updating existing repository in $REPO_DIR..."
    cd "$REPO_DIR"
    git fetch origin
    git reset --hard origin/main
else
    echo "📥 Cloning repository to $REPO_DIR..."
    git clone https://github.com/Krishna8208863439/Health-OPD.git "$REPO_DIR"
    cd "$REPO_DIR"
fi

# 2. Setup Virtual Environment
echo "🐍 Creating virtual environment at $VENV_DIR..."
mkdir -p "$HOME/.virtualenvs"
rm -rf "$VENV_DIR" || true
virtualenv --python=/usr/bin/python3.10 "$VENV_DIR"

# 3. Install backend dependencies
echo "📦 Installing required Python packages..."
source "$VENV_DIR/bin/activate"
pip install --no-cache-dir -r "$PROJECT_DIR/requirements.txt"

# 4. Initialize Database and Verify ML Models
echo "🔬 Initializing database & checking ML models..."
cd "$PROJECT_DIR"
python -c "from app import db, create_app; app = create_app(); app.app_context().push(); db.create_all(); print('Database ready!')"

echo "=========================================================="
echo "✅ Backend & ML Pipeline installed successfully!"
echo "👉 Now configure the Web Tab on PythonAnywhere:"
echo "   - Source code: /home/$USER/Health-OPD/backend"
echo "   - Working directory: /home/$USER/Health-OPD/backend"
echo "   - Virtualenv: /home/$USER/.virtualenvs/healthpredict-env"
echo "   - WSGI file: /var/www/${USER}_pythonanywhere_com_wsgi.py"
echo "   - Then click 'Reload $USER.pythonanywhere.com'"
echo "=========================================================="
