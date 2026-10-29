"""
Application Configuration Module.
Loads environment variables and sets up database and Flask application parameters.
"""

import os
import urllib.parse
from dotenv import load_dotenv

# Load .env file from project root
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_mini_project_secret_key_change_me')
    
    # MySQL Database credentials
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME', 'student_predictor_db')

    # Safely URL-encode user & password for special characters (e.g. '@', '%', ':')
    encoded_user = urllib.parse.quote_plus(DB_USER)
    encoded_pass = urllib.parse.quote_plus(DB_PASSWORD) if DB_PASSWORD else ''

    # Construct primary MySQL connection URI
    if encoded_pass:
        MYSQL_DATABASE_URI = f"mysql+pymysql://{encoded_user}:{encoded_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        MYSQL_DATABASE_URI = f"mysql+pymysql://{encoded_user}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Local fallback SQLite URI
    SQLITE_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'student_predictor.db')}"

    # Database URI configuration: supports DATABASE_URL (Cloud PostgreSQL / TiDB MySQL) or local MySQL / SQLite
    raw_db_url = os.environ.get('DATABASE_URL')
    if raw_db_url:
        if raw_db_url.startswith('postgres://'):
            raw_db_url = raw_db_url.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = raw_db_url
    else:
        SQLALCHEMY_DATABASE_URI = MYSQL_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Initial Admin Seed Configuration
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'AdminPassword@2026')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@college.edu')
    ADMIN_FULL_NAME = os.environ.get('ADMIN_FULL_NAME', 'System Administrator')

    # Allow automatic SQLite fallback if MySQL is unreachable during development
    SQLITE_FALLBACK = os.environ.get('SQLITE_FALLBACK', 'True').lower() in ('true', '1', 't')
