"""
Student Performance Predictor - Main Flask Application Factory & Entry Point.
"""

import os
from datetime import datetime
from flask import Flask, render_template
from config import Config
from backend.database.connection import setup_database, DATABASE_RUNTIME_STATUS
from backend.authentication.auth import get_current_user

def create_app(config_class=Config):
    # Specify templates and static folder in frontend/
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.join(base_dir, 'frontend', 'templates')
    static_dir = os.path.join(base_dir, 'frontend', 'static')

    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir
    )
    app.config.from_object(config_class)

    # Initialize Database & Seeding
    setup_database(app)

    # Register Blueprints
    from backend.routes.main_routes import main_bp
    from backend.routes.auth_routes import auth_bp
    from backend.routes.api_routes import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    # Global Template Context Processor
    @app.context_processor
    def inject_globals():
        return {
            'current_user': get_current_user(),
            'current_year': datetime.now().year,
            'db_status': DATABASE_RUNTIME_STATUS,
            'project_name': 'Student Performance Predictor'
        }

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', error_title="404 - Page Not Found",
                               error_msg="The page you requested does not exist."), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('base.html', error_title="500 - Server Error",
                               error_msg="An unexpected error occurred. Please try again later."), 500

    @app.errorhandler(403)
    def forbidden_error(e):
        return render_template('base.html', error_title="403 - Forbidden",
                               error_msg="You do not have permission to view this resource."), 403

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1')
    print(f"\n==============================================================")
    print(f"  STUDENT PERFORMANCE PREDICTOR - SERVER ACTIVE")
    print(f"  Local Browser URL:  http://127.0.0.1:{port}")
    print(f"  Network Alternate:  http://localhost:{port}")
    print(f"  (Do NOT type 0.0.0.0 in Windows browser)")
    print(f"  Database Status:    {DATABASE_RUNTIME_STATUS['message']}")
    print(f"==============================================================\n")
    app.run(host=host, port=port, debug=debug_mode)
