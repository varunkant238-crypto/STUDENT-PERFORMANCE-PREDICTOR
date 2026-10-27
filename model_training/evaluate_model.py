"""
Model Evaluation Module for Student Performance Predictor.
Loads trained models, validates performance metrics against the holdout test set,
and renders visual evaluation charts.
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, classification_report, confusion_matrix
)

from preprocessing.preprocessing import (
    load_and_clean_data, ALL_SELECTED_FEATURES, PASSING_THRESHOLD
)

SAVED_MODELS_DIR = os.path.join(os.path.dirname(__file__), 'saved_models')
STATIC_IMG_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static', 'images')

def evaluate_saved_models():
    print("=" * 60)
    print("  STUDENT PERFORMANCE PREDICTOR - EVALUATION PIPELINE")
    print("=" * 60)

    reg_path = os.path.join(SAVED_MODELS_DIR, 'rf_regressor.joblib')
    clf_path = os.path.join(SAVED_MODELS_DIR, 'rf_classifier.joblib')
    prep_path = os.path.join(SAVED_MODELS_DIR, 'preprocessor.joblib')

    if not (os.path.exists(reg_path) and os.path.exists(prep_path)):
        raise FileNotFoundError("Trained models not found! Run train_model.py first.")

    regressor = joblib.load(reg_path)
    classifier = joblib.load(clf_path) if os.path.exists(clf_path) else None
    preprocessor = joblib.load(prep_path)

    # Load holdout test data
    X, y_reg, y_clf, _ = load_and_clean_data(deduplicate=True)
    _, X_test, _, y_reg_test, _, y_clf_test = train_test_split(
        X, y_reg, y_clf, test_size=0.20, random_state=42, stratify=y_clf
    )

    X_test_trans = preprocessor.transform(X_test)
    reg_preds = regressor.predict(X_test_trans)

    mae = mean_absolute_error(y_reg_test, reg_preds)
    rmse = np.sqrt(mean_squared_error(y_reg_test, reg_preds))
    r2 = r2_score(y_reg_test, reg_preds)

    print(f"\n[REGRESSION EVALUATION]")
    print(f"  Holdout Samples: {len(X_test)}")
    print(f"  Mean Absolute Error (MAE): {mae:.3f} marks")
    print(f"  Root Mean Squared Error (RMSE): {rmse:.3f} marks")
    print(f"  Coefficient of Determination (R²): {r2:.3f}")

    os.makedirs(STATIC_IMG_DIR, exist_ok=True)

    # 1. Actual vs Predicted Plot
    plt.figure(figsize=(7, 5))
    plt.scatter(y_reg_test, reg_preds, color='#3a86ff', alpha=0.7, edgecolors='k')
    min_val = min(y_reg_test.min(), reg_preds.min()) - 2
    max_val = max(y_reg_test.max(), reg_preds.max()) + 2
    plt.plot([min_val, max_val], [min_val, max_val], color='#e63946', linestyle='--', linewidth=2, label='Ideal 1:1 Fit')
    plt.xlabel('Actual Final Exam Score', fontsize=11)
    plt.ylabel('Predicted Final Exam Score', fontsize=11)
    plt.title(f'Actual vs Predicted Final Scores (R² = {r2:.2f})', fontsize=13, fontweight='bold', pad=12)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(STATIC_IMG_DIR, 'actual_vs_predicted.png'), dpi=150)
    plt.close()

    # 2. Confusion Matrix Plot
    if classifier:
        clf_preds = classifier.predict(X_test_trans)
        acc = accuracy_score(y_clf_test, clf_preds)
        cm = confusion_matrix(y_clf_test, clf_preds)

        print(f"\n[CLASSIFICATION EVALUATION]")
        print(f"  Accuracy: {acc:.2%}")
        print("\nClassification Report:\n", classification_report(y_clf_test, clf_preds, target_names=['Fail', 'Pass']))

        plt.figure(figsize=(6, 4.5))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=['Predicted Fail', 'Predicted Pass'],
                    yticklabels=['Actual Fail', 'Actual Pass'])
        plt.title(f'Confusion Matrix (Accuracy = {acc:.1%})', fontsize=13, fontweight='bold', pad=12)
        plt.tight_layout()
        plt.savefig(os.path.join(STATIC_IMG_DIR, 'confusion_matrix.png'), dpi=150)
        plt.close()

    print(f"[SUCCESS] Evaluation figures successfully saved in {STATIC_IMG_DIR}")
    return {
        'mae': mae,
        'rmse': rmse,
        'r2': r2,
        'accuracy': acc if classifier else None
    }

if __name__ == '__main__':
    evaluate_saved_models()
