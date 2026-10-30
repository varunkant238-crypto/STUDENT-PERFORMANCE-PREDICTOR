"""
Student Service Module.
Handles database queries, business logic, analytics calculations,
and student profile management.
"""

from sqlalchemy import func
from backend.database.models import db, User, Student, Prediction, get_ist_now

def get_dashboard_metrics(user):
    """
    Compute role-based analytics metrics.
    Admin sees global institution stats; Student sees personal statistics.
    """
    if user.is_admin:
        total_students = Student.query.count()
        total_predictions = Prediction.query.count()
        
        # Pass rate calculation
        pass_count = Prediction.query.filter_by(pass_fail='Pass').count()
        pass_rate = round((pass_count / total_predictions * 100), 1) if total_predictions > 0 else 0.0

        # Average predicted score
        avg_score_res = db.session.query(func.avg(Prediction.predicted_score)).scalar()
        avg_score = round(float(avg_score_res), 1) if avg_score_res else 0.0

        # Recent 5 predictions across all students
        recent_predictions = Prediction.query.order_by(Prediction.created_at.desc()).limit(5).all()

        return {
            'role': 'admin',
            'total_students': total_students,
            'total_predictions': total_predictions,
            'pass_rate': pass_rate,
            'avg_score': avg_score,
            'recent_predictions': recent_predictions
        }
    else:
        # Student personal metrics
        user_predictions = Prediction.query.filter_by(user_id=user.id).order_by(Prediction.created_at.desc()).all()
        total_predictions = len(user_predictions)
        
        pass_count = sum(1 for p in user_predictions if p.pass_fail == 'Pass')
        pass_rate = round((pass_count / total_predictions * 100), 1) if total_predictions > 0 else 0.0

        scores = [p.predicted_score for p in user_predictions]
        avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0
        latest_prediction = user_predictions[0] if user_predictions else None

        return {
            'role': 'student',
            'total_predictions': total_predictions,
            'pass_rate': pass_rate,
            'avg_score': avg_score,
            'latest_prediction': latest_prediction,
            'recent_predictions': user_predictions[:5]
        }

def save_prediction(user, input_data, prediction_result, student_code=None):
    """Save a validated prediction attempt into MySQL database."""
    if not student_code:
        student_code = user.student_code or f"STU-{user.id:03d}"

    prediction = Prediction(
        user_id=user.id,
        student_code=student_code,
        study_hours=int(input_data['Study_Hours_per_Week'].iloc[0]),
        attendance_rate=float(input_data['Attendance_Rate'].iloc[0]),
        past_scores=int(input_data['Past_Exam_Scores'].iloc[0]),
        parental_education=str(input_data['Parental_Education_Level'].iloc[0]),
        extracurricular=str(input_data['Extracurricular_Activities'].iloc[0]),
        predicted_score=float(prediction_result['predicted_score']),
        pass_fail=str(prediction_result['pass_fail']),
        performance_category=str(prediction_result['performance_category']),
        created_at=get_ist_now()
    )
    db.session.add(prediction)
    db.session.commit()

    # Synchronize with persistent store for instant recovery across restarts
    try:
        from backend.database.persistent_sync import record_persistent_prediction
        record_persistent_prediction(prediction, user.username)
    except Exception:
        pass

    return prediction

def get_student_records(user, search_query=None, filter_status=None):
    """
    Retrieve student records respecting privacy and authorization.
    Admins can view all records and predictions; Students see only their own.
    """
    if user.is_admin:
        query = db.session.query(
            Prediction, User
        ).join(User, Prediction.user_id == User.id)

        if search_query:
            q = f"%{search_query.strip()}%"
            query = query.filter(
                (Prediction.student_code.ilike(q)) |
                (User.full_name.ilike(q)) |
                (User.username.ilike(q))
            )
        if filter_status and filter_status in ('Pass', 'Fail'):
            query = query.filter(Prediction.pass_fail == filter_status)

        results = query.order_by(Prediction.created_at.desc()).all()
        records = []
        for pred, usr in results:
            records.append({
                'id': pred.id,
                'student_code': pred.student_code,
                'full_name': usr.full_name,
                'username': usr.username,
                'study_hours': pred.study_hours,
                'attendance_rate': pred.attendance_rate,
                'past_scores': pred.past_scores,
                'parental_education': pred.parental_education,
                'extracurricular': pred.extracurricular,
                'predicted_score': pred.predicted_score,
                'pass_fail': pred.pass_fail,
                'performance_category': pred.performance_category,
                'created_at': pred.created_at.strftime('%d %b %Y, %I:%M %p') if pred.created_at else ''
            })
        return records
    else:
        # Students see only their own submissions
        query = Prediction.query.filter_by(user_id=user.id)
        if filter_status and filter_status in ('Pass', 'Fail'):
            query = query.filter_by(pass_fail=filter_status)
        results = query.order_by(Prediction.created_at.desc()).all()
        return [p.to_dict() for p in results]
