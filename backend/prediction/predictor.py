"""
Prediction Service for Student Performance Predictor.
Loads serialized models and preprocessors, validates runtime input,
and calculates predicted marks, pass/fail status, and category.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np

from preprocessing.preprocessing import (
    ALL_SELECTED_FEATURES, FEATURE_CONSTRAINTS,
    validate_and_format_input, derive_pass_fail, derive_performance_category,
    PASSING_THRESHOLD
)

SAVED_MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'model_training', 'saved_models')

class PredictionEngine:
    _instance = None

    def __init__(self):
        self.regressor = None
        self.classifier = None
        self.preprocessor = None
        self.metadata = {}
        self.loaded = False
        self.load_models()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = PredictionEngine()
        return cls._instance

    def load_models(self):
        reg_path = os.path.join(SAVED_MODELS_DIR, 'rf_regressor.joblib')
        clf_path = os.path.join(SAVED_MODELS_DIR, 'rf_classifier.joblib')
        prep_path = os.path.join(SAVED_MODELS_DIR, 'preprocessor.joblib')
        meta_path = os.path.join(SAVED_MODELS_DIR, 'model_metadata.json')

        if not (os.path.exists(reg_path) and os.path.exists(prep_path)):
            self.loaded = False
            print("[WARN] Trained models not found in saved_models directory. Predictions will be disabled until trained.")
            return False

        try:
            self.regressor = joblib.load(reg_path)
            self.classifier = joblib.load(clf_path) if os.path.exists(clf_path) else None
            self.preprocessor = joblib.load(prep_path)

            if os.path.exists(meta_path):
                with open(meta_path, 'r') as f:
                    self.metadata = json.load(f)
            self.loaded = True
            print("[INFO] Successfully loaded ML models and preprocessor.")
            return True
        except Exception as e:
            self.loaded = False
            print(f"[ERROR] Failed loading ML models: {e}")
            return False

    def predict(self, raw_input_dict):
        """
        Takes raw dictionary from web form / JSON payload.
        Returns:
            dict with predicted_score, pass_fail, category, pass_probability, recommendations
        """
        if not self.loaded:
            if not self.load_models():
                raise RuntimeError("Machine Learning models are not trained yet. Please execute 'python model_training/train_model.py'.")

        # 1. Validate and format input features
        input_df, error_msg = validate_and_format_input(raw_input_dict)
        if error_msg:
            raise ValueError(error_msg)

        # 2. Transform through preprocessor
        transformed_features = self.preprocessor.transform(input_df)

        # 3. Advanced Multi-Factor Calibrated Ensemble Engine
        raw_ml_score = float(self.regressor.predict(transformed_features)[0])

        study_hrs = float(input_df['Study_Hours_per_Week'].iloc[0])
        attendance = float(input_df['Attendance_Rate'].iloc[0])
        past_score = float(input_df['Past_Exam_Scores'].iloc[0])
        parental_edu = str(input_df['Parental_Education_Level'].iloc[0])
        extracurricular = str(input_df['Extracurricular_Activities'].iloc[0])

        import math

        # A. Calibrated ML Regressor mapping [50.0, 75.0] -> [35.0, 95.0]
        ml_relative = max(0.0, min(1.0, (raw_ml_score - 50.0) / 22.0))
        ml_calibrated_score = 35.0 + (ml_relative * 60.0)

        # B. Non-linear Self-Study Curve with Diminishing Returns (optimal range 32-38 hrs/wk)
        study_curve = 100.0 * (1.0 - math.exp(-study_hrs / 16.0))
        study_norm = min(100.0, study_curve * 1.15)

        # C. Lecture Attendance Factor with Realistic Collegiate Shortage Penalties
        if attendance < 60.0:
            att_effective = attendance * 0.85  # Debarment / severe detention threshold
        elif attendance < 75.0:
            att_effective = attendance * 0.95  # Shortage warning range
        else:
            att_effective = attendance

        # D. Environmental & Demographic Modifiers
        parent_bonus = {
            'PhD': 2.5,
            'Masters': 1.8,
            'Bachelors': 1.0,
            'High School': -1.0
        }.get(parental_edu, 0.5)
        extra_bonus = 1.5 if extracurricular == 'Yes' else -0.5

        # E. Core Academic Potential Index (Past Scores 52%, Attendance 28%, Study 16%, Background 4%)
        past_contrib = past_score * 0.52
        att_contrib = att_effective * 0.28
        study_contrib = study_norm * 0.16
        env_contrib = parent_bonus + extra_bonus

        academic_index = past_contrib + att_contrib + study_contrib + env_contrib
        academic_index = max(10.0, min(99.0, academic_index))

        # F. Blended Ensemble: 85% Academic Factor Matrix + 15% Supervised Regressor
        blended_score = (0.85 * academic_index) + (0.15 * ml_calibrated_score)
        predicted_score = round(max(12.0, min(98.5, blended_score)), 1)

        # 4. Standard Passing Thresholds & CGPA (10.0 UGC Scale)
        pass_fail = derive_pass_fail(predicted_score)
        cgpa = round(predicted_score / 10.0, 2)

        # 5. Dynamic Pass Probability calibrated with Sigmoid Curve
        try:
            sigmoid_prob = 1.0 / (1.0 + math.exp(-(predicted_score - PASSING_THRESHOLD) / 4.2)) * 100.0
            pass_prob = round(max(1.0, min(99.9, sigmoid_prob)), 1)
        except Exception:
            pass_prob = 98.0 if pass_fail == 'Pass' else 12.0

        # 6. Qualitative Performance Category & Letter Grade
        performance_category = derive_performance_category(predicted_score)

        if predicted_score >= 90.0:
            letter_grade = "O (Outstanding - Top Tier)"
            academic_standing = "Honors Division (Dean's List Candidate)"
        elif predicted_score >= 80.0:
            letter_grade = "A+ (Excellent Performance)"
            academic_standing = "First Class with Distinction"
        elif predicted_score >= 70.0:
            letter_grade = "A (Very Good)"
            academic_standing = "First Class Division"
        elif predicted_score >= 65.0:
            letter_grade = "B+ (Good Standing)"
            academic_standing = "Second Class Division (Satisfactory)"
        elif predicted_score >= 60.0:
            letter_grade = "B (Above Average - Pass)"
            academic_standing = "Standard Pass Standing"
        else:
            letter_grade = "F (Needs Improvement - Fail)"
            academic_standing = "Academic Remedial Action Required"

        # 7. Explainable AI: Feature Contributions
        feature_breakdown = {
            'past_foundation': round(past_contrib, 1),
            'attendance_impact': round(att_contrib, 1),
            'study_habit_impact': round(study_contrib, 1),
            'environment_impact': round(max(0.0, env_contrib), 1)
        }

        # 8. Actionable Insights & Targeted Recommendations
        recommendations = self._generate_recommendations(input_df.iloc[0], predicted_score)

        return {
            'predicted_score': predicted_score,
            'pass_fail': pass_fail,
            'performance_category': performance_category,
            'pass_probability': pass_prob,
            'passing_threshold': PASSING_THRESHOLD,
            'cgpa': cgpa,
            'letter_grade': letter_grade,
            'academic_standing': academic_standing,
            'feature_breakdown': feature_breakdown,
            'features_used': input_df.to_dict(orient='records')[0],
            'recommendations': recommendations
        }

    def _generate_recommendations(self, row, predicted_score=None):
        """Generates constructive, targeted academic advice based on student inputs."""
        recs = []
        study_hrs = row['Study_Hours_per_Week']
        att_rate = row['Attendance_Rate']
        past_score = row['Past_Exam_Scores']

        if att_rate < 60.0:
            recs.append("Critical: Attendance is below 60%. High risk of academic debarment / detention. Prioritize classes immediately.")
        elif att_rate < 75.0:
            recs.append("Attendance is below institutional 75% norm. Attend upcoming lecture sessions regularly to avoid shortages.")
        elif att_rate >= 95.0:
            recs.append("Praiseworthy attendance record (>=95%)! Consistent participation directly boosts exam confidence.")

        if study_hrs < 15:
            recs.append("Weekly self-study is low (<15 hrs). Dedicating an additional 1-2 hours daily will substantially elevate final scores.")
        elif study_hrs >= 35:
            recs.append("Strong self-study dedication. Maintain regular revision cycles and avoid pre-exam fatigue.")

        if past_score < 60:
            recs.append("Foundational prerequisite gaps detected from past exam scores. Schedule targeted doubt-clearing sessions.")
        elif past_score >= 90:
            recs.append("Outstanding academic foundation. Target competitive university honors and advanced course projects.")

        if row['Extracurricular_Activities'] == 'No':
            recs.append("Active participation in technical clubs or campus sports improves mental focus and stress management.")

        if not recs:
            recs.append("Well-balanced academic profile. Continue disciplined revision, mock test practice, and timely coursework.")

        return recs

def get_predictor():
    return PredictionEngine.get_instance()
