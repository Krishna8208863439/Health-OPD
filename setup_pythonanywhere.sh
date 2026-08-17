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

# 1. Aggressively clean up caches and old envs to prevent Disk Quota Exceeded errors
echo "🧹 Cleaning up pip caches and old virtual environments to free disk space..."
rm -rf ~/.cache/pip ~/.cache/* /tmp/pip* ~/.local/share/Trash/* || true
rm -rf "$HOME/.virtualenvs/healthcare-env" "$HOME/.virtualenvs/healthpredict-env" || true

# 2. Clone or pull latest code
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

# 3. Setup Virtual Environment using --system-site-packages (reuses PythonAnywhere's pre-installed numpy, scipy, scikit-learn, pandas)
echo "🐍 Creating virtual environment with --system-site-packages at $VENV_DIR..."
mkdir -p "$HOME/.virtualenvs"
virtualenv --python=/usr/bin/python3.10 --system-site-packages "$VENV_DIR"

# 4. Install only the missing lightweight packages (takes < 2 MB disk space)
echo "📦 Installing required Python packages without downloading heavy wheels..."
source "$VENV_DIR/bin/activate"
pip install --no-cache-dir -r "$PROJECT_DIR/requirements.txt"

# 5. Clean cache again
rm -rf ~/.cache/pip ~/.cache/* || true

# 6. Initialize Database and Verify ML Models
echo "🔬 Initializing database & checking ML models..."
cd "$PROJECT_DIR"
python -c "from app import db, create_app; app = create_app(); app.app_context().push(); db.create_all(); print('✅ Database ready!')"

echo "=========================================================="
echo "✅ Backend & ML Pipeline installed successfully!"
echo "👉 Web Tab configuration for PythonAnywhere:"
echo "   - Source code: /home/$USER/Health-OPD/backend"
echo "   - Working directory: /home/$USER/Health-OPD/backend"
echo "   - Virtualenv: /home/$USER/.virtualenvs/healthpredict-env"
echo "   - WSGI file: /var/www/${USER}_pythonanywhere_com_wsgi.py"
echo "   - Then click 'Reload $USER.pythonanywhere.com'"
echo "=========================================================="
