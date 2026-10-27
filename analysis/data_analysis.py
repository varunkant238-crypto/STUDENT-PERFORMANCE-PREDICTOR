"""
Student Performance Predictor - Dataset Analysis Module
Loads and performs comprehensive exploratory data analysis on the Amr Maree Kaggle dataset.
Generates statistical metrics and visualizations.
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_selection import mutual_info_regression

def get_dataset_path():
    """Locate dataset file in current workspace."""
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
    raise FileNotFoundError("Could not locate student_performance_dataset.csv.")

def analyze_dataset():
    dataset_path = get_dataset_path()
    print(f"[INFO] Loading dataset from: {dataset_path}")
    df = pd.read_csv(dataset_path)

    # Basic shape & columns
    n_rows, n_cols = df.shape
    columns = df.columns.tolist()
    missing_vals = df.isnull().sum().to_dict()
    duplicates = int(df.duplicated().sum())

    print(f"[INFO] Dataset Shape: {n_rows} rows x {n_cols} columns")
    print(f"[INFO] Missing values: {missing_vals}")
    print(f"[INFO] Duplicate rows: {duplicates}")

    # Numerical & categorical splits
    num_cols = ['Study_Hours_per_Week', 'Attendance_Rate', 'Past_Exam_Scores', 'Final_Exam_Score']
    cat_cols = ['Gender', 'Parental_Education_Level', 'Internet_Access_at_Home', 'Extracurricular_Activities', 'Pass_Fail']

    num_stats = df[num_cols].describe().to_dict()
    corr_matrix = df[num_cols].corr()

    # Pass / Fail analysis
    pass_fail_counts = df['Pass_Fail'].value_counts().to_dict()
    pass_fail_score_stats = df.groupby('Pass_Fail')['Final_Exam_Score'].agg(['min', 'max', 'mean', 'std']).to_dict(orient='index')

    # Mutual information
    features_for_mi = ['Study_Hours_per_Week', 'Attendance_Rate', 'Past_Exam_Scores', 
                       'Gender', 'Parental_Education_Level', 'Internet_Access_at_Home', 'Extracurricular_Activities']
    df_mi = df.copy()
    for col in ['Gender', 'Parental_Education_Level', 'Internet_Access_at_Home', 'Extracurricular_Activities']:
        df_mi[col] = df_mi[col].astype('category').cat.codes

    mi_values = mutual_info_regression(df_mi[features_for_mi], df['Final_Exam_Score'], random_state=42)
    mi_dict = dict(zip(features_for_mi, [round(float(v), 4) for v in mi_values]))
    mi_sorted = sorted(mi_dict.items(), key=lambda x: x[1], reverse=True)

    # Visualizations
    out_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static', 'images')
    os.makedirs(out_dir, exist_ok=True)

    # 1. Target distribution
    plt.figure(figsize=(8, 4.5))
    sns.histplot(df['Final_Exam_Score'], kde=True, bins=15, color='#4361ee')
    plt.axvline(60, color='#e63946', linestyle='--', linewidth=2, label='Pass Threshold (60 Marks)')
    plt.title('Distribution of Final Exam Scores', fontsize=14, fontweight='bold', pad=12)
    plt.xlabel('Final Exam Score (Marks out of 100)', fontsize=11)
    plt.ylabel('Student Count', fontsize=11)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'score_distribution.png'), dpi=150)
    plt.close()

    # 2. Correlation heatmap
    plt.figure(figsize=(7, 5))
    sns.heatmap(corr_matrix, annot=True, cmap='Blues', fmt='.3f', cbar=True, square=True)
    plt.title('Correlation Heatmap (Numerical Variables)', fontsize=14, fontweight='bold', pad=12)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'correlation_heatmap.png'), dpi=150)
    plt.close()

    # 3. Attendance vs Final Exam Score scatter
    plt.figure(figsize=(8, 4.5))
    sns.scatterplot(data=df, x='Attendance_Rate', y='Final_Exam_Score', hue='Pass_Fail', 
                    palette={'Pass': '#2ec4b6', 'Fail': '#e71d36'}, alpha=0.8)
    plt.title('Attendance Rate vs Final Exam Score', fontsize=14, fontweight='bold', pad=12)
    plt.xlabel('Attendance Rate (%)', fontsize=11)
    plt.ylabel('Final Exam Score', fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'attendance_vs_score.png'), dpi=150)
    plt.close()

    # 4. Study Hours vs Final Exam Score
    plt.figure(figsize=(8, 4.5))
    sns.boxplot(data=df, x='Parental_Education_Level', y='Final_Exam_Score', palette='Set2')
    plt.title('Final Exam Score by Parental Education Level', fontsize=14, fontweight='bold', pad=12)
    plt.xlabel('Parental Education Level', fontsize=11)
    plt.ylabel('Final Exam Score', fontsize=11)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'parental_edu_vs_score.png'), dpi=150)
    plt.close()

    print("[SUCCESS] Dataset analysis complete and figures generated successfully.")
    return {
        'n_rows': n_rows,
        'n_cols': n_cols,
        'columns': columns,
        'missing_values': missing_vals,
        'duplicates': duplicates,
        'numerical_stats': num_stats,
        'correlations': corr_matrix.to_dict(),
        'pass_fail_counts': pass_fail_counts,
        'pass_fail_score_stats': pass_fail_score_stats,
        'mutual_info': mi_sorted
    }

if __name__ == '__main__':
    analyze_dataset()
