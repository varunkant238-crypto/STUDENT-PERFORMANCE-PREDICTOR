"""
Model Training Module for Student Performance Predictor.
Trains supervised ML models on the 5 selected features, evaluates performance,
and persists trained artifacts and evaluation metadata.
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, RandomForestClassifier
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
)

from preprocessing.preprocessing import (
    load_and_clean_data, build_preprocessor, ALL_SELECTED_FEATURES,
    SELECTED_NUMERICAL_FEATURES, SELECTED_CATEGORICAL_FEATURES,
    PASSING_THRESHOLD
)

SAVED_MODELS_DIR = os.path.join(os.path.dirname(__file__), 'saved_models')

def train_and_save_models():
    os.makedirs(SAVED_MODELS_DIR, exist_ok=True)
    print("=" * 60)
    print("  STUDENT PERFORMANCE PREDICTOR - MODEL TRAINING PIPELINE")
    print("=" * 60)

    # 1. Load data
    X, y_reg, y_clf, raw_df = load_and_clean_data(deduplicate=True)
    print(f"[INFO] Training dataset size: {len(X)} rows")
    print(f"[INFO] Selected Features (5): {ALL_SELECTED_FEATURES}")

    # 2. Train-test split (80-20, fixed seed for reproducibility)
    X_train, X_test, y_reg_train, y_reg_test, y_clf_train, y_clf_test = train_test_split(
        X, y_reg, y_clf, test_size=0.20, random_state=42, stratify=y_clf
    )
    print(f"[INFO] Train samples: {len(X_train)}, Test samples: {len(X_test)}")

    # 3. Fit Preprocessing Pipeline strictly on training data
    preprocessor = build_preprocessor()
    X_train_transformed = preprocessor.fit_transform(X_train)
    X_test_transformed = preprocessor.transform(X_test)

    # 4. Train Regression Models
    print("\n--- Evaluating Regression Models ---")
    reg_candidates = {
        'Linear Regression': LinearRegression(),
        'Ridge Regression': Ridge(alpha=1.0),
        'Random Forest Regressor': RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42),
        'Gradient Boosting Regressor': GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42)
    }

    reg_results = {}
    best_reg_name = None
    best_reg_mae = float('inf')
    best_reg_model = None

    for name, model in reg_candidates.items():
        model.fit(X_train_transformed, y_reg_train)
        preds = model.predict(X_test_transformed)
        mae = float(mean_absolute_error(y_reg_test, preds))
        rmse = float(np.sqrt(mean_squared_error(y_reg_test, preds)))
        r2 = float(r2_score(y_reg_test, preds))

        reg_results[name] = {'mae': round(mae, 3), 'rmse': round(rmse, 3), 'r2': round(r2, 3)}
        print(f"  {name:28s} | MAE: {mae:.3f} | RMSE: {rmse:.3f} | R²: {r2:.3f}")

        if mae < best_reg_mae:
            best_reg_mae = mae
            best_reg_name = name
            best_reg_model = model

    print(f"[SELECTED REGRESSOR] -> {best_reg_name} (MAE: {best_reg_mae:.3f})")

    # 5. Train Classification Models
    print("\n--- Evaluating Classification Models ---")
    clf_candidates = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Random Forest Classifier': RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    }

    clf_results = {}
    best_clf_name = None
    best_clf_acc = -1.0
    best_clf_model = None

    for name, model in clf_candidates.items():
        model.fit(X_train_transformed, y_clf_train)
        preds = model.predict(X_test_transformed)
        acc = float(accuracy_score(y_clf_test, preds))
        prec = float(precision_score(y_clf_test, preds, zero_division=0))
        rec = float(recall_score(y_clf_test, preds, zero_division=0))
        f1 = float(f1_score(y_clf_test, preds, zero_division=0))

        clf_results[name] = {
            'accuracy': round(acc, 4),
            'precision': round(prec, 4),
            'recall': round(rec, 4),
            'f1_score': round(f1, 4)
        }
        print(f"  {name:28s} | Accuracy: {acc:.2%} | F1: {f1:.3f} | Precision: {prec:.3f} | Recall: {rec:.3f}")

        if acc > best_clf_acc:
            best_clf_acc = acc
            best_clf_name = name
            best_clf_model = model

    print(f"[SELECTED CLASSIFIER] -> {best_clf_name} (Accuracy: {best_clf_acc:.2%})")

    # 6. Confusion Matrix for Selected Classifier
    final_clf_preds = best_clf_model.predict(X_test_transformed)
    cm = confusion_matrix(y_clf_test, final_clf_preds).tolist()

    # 7. Persist Models
    reg_path = os.path.join(SAVED_MODELS_DIR, 'rf_regressor.joblib')
    clf_path = os.path.join(SAVED_MODELS_DIR, 'rf_classifier.joblib')
    prep_path = os.path.join(SAVED_MODELS_DIR, 'preprocessor.joblib')

    joblib.dump(best_reg_model, reg_path)
    joblib.dump(best_clf_model, clf_path)
    joblib.dump(preprocessor, prep_path)
    print(f"[INFO] Persisted models to: {SAVED_MODELS_DIR}")

    # 8. Feature importances if available
    feature_importances = {}
    if hasattr(best_reg_model, 'feature_importances_'):
        # Get one-hot feature names
        try:
            ohe = preprocessor.named_transformers_['cat'].named_steps['encoder']
            cat_feat_names = list(ohe.get_feature_names_out(SELECTED_CATEGORICAL_FEATURES))
        except Exception:
            cat_feat_names = SELECTED_CATEGORICAL_FEATURES
        all_trans_names = SELECTED_NUMERICAL_FEATURES + cat_feat_names
        for fname, imp in zip(all_trans_names, best_reg_model.feature_importances_):
            feature_importances[fname] = round(float(imp), 4)

    # 9. Save comprehensive metadata
    metadata = {
        'training_timestamp': datetime.now().isoformat(),
        'dataset_total_samples': len(raw_df),
        'deduplicated_samples': len(X),
        'train_samples': len(X_train),
        'test_samples': len(X_test),
        'selected_features': ALL_SELECTED_FEATURES,
        'numerical_features': SELECTED_NUMERICAL_FEATURES,
        'categorical_features': SELECTED_CATEGORICAL_FEATURES,
        'pass_threshold': PASSING_THRESHOLD,
        'selected_regressor': {
            'model_name': best_reg_name,
            'metrics': reg_results[best_reg_name]
        },
        'all_regressors': reg_results,
        'selected_classifier': {
            'model_name': best_clf_name,
            'metrics': clf_results[best_clf_name],
            'confusion_matrix': cm
        },
        'all_classifiers': clf_results,
        'feature_importances': feature_importances
    }

    meta_path = os.path.join(SAVED_MODELS_DIR, 'model_metadata.json')
    with open(meta_path, 'w') as f:
        json.dump(metadata, f, indent=4)
    print(f"[INFO] Saved training metadata to: {meta_path}")
    print("=" * 60)
    print("  MODEL TRAINING PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)
    return metadata

if __name__ == '__main__':
    train_and_save_models()
