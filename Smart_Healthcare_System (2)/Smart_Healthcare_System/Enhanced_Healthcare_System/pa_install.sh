#!/bin/bash
# ── PythonAnywhere installer ──────────────────────────────────────────────────
# Uses system pandas/numpy/scikit-learn (already on PythonAnywhere)
# Only installs small missing packages to save disk space
# Usage: bash pa_install.sh

echo "=== HealthCare Plus - PythonAnywhere Setup ==="

APP_DIR="/home/KD3114/Health-OPD/Smart_Healthcare_System (2)/Smart_Healthcare_System/Enhanced_Healthcare_System"

# Step 1: Check system packages
echo "[1/4] Checking system packages..."
python3.10 -c "import pandas, numpy, sklearn; print('System pandas/numpy/sklearn: OK')" 2>/dev/null || {
    echo "System packages missing - installing..."
    pip3.10 install --user pandas==2.1.4 numpy==1.26.2 scikit-learn==1.3.2
}

# Step 2: Install flask and small packages only
echo "[2/4] Installing Flask and small packages..."
pip3.10 install --user \
    flask==3.0.0 \
    flask-login==0.6.3 \
    werkzeug==3.0.1 \
    reportlab==4.0.8

# Step 3: Verify all imports work
echo "[3/4] Verifying all imports..."
python3.10 -c "
import pandas, numpy, sklearn, flask, flask_login, werkzeug, reportlab
print('All packages OK!')
print('pandas:', pandas.__version__)
print('flask:', flask.__version__)
print('sklearn:', sklearn.__version__)
"

# Step 4: Pre-cache the ML model
echo "[4/4] Pre-caching ML model..."
cd "$APP_DIR"
python3.10 -c "from model import train_model; train_model(); print('Model cached!')"

echo ""
echo "=== Setup complete! Go to Web tab and click Reload ==="
echo "Your site: https://kd3114.pythonanywhere.com"
