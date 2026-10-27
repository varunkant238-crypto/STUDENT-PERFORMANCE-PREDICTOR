# Feature Selection Report & Justification

## 1. Feature Selection Overview
Per project constraints, the machine learning model must use strictly **4 to 5 input features** rather than all available columns.

Based on exploratory data analysis, correlation values, mutual information rankings, and educational domain considerations, exactly **5 features** have been selected.

---

## 2. Selected Features (Final 5 Input Features)

| Feature Name (Dataset Column) | Type | Valid Range / Categories | Mutual Info | Pearson Correlation | Domain Relevance |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`Past_Exam_Scores`** | Integer | 50 – 100 | 0.4675 | +0.4895 | Academic baseline. Historical test achievement is the strongest single baseline indicator. |
| **`Attendance_Rate`** | Float | 50.0 – 100.0% | 0.6849 | +0.4605 | Consistency & engagement. Highest mutual information score with final grades. |
| **`Study_Hours_per_Week`** | Integer | 10 – 40 hours | 0.3973 | +0.3704 | Direct measure of dedicated independent student effort outside the classroom. |
| **`Parental_Education_Level`** | Categorical | High School, Bachelors, Masters, PhD | 0.0965 | Categorical Grouping | Socio-academic home support environment; higher degrees correlate with structured study culture. |
| **`Extracurricular_Activities`** | Categorical | Yes, No | 0.0358 | Categorical Grouping | Holistic student balance. Students involved in extracurriculars demonstrate balanced time management. |

---

## 3. Justification for Excluded Features

| Excluded Column | Reason for Exclusion |
| :--- | :--- |
| `Student_ID` | Identification code only (nominal). Zero generalizability; including it would lead to spurious memorization. |
| `Gender` | Near-zero correlation ($r \approx 0.03$) and lowest mutual information (0.0028). Excluded to enforce demographic fairness and avoid algorithmic bias. |
| `Internet_Access_at_Home` | Lower predictive power than the top 5 features ($MI = 0.0345$). With 5 feature limit, `Extracurricular_Activities` provides higher qualitative differentiation. |
| `Final_Exam_Score` | Primary prediction target variable (regression). Including as an input would constitute severe target leakage. |
| `Pass_Fail` | Secondary prediction target variable (classification). Ground truth derived from `Final_Exam_Score >= 60`. Must never be fed as an input. |

---

## 4. Single Source of Truth Configuration
All components of the application (data preprocessing, model training, Flask forms, API validation, and database records) reference the identical feature definition located in `preprocessing/preprocessing.py`:

```python
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
```

---

## 5. Potential Limitations of Selected Features
- Student mental health, exam anxiety, and teacher quality are unmeasured in this dataset.
- Attendance rates below 50% are absent from the dataset distribution.
- Model predictions serve as **guidance and risk intervention indicators**, not deterministic guarantees of academic success.
