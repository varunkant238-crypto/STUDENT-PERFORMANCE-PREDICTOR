# Dataset Documentation

## Dataset Source
- **Origin**: Kaggle Dataset
- **URL**: [https://www.kaggle.com/datasets/amrmaree/student-performance-prediction](https://www.kaggle.com/datasets/amrmaree/student-performance-prediction)
- **Author**: Amr Maree
- **Local File Path**: `dataset/student_performance_dataset.csv`

## Dataset Description
The dataset contains 708 academic performance records capturing students' academic history, attendance, weekly study hours, parental education levels, and extracurricular activity participation.

## Dataset Structure
- **Number of Rows**: 708
- **Number of Columns**: 10
- **Missing Values**: 0 (Complete dataset)
- **Duplicate Rows**: 0

## Columns & Data Types
1. `Student_ID` (String): Unique identifier assigned to each student (e.g., S147, S136).
2. `Gender` (String): Binary categorical attribute (`Female`: 375, `Male`: 333).
3. `Study_Hours_per_Week` (Integer): Continuous weekly study duration ranging from 10 to 39 hours (Mean: 26.13, Std: 8.65).
4. `Attendance_Rate` (Float): Class attendance percentage ranging from 50.12% to 99.97% (Mean: 78.11%, Std: 14.47%).
5. `Past_Exam_Scores` (Integer): Prior examination marks ranging from 50 to 100 (Mean: 77.87, Std: 14.86).
6. `Parental_Education_Level` (String): Categorical variable (`Bachelors`: 189, `High School`: 183, `Masters`: 171, `PhD`: 165).
7. `Internet_Access_at_Home` (String): Binary categorical variable (`No`: 381, `Yes`: 327).
8. `Extracurricular_Activities` (String): Binary categorical variable (`No`: 361, `Yes`: 347).
9. `Final_Exam_Score` (Integer): The primary numerical target variable representing final exam marks, ranging from 50 to 77 (Mean: 58.77, Std: 6.71).
10. `Pass_Fail` (String): The binary outcome target variable (`Pass`: 354, `Fail`: 354).

## Target Verification & Relationship
Analysis reveals an exact threshold link between `Final_Exam_Score` and `Pass_Fail`:
- **Fail** (354 records): `Final_Exam_Score` in `[50, 59]`
- **Pass** (354 records): `Final_Exam_Score` in `[60, 77]`
- Passing mark threshold is exactly **60**.
