"""
Centralized Preprocessing and Feature Definitions Module.
All modules (training, evaluation, backend inference, and UI validation)
reference this module for feature definitions and transformations.
"""

import os
import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

# 5 SELECTED FEATURES ONLY
SELECTED_NUMERICAL_FEATURES = [
    'Study_Hours_per_Week',
    'Attendance_Rate',
    'Past_Exam_Scores'
]

SELECTED_CATEGORICAL_FEATURES = [
    'Parental_Education_Level',
    'Extracurricular_Activities'
]

ALL_SELECTED_FEATURES = SELECTED_NUMERICAL_FEATURES + SELECTED_CATEGORICAL_FEATURES

# TARGET DEFINITIONS
TARGET_REGRESSION = 'Final_Exam_Score'
TARGET_CLASSIFICATION = 'Pass_Fail'

# VALIDATION CONSTRAINTS (Expanded to full natural range 0-100)
FEATURE_CONSTRAINTS = {
    'Study_Hours_per_Week': {'min': 0, 'max': 100, 'default': 25, 'label': 'Study Hours per Week (hrs)'},
    'Attendance_Rate': {'min': 0.0, 'max': 100.0, 'default': 80.0, 'label': 'Attendance Rate (%)'},
    'Past_Exam_Scores': {'min': 0, 'max': 100, 'default': 75, 'label': 'Past Exam Scores (Marks)'},
    'Parental_Education_Level': {
        'allowed': ['High School', 'Bachelors', 'Masters', 'PhD'],
        'default': 'Bachelors',
        'label': 'Parental Education Level'
    },
    'Extracurricular_Activities': {
        'allowed': ['Yes', 'No'],
        'default': 'No',
        'label': 'Extracurricular Participation'
    }
}

# PASSING THRESHOLD IN DATASET
PASSING_THRESHOLD = 60.0

def derive_pass_fail(score: float) -> str:
    """Derive binary Pass/Fail based on dataset passing threshold."""
    return "Pass" if score >= PASSING_THRESHOLD else "Fail"

def derive_performance_category(score: float) -> str:
    """Categorize numerical performance score into intuitive academic bands."""
    if score >= 70.0:
        return "Excellent (Grade A)"
    elif score >= 65.0:
        return "Good (Grade B)"
    elif score >= 60.0:
        return "Average (Grade C - Pass)"
    else:
        return "Needs Improvement (Grade F - Fail)"

def get_default_dataset_path() -> str:
    candidates = [
        os.path.join(os.path.dirname(__file__), '..', 'dataset', 'student_performance_dataset.csv'),
        os.path.join(os.path.dirname(__file__), '..', 'student_performance_dataset.csv'),
        'student_performance_dataset.csv',
        os.path.join('dataset', 'student_performance_dataset.csv')
    ]
    for path in candidates:
        norm = os.path.normpath(path)
        if os.path.exists(norm):
            return norm
    raise FileNotFoundError("Could not find student_performance_dataset.csv in workspace.")

def load_and_clean_data(filepath=None, deduplicate=True):
    """Load dataset, handle missing values, and return clean features & targets."""
    if filepath is None:
        filepath = get_default_dataset_path()
    df = pd.read_csv(filepath)

    if deduplicate:
        # Deduplicate to prevent train-test data leakage
        df = df.drop_duplicates()

    # Verify presence of selected features and targets
    for col in ALL_SELECTED_FEATURES + [TARGET_REGRESSION, TARGET_CLASSIFICATION]:
        if col not in df.columns:
            raise ValueError(f"Missing required dataset column: {col}")

    X = df[ALL_SELECTED_FEATURES].copy()
    y_reg = df[TARGET_REGRESSION].astype(float).copy()
    y_clf = (df[TARGET_CLASSIFICATION] == 'Pass').astype(int).copy()

    return X, y_reg, y_clf, df

def build_preprocessor():
    """
    Construct scikit-learn ColumnTransformer for 5 selected features.
    StandardScaler for numerical features, OneHotEncoder for categorical features.
    """
    num_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    cat_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', num_pipeline, SELECTED_NUMERICAL_FEATURES),
            ('cat', cat_pipeline, SELECTED_CATEGORICAL_FEATURES)
        ],
        remainder='drop'
    )
    return preprocessor

def validate_and_format_input(raw_dict):
    """
    Validate and convert raw web form input into DataFrame matching training schema.
    Returns (cleaned_df, error_message).
    """
    clean_data = {}

    # 1. Study Hours
    try:
        sh = float(raw_dict.get('Study_Hours_per_Week', ''))
        c = FEATURE_CONSTRAINTS['Study_Hours_per_Week']
        if not (c['min'] <= sh <= c['max']):
            return None, f"Study Hours must be between {c['min']} and {c['max']} hours/week."
        clean_data['Study_Hours_per_Week'] = [int(round(sh))]
    except (ValueError, TypeError):
        return None, "Please provide a valid numerical value for Study Hours per Week."

    # 2. Attendance Rate
    try:
        att = float(raw_dict.get('Attendance_Rate', ''))
        c = FEATURE_CONSTRAINTS['Attendance_Rate']
        if not (c['min'] <= att <= c['max']):
            return None, f"Attendance Rate must be between {c['min']}% and {c['max']}%."
        clean_data['Attendance_Rate'] = [round(att, 2)]
    except (ValueError, TypeError):
        return None, "Please provide a valid numerical value for Attendance Rate (e.g., 85.5)."

    # 3. Past Exam Scores
    try:
        pe = float(raw_dict.get('Past_Exam_Scores', ''))
        c = FEATURE_CONSTRAINTS['Past_Exam_Scores']
        if not (c['min'] <= pe <= c['max']):
            return None, f"Past Exam Scores must be between {c['min']} and {c['max']} marks."
        clean_data['Past_Exam_Scores'] = [int(round(pe))]
    except (ValueError, TypeError):
        return None, "Please provide a valid numerical value for Past Exam Scores (e.g., 75)."

    # 4. Parental Education Level
    pel = str(raw_dict.get('Parental_Education_Level', '')).strip()
    c = FEATURE_CONSTRAINTS['Parental_Education_Level']
    if pel not in c['allowed']:
        return None, f"Parental Education Level must be one of: {', '.join(c['allowed'])}."
    clean_data['Parental_Education_Level'] = [pel]

    # 5. Extracurricular Activities
    act = str(raw_dict.get('Extracurricular_Activities', '')).strip().capitalize()
    c = FEATURE_CONSTRAINTS['Extracurricular_Activities']
    if act not in c['allowed']:
        return None, "Extracurricular Activities must be either 'Yes' or 'No'."
    clean_data['Extracurricular_Activities'] = [act]

    df = pd.DataFrame(clean_data)[ALL_SELECTED_FEATURES]
    return df, None
