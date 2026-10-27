"""
Main Page Routes (Home, Dashboard, Prediction, Records, Graphs, About).
Enforces permissions and prepares structured view data.
"""

import os
import json
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from backend.authentication.auth import login_required, get_current_user
from backend.services.student_service import get_dashboard_metrics, save_prediction, get_student_records
from backend.prediction.predictor import get_predictor
from preprocessing.preprocessing import FEATURE_CONSTRAINTS, validate_and_format_input
from backend.database.connection import DATABASE_RUNTIME_STATUS

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    """Page 1: Home Landing Page."""
    current_user = get_current_user()
    return render_template('home.html', user=current_user, db_status=DATABASE_RUNTIME_STATUS)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Page 2: Role-based Dashboard."""
    user = get_current_user()
    metrics = get_dashboard_metrics(user)
    
    # Load model evaluation summary for dashboard card
    predictor = get_predictor()
    model_meta = predictor.metadata

    return render_template(
        'dashboard.html',
        user=user,
        metrics=metrics,
        model_meta=model_meta,
        db_status=DATABASE_RUNTIME_STATUS
    )

@main_bp.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    """Page 3: Student Prediction."""
    user = get_current_user()
    prediction_result = None
    form_values = {}
    error_message = None

    if request.method == 'POST':
        raw_input = {
            'Study_Hours_per_Week': request.form.get('study_hours', ''),
            'Attendance_Rate': request.form.get('attendance_rate', ''),
            'Past_Exam_Scores': request.form.get('past_scores', ''),
            'Parental_Education_Level': request.form.get('parental_education', ''),
            'Extracurricular_Activities': request.form.get('extracurricular', '')
        }
        form_values = raw_input
        student_code = request.form.get('student_code', user.student_code or f"STU-{user.id:03d}").strip()

        try:
            # 1. Validate and convert via preprocessing module
            clean_df, val_error = validate_and_format_input(raw_input)
            if val_error:
                error_message = val_error
            else:
                predictor = get_predictor()
                prediction_result = predictor.predict(raw_input)

                # 2. Persist to MySQL database
                save_prediction(user, clean_df, prediction_result, student_code=student_code)
                flash("Prediction computed and recorded in database successfully!", "success")

        except Exception as e:
            error_message = f"Prediction computation failed: {str(e)}"

    return render_template(
        'prediction.html',
        user=user,
        constraints=FEATURE_CONSTRAINTS,
        result=prediction_result,
        form_values=form_values,
        error_message=error_message,
        db_status=DATABASE_RUNTIME_STATUS
    )

@main_bp.route('/records')
@login_required
def student_records():
    """Page 4: Student Records & Prediction History."""
    user = get_current_user()
    search_query = request.args.get('search', '').strip()
    filter_status = request.args.get('status', '').strip()

    records = get_student_records(user, search_query=search_query, filter_status=filter_status)

    return render_template(
        'student_records.html',
        user=user,
        records=records,
        search_query=search_query,
        filter_status=filter_status,
        db_status=DATABASE_RUNTIME_STATUS
    )

@main_bp.route('/graphs')
@login_required
def graphs():
    """Page 5: Dedicated Analytics and Graphs."""
    user = get_current_user()
    predictor = get_predictor()
    model_meta = predictor.metadata

    # Check available generated image files
    static_img_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'static', 'images')
    available_images = os.listdir(static_img_dir) if os.path.exists(static_img_dir) else []

    return render_template(
        'graphs.html',
        user=user,
        model_meta=model_meta,
        available_images=available_images,
        db_status=DATABASE_RUNTIME_STATUS
    )

@main_bp.route('/about')
def about():
    """Page 6: About Project & Documentation."""
    user = get_current_user()
    predictor = get_predictor()
    model_meta = predictor.metadata
    return render_template('about.html', user=user, model_meta=model_meta, db_status=DATABASE_RUNTIME_STATUS)
