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
                DATABASE_RUNTIME_STATUS['engine_name'] = 'SQLite (Local Fallback)'
                DATABASE_RUNTIME_STATUS['connected'] = True
                DATABASE_RUNTIME_STATUS['using_fallback'] = True
                DATABASE_RUNTIME_STATUS['message'] = "MySQL offline; running on local SQLite fallback. Start MySQL for production."
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
    """Seed initial administrator account and base student profiles if not existing."""
    # 1. Seed Admin
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
        logger.info(f"Created initial admin user: {admin_user}")

    # 2. Seed Demo Student User
    demo_student = User.query.filter_by(username='student1').first()
    if not demo_student:
        student = User(
            username='student1',
            email='student1@college.edu',
            role='student',
            full_name='Aarav Sharma',
            student_code='S147'
        )
        student.set_password('StudentPassword@2026')
        db.session.add(student)
        db.session.commit()

        # Add profile
        profile = Student(
            student_code='S147',
            gender='Male',
            user_id=student.id
        )
        db.session.add(profile)
        db.session.commit()
        logger.info("Created demo student account: student1 (S147)")

    # 3. Seed initial student records from dataset if empty
    if Student.query.count() < 5:
        initial_students = [
            ('S136', 'Male'),
            ('S209', 'Female'),
            ('S458', 'Female'),
            ('S078', 'Female'),
            ('S235', 'Male'),
        ]
        for code, gen in initial_students:
            if not Student.query.filter_by(student_code=code).first():
                db.session.add(Student(student_code=code, gender=gen))
        db.session.commit()
