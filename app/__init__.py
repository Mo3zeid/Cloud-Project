"""Flask application factory."""

import os
from flask import Flask
from config import Config
from app.extensions import db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure directories exist
    os.makedirs(app.config.get("UPLOAD_FOLDER", "uploads"), exist_ok=True)
    os.makedirs(app.config.get("RESULTS_FOLDER", "results"), exist_ok=True)
    os.makedirs(os.path.join(app.instance_path), exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # User loader for Flask-Login
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app.auth import auth_bp
    from app.portal import portal_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(portal_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    # Start background job runner (only in worker process to avoid reloading race conditions)
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.config["DEBUG"]:
        from app.services.job_runner import start_job_runner
        start_job_runner(app)

    return app
