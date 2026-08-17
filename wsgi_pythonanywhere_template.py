# ==============================================================================
# HealthPredict AI — WSGI Configuration for PythonAnywhere
# File Location: /var/www/kd3114_pythonanywhere_com_wsgi.py
# ==============================================================================

import sys
import os

# 1. Add project paths to sys.path
backend_dir = '/home/kd3114/Health-OPD/backend'
root_dir = '/home/kd3114/Health-OPD'

for p in [backend_dir, root_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

# 2. Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['DEBUG'] = 'False'

# 3. Import and expose the Flask WSGI application instance
try:
    from app import app as application
except Exception as e:
    import traceback
    print("CRITICAL ERROR INITIALIZING FLASK WSGI APPLICATION:", file=sys.stderr)
    traceback.print_exc()
    raise e
