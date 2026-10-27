"""
Dataset Validation Tests.
Ensures the official Kaggle dataset matches all project criteria.
"""

import os
import pandas as pd
import pytest
from preprocessing.preprocessing import (
    get_default_dataset_path, ALL_SELECTED_FEATURES,
    TARGET_REGRESSION, TARGET_CLASSIFICATION, PASSING_THRESHOLD
)

def test_dataset_exists():
    path = get_default_dataset_path()
    assert os.path.exists(path), f"Dataset file does not exist at {path}"

def test_dataset_structure():
    path = get_default_dataset_path()
    df = pd.read_csv(path)
    # Validate rows and columns
    assert len(df) >= 500, f"Expected at least 500 records, got {len(df)}"
    for feat in ALL_SELECTED_FEATURES:
        assert feat in df.columns, f"Missing selected feature {feat} in dataset"
    assert TARGET_REGRESSION in df.columns, f"Missing regression target {TARGET_REGRESSION}"
    assert TARGET_CLASSIFICATION in df.columns, f"Missing classification target {TARGET_CLASSIFICATION}"

def test_no_missing_values():
    path = get_default_dataset_path()
    df = pd.read_csv(path)
    assert df[ALL_SELECTED_FEATURES].isnull().sum().sum() == 0, "Selected features have missing values"

def test_passing_threshold_alignment():
    path = get_default_dataset_path()
    df = pd.read_csv(path)
    pass_scores = df[df[TARGET_CLASSIFICATION] == 'Pass'][TARGET_REGRESSION]
    fail_scores = df[df[TARGET_CLASSIFICATION] == 'Fail'][TARGET_REGRESSION]
    assert pass_scores.min() >= PASSING_THRESHOLD, "Pass record with score below cutoff found"
    assert fail_scores.max() < PASSING_THRESHOLD, "Fail record with score above cutoff found"
