#!/bin/bash
# ==============================================================================
# HealthPredict AI — 100% Automated PythonAnywhere Deployment Script
# Target Account: kd3114 (https://kd3114.pythonanywhere.com)
# ==============================================================================

set -e

USER=$(whoami)
echo "=========================================================="
echo "🏥 HealthPredict AI & HealthCare+: Automated Deployer"
echo "👤 PythonAnywhere User: $USER"
echo "🌐 Live Web App URL: https://$USER.pythonanywhere.com"
echo "=========================================================="

REPO_DIR="$HOME/Health-OPD"
PROJECT_DIR="$REPO_DIR/backend"
VENV_DIR="$HOME/.virtualenvs/healthpredict-env"

# 1. Clean up old caches and avoid Disk Quota Exceeded error
echo "🧹 1/5 Cleaning up temporary caches to free disk space..."
rm -rf ~/.cache/pip ~/.cache/* /tmp/pip* ~/.local/share/Trash/* || true
rm -rf "$HOME/.virtualenvs/healthcare-env" "$HOME/.virtualenvs/healthpredict-env" "$HOME/healthpredict-env" || true

# 2. Clone or pull repository
echo "📥 2/5 Pulling latest unified project code from GitHub..."
if [ -d "$REPO_DIR" ]; then
    cd "$REPO_DIR"
    git fetch origin
    git reset --hard origin/main
else
    git clone https://github.com/Krishna8208863439/Health-OPD.git "$REPO_DIR"
    cd "$REPO_DIR"
fi

# 3. Create virtualenv with system site packages (avoids downloading huge scikit-learn/pandas wheels)
echo "🐍 3/5 Creating virtual environment at $VENV_DIR..."
mkdir -p "$HOME/.virtualenvs"

# Detect Python 3.10 / 3.9 / default python3
if command -v python3.10 &>/dev/null; then
    PYTHON_EXEC=$(which python3.10)
elif command -v python3.9 &>/dev/null; then
    PYTHON_EXEC=$(which python3.9)
else
    PYTHON_EXEC=$(which python3)
fi

echo "Using Python binary: $PYTHON_EXEC"
virtualenv --python="$PYTHON_EXEC" --system-site-packages "$VENV_DIR"

# Also create convenient symlink at $HOME/healthpredict-env
ln -sfn "$VENV_DIR" "$HOME/healthpredict-env" || true

# 4. Install requirements
echo "📦 4/5 Installing dependencies..."
source "$VENV_DIR/bin/activate"
pip install --no-cache-dir -r "$PROJECT_DIR/requirements.txt"
rm -rf ~/.cache/pip ~/.cache/* || true

# 5. Automatically write WSGI configuration file
echo "⚙️ 5/5 Configuring WSGI configuration file..."
WSGI_FILE="/var/www/${USER}_pythonanywhere_com_wsgi.py"
if [ -f "$WSGI_FILE" ] || [ -d "/var/www" ]; then
    cat << 'EOF' > "$WSGI_FILE"
import sys
import os

backend_dir = os.path.expanduser('~/Health-OPD/backend')
root_dir = os.path.expanduser('~/Health-OPD')

for p in [backend_dir, root_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

os.environ['FLASK_ENV'] = 'production'
os.environ['DEBUG'] = 'False'

try:
    from app import app as application
except Exception as e:
    import traceback
    print("ERROR LOADING FLASK WSGI APPLICATION:", file=sys.stderr)
    traceback.print_exc()
    raise e
EOF
    echo "✅ Updated $WSGI_FILE automatically!"
fi

# 6. Initialize database tables (Users, Predictions, Metrics, Vitals, Meds, OPD)
echo "🔬 Initializing database tables..."
cd "$PROJECT_DIR"
python -c "from app import db, app; app.app_context().push(); db.create_all(); print('✅ Database tables initialized successfully!')"

echo ""
echo "=========================================================="
echo "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "=========================================================="
echo "👉 Now in your PythonAnywhere 'Web' tab, set these 3 fields:"
echo ""
echo "1. Source code:"
echo "   /home/$USER/Health-OPD/backend"
echo ""
echo "2. Working directory:"
echo "   /home/$USER/Health-OPD/backend"
echo ""
echo "3. Virtualenv (Copy & Paste this exact path into the box):"
echo "   /home/$USER/.virtualenvs/healthpredict-env"
echo "   (or simply: healthpredict-env)"
echo ""
echo "4. Click the big green button: [ 🔄 Reload $USER.pythonanywhere.com ]"
echo "=========================================================="
