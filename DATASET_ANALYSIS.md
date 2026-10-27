# Dataset Analysis & Validation Report

## 1. Dataset Verification
- **Official Source**: Amr Maree — [Student Performance Prediction on Kaggle](https://www.kaggle.com/datasets/amrmaree/student-performance-prediction)
- **Local File**: `dataset/student_performance_dataset.csv`
- **File Dimensions**: 708 rows $\times$ 10 columns
- **Integrity**: 0 missing values across all columns.
- **Unique Students**: 500 unique `Student_ID` identifiers (208 repeated observations).

---

## 2. Dataset Columns & Statistical Summary

| Column Name | Data Type | Role | Value Range / Classes | Mean / Distribution |
| :--- | :--- | :--- | :--- | :--- |
| `Student_ID` | String | Identifier | S001 to S500 | 500 unique IDs |
| `Gender` | Categorical | Demographic | Female (375), Male (333) | 53% Female, 47% Male |
| `Study_Hours_per_Week` | Integer | Feature | 10 to 39 | Mean: 26.13, Std: 8.65 |
| `Attendance_Rate` | Float | Feature | 50.12% to 99.97% | Mean: 78.11%, Std: 14.47% |
| `Past_Exam_Scores` | Integer | Feature | 50 to 100 | Mean: 77.87, Std: 14.86 |
| `Parental_Education_Level` | Categorical | Feature | High School (183), Bachelors (189), Masters (171), PhD (165) | Evenly distributed |
| `Internet_Access_at_Home` | Categorical | Feature | No (381), Yes (327) | 53.8% No, 46.2% Yes |
| `Extracurricular_Activities` | Categorical | Feature | No (361), Yes (347) | 51.0% No, 49.0% Yes |
| `Final_Exam_Score` | Integer | Target (Regression) | 50 to 77 | Mean: 58.77, Std: 6.71 |
| `Pass_Fail` | Categorical | Target (Classification) | Pass (354), Fail (354) | 50.0% Pass, 50.0% Fail |

---

## 3. Target Distribution & Pass/Fail Relationship
Analyzing `Final_Exam_Score` grouped by `Pass_Fail`:
- **Fail Group**: Count = 354, Min = 50, Max = 59, Mean = 52.98, Std = 2.45
- **Pass Group**: Count = 354, Min = 60, Max = 77, Mean = 64.56, Std = 4.21

**Key Finding**: The dataset maintains an explicit, rigid passing cutoff at **60 marks**. Any student scoring $\ge 60$ marks is assigned `Pass`, and any score $\le 59$ marks is assigned `Fail`.

---

## 4. Correlation Analysis (Numerical Variables with Target)

| Numerical Feature | Pearson Correlation ($r$) with `Final_Exam_Score` | Interpretation |
| :--- | :--- | :--- |
| `Past_Exam_Scores` | **+0.490** | Strong positive correlation; prior performance strongly predicts current exam outcome. |
| `Attendance_Rate` | **+0.460** | Strong positive correlation; students attending $\ge 85\%$ classes score significantly higher. |
| `Study_Hours_per_Week` | **+0.370** | Moderate positive correlation; direct indicator of self-study effort. |

---

## 5. Mutual Information (Non-linear & Categorical Dependencies)

| Feature | Mutual Information Score with Target |
| :--- | :--- |
| `Attendance_Rate` | **0.6849** |
| `Past_Exam_Scores` | **0.4675** |
| `Study_Hours_per_Week` | **0.3973** |
| `Parental_Education_Level` | **0.0965** |
| `Extracurricular_Activities` | **0.0358** |
| `Internet_Access_at_Home` | 0.0346 |
| `Gender` | 0.0028 |

---

## 6. Preprocessing Strategy
1. **Deduplication**: Remove exact repeated rows for model cross-validation to prevent training/test leakage.
2. **Missing Values**: Dataset has zero missing values. An imputer is included in the pipeline as a safeguard for runtime prediction inputs.
3. **Scaling**: Numerical features (`Attendance_Rate`, `Study_Hours_per_Week`, `Past_Exam_Scores`) are standardized using `StandardScaler` ($\mu=0, \sigma=1$).
4. **Encoding**: Categorical features (`Parental_Education_Level`, `Extracurricular_Activities`) are encoded using `OneHotEncoder(drop='first')`.
