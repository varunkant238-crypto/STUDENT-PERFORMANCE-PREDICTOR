"""
Preprocessing & Input Validation Tests.
"""

import pytest
from preprocessing.preprocessing import (
    validate_and_format_input, derive_pass_fail, derive_performance_category,
    ALL_SELECTED_FEATURES
)

def test_derive_pass_fail():
    assert derive_pass_fail(60.0) == "Pass"
    assert derive_pass_fail(75.5) == "Pass"
    assert derive_pass_fail(59.9) == "Fail"
    assert derive_pass_fail(45.0) == "Fail"

def test_derive_performance_category():
    assert "Grade A" in derive_performance_category(72.0)
    assert "Grade B" in derive_performance_category(67.0)
    assert "Grade C" in derive_performance_category(62.0)
    assert "Grade F" in derive_performance_category(55.0)

def test_valid_input_formatting():
    raw = {
        'Study_Hours_per_Week': '25',
        'Attendance_Rate': '85.5',
        'Past_Exam_Scores': '78',
        'Parental_Education_Level': 'Bachelors',
        'Extracurricular_Activities': 'Yes'
    }
    df, err = validate_and_format_input(raw)
    assert err is None
    assert df is not None
    assert list(df.columns) == ALL_SELECTED_FEATURES
    assert df['Study_Hours_per_Week'].iloc[0] == 25
    assert df['Attendance_Rate'].iloc[0] == 85.5

def test_invalid_input_range_rejected():
    raw_invalid = {
        'Study_Hours_per_Week': '150',  # Exceeds max
        'Attendance_Rate': '85.5',
        'Past_Exam_Scores': '78',
        'Parental_Education_Level': 'Bachelors',
        'Extracurricular_Activities': 'Yes'
    }
    df, err = validate_and_format_input(raw_invalid)
    assert df is None
    assert "Study Hours" in err

def test_low_values_accepted():
    # Verify low attendance and low marks (e.g. 15% and 20 marks) are accepted without error
    raw_low = {
        'Study_Hours_per_Week': '2',
        'Attendance_Rate': '15.0',
        'Past_Exam_Scores': '20',
        'Parental_Education_Level': 'High School',
        'Extracurricular_Activities': 'No'
    }
    df, err = validate_and_format_input(raw_low)
    assert err is None
    assert df is not None
    assert df['Attendance_Rate'].iloc[0] == 15.0
    assert df['Past_Exam_Scores'].iloc[0] == 20
