"""
Safe Migration Utility: SQLite to MySQL
Transfers all existing users, student profiles, and prediction history
from local SQLite (student_predictor.db) into MySQL without data loss.
"""

import os
import sys
import sqlite3
import pymysql
from dotenv import load_dotenv

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
load_dotenv('.env')

DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('DB_PORT', '3306'))
DB_NAME = os.environ.get('DB_NAME', 'student_predictor_db')

SQLITE_PATH = os.path.join(os.path.dirname(__file__), 'student_predictor.db')

def migrate():
    print("=" * 60)
    print("  STUDENT PERFORMANCE PREDICTOR - DATA MIGRATION")
    print("  Source: SQLite (student_predictor.db) -> Target: MySQL")
    print("=" * 60)

    if not os.path.exists(SQLITE_PATH):
        print(f"[ERROR] Source SQLite database not found at {SQLITE_PATH}")
        return False

    # 1. Connect to MySQL Server
    try:
        print(f"[INFO] Connecting to MySQL server at {DB_HOST}:{DB_PORT} as '{DB_USER}'...")
        conn_mysql_server = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4'
        )
        with conn_mysql_server.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            print(f"[SUCCESS] Database `{DB_NAME}` verified on MySQL.")
        conn_mysql_server.close()
    except Exception as e:
        print(f"[ERROR] Could not connect to MySQL server: {e}")
        print("[TIP] Ensure MySQL service is running and credentials in .env are correct.")
        return False

    # 2. Initialize SQLAlchemy Schema in MySQL
    from app import create_app
    from backend.database.models import db, User, Student, Prediction

    app = create_app()
    with app.app_context():
        # Ensure schema tables exist
        db.create_all()
        print("[SUCCESS] MySQL schema tables ensured.")

    # 3. Read SQLite Records
    conn_sqlite = sqlite3.connect(SQLITE_PATH)
    cur_sqlite = conn_sqlite.cursor()

    cur_sqlite.execute("SELECT id, username, email, password_hash, role, full_name, student_code, created_at FROM users")
    sqlite_users = cur_sqlite.fetchall()

    cur_sqlite.execute("SELECT id, student_code, gender, user_id, created_at FROM students")
    sqlite_students = cur_sqlite.fetchall()

    cur_sqlite.execute("""
        SELECT id, user_id, student_code, study_hours, attendance_rate, past_scores, 
               parental_education, extracurricular, predicted_score, pass_fail, 
               performance_category, created_at 
        FROM predictions
    """)
    sqlite_predictions = cur_sqlite.fetchall()

    print(f"\n[INFO] Found in SQLite:")
    print(f"  - Users: {len(sqlite_users)}")
    print(f"  - Students: {len(sqlite_students)}")
    print(f"  - Predictions: {len(sqlite_predictions)}")

    # 4. Insert into MySQL (Upsert / Ignore existing)
    conn_mysql = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8mb4'
    )
    cur_mysql = conn_mysql.cursor()

    try:
        # A. Users
        for u in sqlite_users:
            cur_mysql.execute("""
                INSERT INTO users (id, username, email, password_hash, role, full_name, student_code, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    email = VALUES(email),
                    full_name = VALUES(full_name),
                    student_code = VALUES(student_code);
            """, u)

        # B. Students
        for s in sqlite_students:
            cur_mysql.execute("""
                INSERT INTO students (id, student_code, gender, user_id, created_at)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    gender = VALUES(gender),
                    user_id = VALUES(user_id);
            """, s)

        # C. Predictions
        for p in sqlite_predictions:
            cur_mysql.execute("""
                INSERT INTO predictions (id, user_id, student_code, study_hours, attendance_rate, 
                                         past_scores, parental_education, extracurricular, 
                                         predicted_score, pass_fail, performance_category, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    predicted_score = VALUES(predicted_score),
                    pass_fail = VALUES(pass_fail);
            """, p)

        conn_mysql.commit()
        print("\n[SUCCESS] Migration committed to MySQL successfully!")

        # Verify Counts in MySQL
        cur_mysql.execute("SELECT COUNT(*) FROM users")
        cnt_u = cur_mysql.fetchone()[0]
        cur_mysql.execute("SELECT COUNT(*) FROM students")
        cnt_s = cur_mysql.fetchone()[0]
        cur_mysql.execute("SELECT COUNT(*) FROM predictions")
        cnt_p = cur_mysql.fetchone()[0]

        print(f"[VERIFIED IN MYSQL]:")
        print(f"  - Users in MySQL: {cnt_u}")
        print(f"  - Students in MySQL: {cnt_s}")
        print(f"  - Predictions in MySQL: {cnt_p}")
        print("=" * 60)
        print("  MIGRATION COMPLETE")
        print("=" * 60)
        return True

    except Exception as e:
        conn_mysql.rollback()
        print(f"[ERROR] Migration failed: {e}")
        return False
    finally:
        cur_sqlite.close()
        conn_sqlite.close()
        cur_mysql.close()
        conn_mysql.close()

if __name__ == '__main__':
    migrate()
