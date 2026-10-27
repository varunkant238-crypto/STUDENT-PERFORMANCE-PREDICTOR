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

        # 3. Regression Prediction (Final Exam Marks)
        raw_score = float(self.regressor.predict(transformed_features)[0])
        # Bound score to realistic exam range
        predicted_score = round(max(0.0, min(100.0, raw_score)), 1)

        # 4. Pass / Fail status
        pass_fail = derive_pass_fail(predicted_score)

        # 5. Classification Probability if classifier available
        pass_prob = None
        if self.classifier is not None and hasattr(self.classifier, 'predict_proba'):
            try:
                probs = self.classifier.predict_proba(transformed_features)[0]
                # Index 1 is Pass (1)
                pass_prob = round(float(probs[1]) * 100, 1)
            except Exception:
                pass_prob = round(min(99.0, max(1.0, (predicted_score / 100.0) * 100)), 1)
        else:
            pass_prob = 85.0 if pass_fail == 'Pass' else 35.0

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
