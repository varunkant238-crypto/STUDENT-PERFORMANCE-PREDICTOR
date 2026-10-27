"""
WSGI Entry Point for Production Deployment (Gunicorn, Waitress, uWSGI).
"""

from app import app

if __name__ == "__main__":
    app.run()
