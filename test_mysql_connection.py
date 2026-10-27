"""
Quick MySQL Connectivity Verification Script.
Checks if MySQL Server is running, tests credentials from .env,
and checks if student_predictor_db is accessible.
"""

import os
import sys
import pymysql
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
load_dotenv('.env')

DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('DB_PORT', '3306'))
DB_NAME = os.environ.get('DB_NAME', 'student_predictor_db')

def test_connection():
    print("=" * 60)
    print("  MYSQL CONNECTION TEST")
    print(f"  Target: {DB_HOST}:{DB_PORT} | User: {DB_USER}")
    print("=" * 60)

    try:
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=3
        )
        print("[SUCCESS] Connected to MySQL Server!")

        with conn.cursor() as cur:
            cur.execute("SELECT VERSION()")
            ver = cur.fetchone()[0]
            print(f"[INFO] MySQL Version: {ver}")

            cur.execute("SHOW DATABASES LIKE %s", (DB_NAME,))
            db_exists = cur.fetchone() is not None
            if db_exists:
                print(f"[SUCCESS] Database '{DB_NAME}' already exists.")
            else:
                print(f"[NOTICE] Database '{DB_NAME}' not created yet. Run migrate_sqlite_to_mysql.py to create it.")

        conn.close()
        print("=" * 60)
        print("  STATUS: MYSQL IS READY!")
        print("=" * 60)
        return True

    except pymysql.err.OperationalError as e:
        code, msg = e.args
        print(f"[FAIL] Could not connect to MySQL: {msg} (Error {code})")
        if code == 2003:
            print("[EXPLANATION] MySQL service is not running or port 3306 is not active.")
        elif code in (1045, 1698):
            print("[EXPLANATION] Access denied! Check DB_PASSWORD in your .env file.")
        print("=" * 60)
        return False
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        print("=" * 60)
        return False

if __name__ == '__main__':
    test_connection()
