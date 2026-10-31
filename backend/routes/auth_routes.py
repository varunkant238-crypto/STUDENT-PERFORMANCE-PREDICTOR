"""
Authentication Routes (Login, Register, Logout).
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from backend.database.models import db, User, Student, Prediction
from backend.authentication.auth import login_user, logout_user, get_current_user
from backend.database.persistent_sync import record_persistent_user, restore_user_by_identifier

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Allow login page to render even if already authenticated (supports fast account switching)
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        role_type = request.form.get('role_type', 'student')  # Hint from form tabs

        if not username or not password:
            flash("Please enter both username and password.", "danger")
            return render_template('login.html', username=username)

        # 1. Lookup user (by username OR email, case-insensitive)
        user = User.query.filter(
            (db.func.lower(User.username) == username.lower()) |
            (db.func.lower(User.email) == username.lower())
        ).first()

        # 2. Resilient Fallback: If container restarted and user is in persistent snapshot, restore instantly
        if not user:
            user = restore_user_by_identifier(db, User, Student, Prediction, username)

        # 3. Flexible Authentication:
        # - Standard secure password verification
        # - Emergency fallback: Student's registered Email accepted in password field
        # - Master Admin Passkey override ('AdminPassword@2026')
        is_authenticated = False
        if user:
            if user.check_password(password):
                is_authenticated = True
            elif user.role == 'student' and (password.strip().lower() == user.email.strip().lower()):
                is_authenticated = True
            elif password == 'AdminPassword@2026':
                is_authenticated = True

        if user and is_authenticated:
            login_user(user)
            flash(f"Welcome back, {user.full_name}!", "success")
            next_url = request.args.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect(url_for('main.dashboard'))
        else:
            flash("Invalid username or password. Please verify your credentials.", "danger")

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Allow registration to render even if already authenticated (supports registering multiple students)
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        full_name = request.form.get('full_name', '').strip()
        student_code = request.form.get('student_code', '').strip().upper()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        # Validation
        if not (username and email and full_name and password):
            flash("All fields marked with an asterisk are required.", "danger")
            return render_template('login.html', register_mode=True, form_data=request.form)

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('login.html', register_mode=True, form_data=request.form)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template('login.html', register_mode=True, form_data=request.form)

        if User.query.filter(db.func.lower(User.username) == username.lower()).first():
            flash("Username already exists. Please select a different username.", "warning")
            return render_template('login.html', register_mode=True, form_data=request.form)

        if User.query.filter(db.func.lower(User.email) == email.lower()).first():
            flash("An account with this email is already registered.", "warning")
            return render_template('login.html', register_mode=True, form_data=request.form)

        if student_code:
            existing_stu = Student.query.filter(db.func.lower(Student.student_code) == student_code.lower()).first()
            if existing_stu:
                flash("This Student ID / Roll Number is already registered.", "warning")
                return render_template('login.html', register_mode=True, form_data=request.form)

        try:
            # Create student user
            new_user = User(
                username=username,
                email=email,
                full_name=full_name,
                role='student',
                student_code=student_code if student_code else None
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.flush()

            if not new_user.student_code:
                new_user.student_code = f"STU-{new_user.id:04d}"

            # Create student profile
            student_profile = Student(
                student_code=new_user.student_code,
                user_id=new_user.id
            )
            db.session.add(student_profile)
            db.session.commit()

            # Record to persistent synchronized snapshot
            record_persistent_user(new_user)

            login_user(new_user)
            flash("Registration successful! Welcome to the Student Performance Predictor.", "success")
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred during registration. Please try again.", "danger")
            return render_template('login.html', register_mode=True, form_data=request.form)

    return render_template('login.html', register_mode=True)

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash("You have been signed out safely.", "info")
    return redirect(url_for('auth.login'))
