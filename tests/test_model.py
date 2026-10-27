"""
Machine Learning Model Inference Tests.
"""

import pytest
from backend.prediction.predictor import get_predictor

def test_model_loading():
    predictor = get_predictor()
    assert predictor.loaded is True, "Predictor failed to load serialized ML models"
    assert predictor.regressor is not None
    assert predictor.preprocessor is not None

def test_prediction_output_structure():
    predictor = get_predictor()
    raw_sample = {
        'Study_Hours_per_Week': '28',
        'Attendance_Rate': '92.0',
        'Past_Exam_Scores': '85',
        'Parental_Education_Level': 'Masters',
        'Extracurricular_Activities': 'Yes'
    }
    res = predictor.predict(raw_sample)
    assert 'predicted_score' in res
    assert 'pass_fail' in res
    assert 'performance_category' in res
    assert 'recommendations' in res
    assert 0 <= res['predicted_score'] <= 100
    assert res['pass_fail'] in ('Pass', 'Fail')
    assert isinstance(res['recommendations'], list)
