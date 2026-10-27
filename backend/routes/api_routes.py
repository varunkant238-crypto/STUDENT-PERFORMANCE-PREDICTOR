"""
API Endpoints for Student Performance Predictor.
"""

from flask import Blueprint, jsonify, request
from backend.prediction.predictor import get_predictor
from backend.authentication.auth import login_required, get_current_user
from backend.database.models import Prediction
from backend.services.student_service import save_prediction
from preprocessing.preprocessing import validate_and_format_input

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/health', methods=['GET'])
def health_check():
    predictor = get_predictor()
    return jsonify({
        'status': 'healthy',
        'model_loaded': predictor.loaded,
        'features': predictor.metadata.get('selected_features', [])
    })

@api_bp.route('/predict', methods=['POST'])
@login_required
def api_predict():
    user = get_current_user()
    data = request.get_json() or {}
    try:
        clean_df, val_error = validate_and_format_input(data)
        if val_error:
            return jsonify({'success': False, 'error': val_error}), 400

        predictor = get_predictor()
        res = predictor.predict(data)
        
        # Save to database
        student_code = data.get('student_code', user.student_code or f"STU-{user.id:03d}")
        save_prediction(user, clean_df, res, student_code=student_code)

        return jsonify({'success': True, 'data': res})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/analytics-data', methods=['GET'])
@login_required
def analytics_data():
    """Returns aggregated stats for frontend charts."""
    user = get_current_user()
    if user.is_admin:
        predictions = Prediction.query.all()
    else:
        predictions = Prediction.query.filter_by(user_id=user.id).all()

    pass_count = sum(1 for p in predictions if p.pass_fail == 'Pass')
    fail_count = sum(1 for p in predictions if p.pass_fail == 'Fail')

    # Categories
    categories = {}
    for p in predictions:
        cat = p.performance_category
        categories[cat] = categories.get(cat, 0) + 1

    return jsonify({
        'pass_fail': {'Pass': pass_count, 'Fail': fail_count},
        'categories': categories,
        'total': len(predictions)
    })
