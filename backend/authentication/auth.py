"""
Authentication and Authorization Module.
Provides login/logout session handling and role-based access decorators.
"""

from functools import wraps
from flask import session, redirect, url_for, flash, request
from backend.database.models import db, User

def login_user(user: User):
    """Store authenticated user details in Flask session."""
    session.clear()
    session['user_id'] = user.id
    session['username'] = user.username
    session['role'] = user.role
    session['full_name'] = user.full_name
    session['student_code'] = user.student_code or ''

def logout_user():
    """Clear active user session."""
    session.clear()

def get_current_user():
    """Retrieve logged-in User instance from database or None."""
    user_id = session.get('user_id')
    if user_id:
        return db.session.get(User, user_id)
    return None

def login_required(f):
    """Enforces authentication for protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Enforces administrator role for privileged routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in as an Administrator.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        if session.get('role') != 'admin':
            flash("Access denied: Administrator privileges required.", "danger")
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function
