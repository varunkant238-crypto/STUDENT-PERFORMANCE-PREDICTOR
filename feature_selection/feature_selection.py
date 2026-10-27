"""
Feature Selection Module for Student Performance Predictor.
Analyzes features and formally defines the selected 5 input features.
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_selection import mutual_info_regression, f_regression

# Centralized definitions of selected features
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
TARGET_REGRESSION = 'Final_Exam_Score'
TARGET_CLASSIFICATION = 'Pass_Fail'

def get_dataset_path():
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
    raise FileNotFoundError("Could not find student_performance_dataset.csv")

def run_feature_selection():
    dataset_path = get_dataset_path()
    df = pd.read_csv(dataset_path)

    print("[INFO] Running formal feature selection analysis...")
    print(f"[INFO] Total features considered: {len(df.columns) - 3}")

    # Encode categorical columns for mathematical analysis
    encoded_df = df.copy()
    for col in ['Gender', 'Parental_Education_Level', 'Internet_Access_at_Home', 'Extracurricular_Activities']:
        encoded_df[col] = encoded_df[col].astype('category').cat.codes

    candidate_features = [
        'Study_Hours_per_Week', 'Attendance_Rate', 'Past_Exam_Scores',
        'Gender', 'Parental_Education_Level', 'Internet_Access_at_Home', 'Extracurricular_Activities'
    ]

    X = encoded_df[candidate_features]
    y = encoded_df[TARGET_REGRESSION]

    # Mutual Information
    mi = mutual_info_regression(X, y, random_state=42)
    mi_series = pd.Series(mi, index=candidate_features).sort_values(ascending=False)

    # F-Regression
    f_vals, _ = f_regression(X, y)
    f_series = pd.Series(f_vals, index=candidate_features).sort_values(ascending=False)

    print("\n[INFO] Mutual Information Ranking:")
    print(mi_series)

    print("\n[INFO] F-Statistic Ranking:")
    print(f_series)

    # Plot Mutual Information
    out_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static', 'images')
    os.makedirs(out_dir, exist_ok=True)

    plt.figure(figsize=(9, 4.5))
    colors = ['#1d3557' if f in ALL_SELECTED_FEATURES else '#a8dadc' for f in mi_series.index]
    ax = mi_series.plot(kind='barh', color=colors)
    plt.title('Mutual Information with Final Exam Score\n(Dark Blue = 5 Selected Features)', fontsize=13, fontweight='bold', pad=12)
    plt.xlabel('Mutual Information Score', fontsize=11)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'feature_importance.png'), dpi=150)
    plt.close()

    print(f"[SUCCESS] Feature selection chart saved to: {os.path.join(out_dir, 'feature_importance.png')}")
    print(f"[SUCCESS] Selected 5 Features: {ALL_SELECTED_FEATURES}")

    return {
        'selected_features': ALL_SELECTED_FEATURES,
        'mutual_info': mi_series.to_dict(),
        'f_stats': f_series.to_dict()
    }

if __name__ == '__main__':
    run_feature_selection()
