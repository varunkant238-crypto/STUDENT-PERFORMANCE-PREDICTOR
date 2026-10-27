"""
Database Initialization Script for Student Performance Predictor.
Tests MySQL connectivity, creates the schema, and seeds default accounts.
"""

import os
import pymysql
from config import Config
from app import create_app
from backend.database.models import db, User, Student, Prediction

def initialize():
    print("=" * 60)
    print("  STUDENT PERFORMANCE PREDICTOR - DATABASE INITIALIZATION")
    print("=" * 60)

    # Attempt MySQL Database Creation if server is reachable
    try:
        print(f"[INFO] Connecting to MySQL server on {Config.DB_HOST}:{Config.DB_PORT} as '{Config.DB_USER}'...")
        conn = pymysql.connect(
            host=Config.DB_HOST,
            port=int(Config.DB_PORT),
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            connect_timeout=3
        )
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            print(f"[SUCCESS] MySQL database '{Config.DB_NAME}' ensured.")
        conn.close()
    except Exception as e:
        print(f"[NOTICE] MySQL direct database creation notice: {e}")
        print("[NOTICE] If MySQL is not running yet, SQLite fallback will be used locally.")

    # Run Flask-SQLAlchemy table creation and seeding
    app = create_app()
    with app.app_context():
        db.create_all()
        print("[SUCCESS] Database tables verified / created.")
        print(f"[SUCCESS] Users count: {User.query.count()}")
        print(f"[SUCCESS] Students count: {Student.query.count()}")
        print(f"[SUCCESS] Predictions count: {Prediction.query.count()}")
    print("=" * 60)
    print("  INITIALIZATION COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    initialize()
