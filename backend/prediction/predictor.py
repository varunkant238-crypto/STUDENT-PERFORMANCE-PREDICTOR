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

        # 3. Intelligent Multi-Factor Regression Prediction (Final Exam Marks)
        raw_ml_score = float(self.regressor.predict(transformed_features)[0])

        # Extract features for realistic academic scaling
        study_hrs = float(input_df['Study_Hours_per_Week'].iloc[0])
        attendance = float(input_df['Attendance_Rate'].iloc[0])
        past_score = float(input_df['Past_Exam_Scores'].iloc[0])
        parental_edu = str(input_df['Parental_Education_Level'].iloc[0])
        extracurricular = str(input_df['Extracurricular_Activities'].iloc[0])

        # Academic background modifiers
        parent_bonus = {
            'PhD': 3.0,
            'Masters': 2.0,
            'Bachelors': 1.0,
            'High School': -1.0
        }.get(parental_edu, 0.0)

        extra_bonus = 1.5 if extracurricular == 'Yes' else -0.5

        # Normalization of study hours (32 hrs/week standard benchmark for full academic credit)
        study_norm = min(100.0, (study_hrs / 32.0) * 100.0)

        # Empirical Academic Potential Index (0 - 100)
        # Weights: Past Scores (50%), Attendance (28%), Study Hours (18%), Background Modifiers (4%)
        academic_index = (
            (past_score * 0.50) +
            (attendance * 0.28) +
            (study_norm * 0.18) +
            parent_bonus +
            extra_bonus
        )
        academic_index = max(10.0, min(99.0, academic_index))

        # Calibrate ML raw score from dataset range [50.0, 75.0] into [35.0, 95.0]
        ml_relative = max(0.0, min(1.0, (raw_ml_score - 50.0) / 22.0))
        ml_calibrated_score = 35.0 + (ml_relative * 60.0)

        # Blended Ensemble: 80% Comprehensive Academic Factors + 20% ML Regressor
        blended_score = (0.80 * academic_index) + (0.20 * ml_calibrated_score)
        predicted_score = round(max(15.0, min(99.0, blended_score)), 1)

        # 4. Pass / Fail status (Passing threshold is 60.0 marks)
        pass_fail = derive_pass_fail(predicted_score)

        # 5. Dynamic Pass Probability calibrated against threshold (60 marks)
        import math
        try:
            sigmoid_prob = 1.0 / (1.0 + math.exp(-(predicted_score - PASSING_THRESHOLD) / 4.5)) * 100.0
            pass_prob = round(max(1.0, min(99.0, sigmoid_prob)), 1)
        except Exception:
            pass_prob = 95.0 if pass_fail == 'Pass' else 15.0

        # 6. Qualitative Performance Category
        performance_category = derive_performance_category(predicted_score)

        # 7. Actionable Recommendations based on inputs
        recommendations = self._generate_recommendations(input_df.iloc[0])

        return {
            'predicted_score': predicted_score,
            'pass_fail': pass_fail,
            'performance_category': performance_category,
            'pass_probability': pass_prob,
            'passing_threshold': PASSING_THRESHOLD,
            'features_used': input_df.to_dict(orient='records')[0],
            'recommendations': recommendations
        }

    def _generate_recommendations(self, row):
        """Generates constructive academic advice based on student inputs."""
        recs = []
        study_hrs = row['Study_Hours_per_Week']
        att_rate = row['Attendance_Rate']
        past_score = row['Past_Exam_Scores']

        if att_rate < 75.0:
            recs.append("Class Attendance is currently below 75%. Prioritize regular lecture participation to boost comprehension.")
        elif att_rate >= 90.0:
            recs.append("Excellent attendance rate! Maintain this level of engagement in lectures.")

        if study_hrs < 20:
            recs.append("Weekly self-study is below 20 hours. Adding 3-5 hours of dedicated study per week could elevate your final grade.")
        elif study_hrs >= 30:
            recs.append("High study commitment detected. Ensure regular revision intervals and balanced rest.")

        if past_score < 60:
            recs.append("Past exam scores indicate foundational gaps. Schedule review sessions on core prerequisite topics.")

        if row['Extracurricular_Activities'] == 'No':
            recs.append("Consider light extracurricular participation to enhance stress relief and time management.")

        if not recs:
            recs.append("Great overall balance! Continue consistent practice, mock tests, and timely assignment submission.")

        return recs

def get_predictor():
    return PredictionEngine.get_instance()
