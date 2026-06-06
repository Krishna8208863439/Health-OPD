#!/bin/bash
# ── Run this once on PythonAnywhere to set up everything ──────────────────────
# Usage: bash setup_and_run.sh

echo "===== HealthCare Plus Setup ====="

# Step 1: Install all required packages
echo "[1/3] Installing Python packages..."
pip install \
    pandas==2.1.4 \
    scikit-learn==1.3.2 \
    numpy==1.26.2 \
    flask==3.0.0 \
    flask-login==0.6.3 \
    werkzeug==3.0.1 \
    reportlab==4.0.8 \
    gunicorn==21.2.0

echo "[2/3] Verifying installs..."
python -c "import pandas, sklearn, numpy, flask, flask_login, reportlab; print('All packages OK')"

echo "[3/3] Pre-training and caching ML model..."
python -c "from model import train_model; train_model(); print('Model cached OK')"

echo ""
echo "===== Setup complete! Now go to Web tab and click Reload ====="
