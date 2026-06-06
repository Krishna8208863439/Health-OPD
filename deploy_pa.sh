#!/bin/bash

# Exit on error
set -e

USER=$(whoami)
echo "=========================================================="
echo "🏥 Smart Healthcare System: PythonAnywhere Deployer 🏥"
echo "Username: $USER"
echo "=========================================================="

# 1. Setup paths
REPO_DIR="$HOME/Health-OPD"
PROJECT_DIR="$REPO_DIR/Smart_Healthcare_System (2)/Smart_Healthcare_System/Enhanced_Healthcare_System"

# 2. Clone or pull the code
if [ -d "$REPO_DIR" ]; then
    echo "Updating existing repository in $REPO_DIR..."
    cd "$REPO_DIR"
    git pull origin main
else
    echo "Cloning repository to $REPO_DIR..."
    git clone https://github.com/Krishna8208863439/Health-OPD.git "$REPO_DIR"
fi

# 3. Create virtual environment (clean up old first to save disk space)
VENV_DIR="$HOME/.virtualenvs/healthcare-env"
echo "Setting up virtualenv at $VENV_DIR..."
rm -rf "$VENV_DIR" || true
virtualenv --python=/usr/bin/python3.10 --system-site-packages "$VENV_DIR"

# 4. Activate virtualenv and install dependencies
source "$VENV_DIR/bin/activate"
echo "Installing requirements..."
pip install --no-cache-dir -r "$PROJECT_DIR/requirements.txt"

echo "=========================================================="
echo "✅ Local deployment preparation completed successfully!"
echo "=========================================================="
