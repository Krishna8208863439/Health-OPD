import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request
from flask_cors import CORS
from config import Config
from models import db, Prediction, ModelMetrics

def setup_logging(app):
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'app.log')

    # Remove existing handlers to avoid duplicates
    app.logger.handlers.clear()

    # Formatter for structured logs
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s (%(funcName)s:%(lineno)d): %(message)s'
    )

    # File Handler (Rotating at 5MB, keep 5 backups)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Console Stream Handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(stream_handler)

    # Also capture werkzeug / root logging to file
    logging.getLogger('werkzeug').addHandler(file_handler)
    app.logger.info("HealthPredict AI structured logging system initialized.")


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Logging
    setup_logging(app)

    # Initialize SQLAlchemy database
    db.init_app(app)

    # Enable CORS for frontend Vite dev server and production
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Ensure database directory exists
    db_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database'))
    os.makedirs(db_dir, exist_ok=True)

    # Auto-create tables on startup
    with app.app_context():
        db.create_all()

    # Request logger
    @app.before_request
    def log_request_info():
        if request.path.startswith('/api'):
            app.logger.info(f"Incoming Request: {request.method} {request.path} | Remote: {request.remote_addr}")

    # Centralized Error Handlers (Return clean JSON, full traceback to logs only)
    @app.errorhandler(400)
    def bad_request_handler(e):
        app.logger.warning(f"400 Bad Request on {request.path}: {str(e)}")
        return jsonify({"error": "Bad request", "message": str(e)}), 400

    @app.errorhandler(404)
    def not_found_handler(e):
        app.logger.warning(f"404 Not Found on {request.path}")
        return jsonify({"error": "Resource not found", "message": f"Endpoint '{request.path}' does not exist"}), 404

    @app.errorhandler(405)
    def method_not_allowed_handler(e):
        app.logger.warning(f"405 Method Not Allowed on {request.path}")
        return jsonify({"error": "Method not allowed", "message": f"HTTP {request.method} is not permitted for this endpoint"}), 405

    @app.errorhandler(500)
    def internal_server_error_handler(e):
        app.logger.exception(f"500 Internal Server Error on {request.path}: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred on the server. Please check input parameters or try again later."
        }), 500

    @app.errorhandler(Exception)
    def unhandled_exception_handler(e):
        app.logger.exception(f"Unhandled Exception on {request.path}: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred on the server. Please check input parameters or try again later."
        }), 500

    # Register API Blueprint (Predictions, Dashboard, Metrics, Reports)
    from routes.api_routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Core Health Check Route
    @app.route('/api/health', methods=['GET'])
    def health_check():
        app.logger.info("Health check endpoint queried successfully.")
        return jsonify({"status": "ok"})

    # Deliberate error test endpoint for Phase 5 verification
    @app.route('/api/test-error', methods=['GET'])
    def test_error_route():
        app.logger.info("Executing deliberate test error trigger for Phase 5 verification...")
        raise RuntimeError("Deliberate 500 error triggered for Phase 5 error handling & logging verification")

    return app

app = create_app()

if __name__ == '__main__':
    port = app.config.get('PORT', 5000)
    # Debug False for production exception trapping verification, or read from env
    debug_mode = app.config.get('DEBUG', False)
    print(f"Starting HealthPredict AI Flask Server on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
