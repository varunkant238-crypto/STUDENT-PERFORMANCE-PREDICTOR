"""
Application Configuration Module.
Loads environment variables and sets up database and Flask application parameters.
"""

import os
import urllib.parse
from datetime import timedelta
from dotenv import load_dotenv

# Load .env file from project root
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_mini_project_secret_key_change_me')
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
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

    # Permanent Cloud PostgreSQL Database URI (Neon Serverless Cloud)
    NEON_DATABASE_URI = (
        "postgresql+psycopg2://neondb_owner:npg_wvDzkbdVS54R@"
        "ep-gentle-glitter-b7leqjr5-pooler.c-13.us-east-1.aws.neon.tech/neondb?sslmode=require"
    )

    # Database URI configuration: supports DATABASE_URL or defaults to permanent Cloud PostgreSQL
    raw_db_url = os.environ.get('DATABASE_URL')
    if raw_db_url:
        if raw_db_url.startswith('postgres://'):
            raw_db_url = raw_db_url.replace('postgres://', 'postgresql+psycopg2://', 1)
        elif raw_db_url.startswith('postgresql://') and not raw_db_url.startswith('postgresql+psycopg2://'):
            raw_db_url = raw_db_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
        SQLALCHEMY_DATABASE_URI = raw_db_url
    else:
        # Default to permanent Cloud PostgreSQL for zero data loss across redeployments
        SQLALCHEMY_DATABASE_URI = NEON_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Initial Admin Seed Configuration
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'AdminPassword@2026')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@college.edu')
    ADMIN_FULL_NAME = os.environ.get('ADMIN_FULL_NAME', 'System Administrator')

    # Allow automatic SQLite fallback if MySQL is unreachable during development
    SQLITE_FALLBACK = os.environ.get('SQLITE_FALLBACK', 'True').lower() in ('true', '1', 't')
