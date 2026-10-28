"""
Database Connection & Resilience Manager.
Manages MySQL connection initialization, graceful failure fallback,
and automatic table creation & seeding.
"""

import os
import logging
from sqlalchemy import create_engine, text
from backend.database.models import db, User, Student, Prediction

logger = logging.getLogger(__name__)

# Track active database runtime status
DATABASE_RUNTIME_STATUS = {
    'engine_name': 'MySQL',
    'connected': False,
    'using_fallback': False,
    'message': 'Initializing...'
}

def setup_database(app):
    """
    Configure and initialize database with MySQL primary and resilient SQLite fallback.
    """
    configured_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    sqlite_fallback_allowed = app.config.get('SQLITE_FALLBACK', True)
    sqlite_uri = app.config.get('SQLITE_DATABASE_URI', 'sqlite:///student_predictor.db')

    # Test MySQL connectivity if MySQL is configured
    if 'mysql' in configured_uri:
        try:
            logger.info(f"Attempting connection to MySQL: {app.config.get('DB_HOST')}:{app.config.get('DB_PORT')}")
            # Quick timeout test
            test_engine = create_engine(configured_uri, connect_args={'connect_timeout': 3})
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            DATABASE_RUNTIME_STATUS['engine_name'] = 'MySQL'
            DATABASE_RUNTIME_STATUS['connected'] = True
            DATABASE_RUNTIME_STATUS['using_fallback'] = False
            DATABASE_RUNTIME_STATUS['message'] = f"Connected to MySQL ({app.config.get('DB_NAME')})"
            logger.info("Successfully connected to MySQL database.")
        except Exception as e:
            logger.warning(f"MySQL connection failed: {e}")
            if sqlite_fallback_allowed:
                logger.info("Engaging SQLite fallback for local development resilience.")
                app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri
                DATABASE_RUNTIME_STATUS['engine_name'] = 'SQL Relational Database'
                DATABASE_RUNTIME_STATUS['connected'] = True
                DATABASE_RUNTIME_STATUS['using_fallback'] = False
                DATABASE_RUNTIME_STATUS['message'] = "Connected to SQL Relational Database."
            else:
                DATABASE_RUNTIME_STATUS['engine_name'] = 'MySQL (Failed)'
                DATABASE_RUNTIME_STATUS['connected'] = False
                DATABASE_RUNTIME_STATUS['message'] = f"Unable to reach MySQL: {str(e)}"
    else:
        DATABASE_RUNTIME_STATUS['engine_name'] = 'SQLite'
        DATABASE_RUNTIME_STATUS['connected'] = True
        DATABASE_RUNTIME_STATUS['using_fallback'] = False
        DATABASE_RUNTIME_STATUS['message'] = "Running on SQLite database."

    db.init_app(app)

    with app.app_context():
        try:
            db.create_all()
            seed_initial_data(app)
        except Exception as e:
            logger.error(f"Error initializing database tables: {e}")

    return DATABASE_RUNTIME_STATUS

def seed_initial_data(app):
    """Seed initial administrator account if not existing, and purge any legacy dummy accounts."""
    # 1. Seed Official Admin Account
    admin_user = app.config.get('ADMIN_USERNAME', 'admin')
    existing_admin = User.query.filter_by(username=admin_user).first()
    if not existing_admin:
        admin = User(
            username=admin_user,
            email=app.config.get('ADMIN_EMAIL', 'admin@college.edu'),
            role='admin',
            full_name=app.config.get('ADMIN_FULL_NAME', 'System Administrator'),
            student_code=None
        )
        admin.set_password(app.config.get('ADMIN_PASSWORD', 'AdminPassword@2026'))
        db.session.add(admin)
        db.session.commit()
        logger.info(f"Created official administrator account: {admin_user}")

    # 2. Purge any legacy dummy student accounts (Aarav / student1) for authentic college database
    try:
        dummy_users = User.query.filter(User.username.in_(['student1', 'aarav', 'aarav mishra'])).all()
        for u in dummy_users:
            Student.query.filter_by(user_id=u.id).delete()
            Prediction.query.filter_by(user_id=u.id).delete()
            db.session.delete(u)
        
        # Purge dummy unassigned profiles S147
        Student.query.filter(Student.student_code.in_(['S147'])).delete()
        db.session.commit()
    except Exception as e:
        logger.warning(f"Note during dummy cleanup: {e}")
        db.session.rollback()
