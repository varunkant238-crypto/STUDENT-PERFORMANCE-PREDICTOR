# Student Performance Predictor — Project Implementation Plan

## 1. Project Overview & Role
- **Project Name**: Student Performance Predictor
- **Target Audience / Purpose**: B.Tech CSE Final Year / Mini-Project Demonstration
- **Primary Goals**:
  1. Build a robust, end-to-end predictive web application using real-world academic data.
  2. Employ supervised Machine Learning with strictly 5 carefully selected input features.
  3. Support dual target outputs: Predicted final exam marks, Pass/Fail outcome, and graded performance categories.
  4. Implement role-based authentication (Admin & Student) with MySQL persistence.
  5. Provide an attractive, responsive UI with interactive dashboards and analytical charts.

---

## 2. Dataset Verification & Objective
- **Kaggle Source**: [https://www.kaggle.com/datasets/amrmaree/student-performance-prediction](https://www.kaggle.com/datasets/amrmaree/student-performance-prediction)
- **Local File**: `dataset/student_performance_dataset.csv` (708 rows, 10 columns, verified complete).
- **Target Identification**:
  - `Final_Exam_Score` (Continuous marks, 50 to 77).
  - `Pass_Fail` (Binary status: 354 Pass, 354 Fail; Pass threshold is verified at $\ge 60$).

---

## 3. Feature Selection Strategy
To prevent overfitting, avoid target leakage, and deliver an intuitive user experience:
- **5 Selected Features**:
  1. `Study_Hours_per_Week` (Academic effort, 10-39 hrs/week)
  2. `Attendance_Rate` (Class consistency, 50-100%)
  3. `Past_Exam_Scores` (Academic baseline, 50-100)
  4. `Parental_Education_Level` (Socio-cultural support: High School, Bachelors, Masters, PhD)
  5. `Extracurricular_Activities` (Holistic student involvement: Yes, No)
- Excluded Features:
  - `Student_ID`: Unique key / nominal, non-generalizable.
  - `Gender`: Discarded to maintain demographic fairness and low mutual information.
  - `Internet_Access_at_Home`: Lower correlation/importance than study hours and attendance.
  - `Pass_Fail` & `Final_Exam_Score`: Target variables.

---

## 4. Machine Learning Methodology
- **Regression**: Random Forest Regressor & Gradient Boosting for continuous final marks prediction.
- **Classification**: Random Forest Classifier & threshold mapping for binary Pass/Fail ($\ge 60$).
- **Performance Tiers**:
  - `Excellent (Grade A)`: Marks $\ge 70$
  - `Good (Grade B)`: $65 \le \text{Marks} < 70$
  - `Average (Grade C - Pass)`: $60 \le \text{Marks} < 65$
  - `Needs Improvement (Grade F - Fail)`: $\text{Marks} < 60$
- **Pipeline & Serialization**: `ColumnTransformer` with `StandardScaler` for numerical and `OneHotEncoder` for categorical variables saved using `joblib`.

---

## 5. Database Architecture (MySQL)
- **Engine**: MySQL 8.0+ via SQLAlchemy & PyMySQL.
- **Resilient Fallback**: Graceful handling of offline MySQL with local SQLite fallback for seamless zero-setup live demos, while keeping full MySQL schema and migration readiness.
- **Entities**:
  - `User`: Admin and student credentials, role-based permissions, bcrypt/werkzeug hashed passwords.
  - `StudentProfile`: Linked profile metadata, student code, demographic background.
  - `PredictionRecord`: Input parameters, predicted marks, pass/fail result, tier, and timestamp.

---

## 6. Authentication & Access Control
- Session-based authentication via Flask Sessions.
- Passwords hashed with salted SHA-256 (`werkzeug.security`).
- Decorators: `@login_required`, `@admin_required`.
- Role segregation:
  - **Admin**: View all student records, global prediction logs, system analytics, model performance.
  - **Student**: Access personalized dashboard, submit prediction forms, view only self prediction history.

---

## 7. Website Structure (7 Required Pages)
1. **Home** (`/`): Landing presentation, key features, architecture overview, quick access.
2. **Dashboard** (`/dashboard`): Role-aware analytics, KPIs, recent predictions, model summary.
3. **Student Prediction** (`/predict`): 5-input prediction form, validation, real-time ML result display.
4. **Student Records** (`/records`): Filterable, searchable table of students and predictions.
5. **Graphs** (`/graphs`): Visual charts (score distributions, correlations, model feature importance).
6. **About Project** (`/about`): Academic mini-project documentation, methodology, stack, and limitations.
7. **Login / Register** (`/login`, `/register`, `/logout`): Secure authentication interface.

---

## 8. Testing Strategy
- Unit & Integration testing with `pytest`.
- Coverage:
  - Dataset loading and validation.
  - Feature selection pipeline integrity.
  - ML model inference and range validity.
  - Authentication and role-based route guard checks.
  - Database CRUD and connection error handling.

---

## 9. Deployment Preparation
- Environment configuration via `.env.example`.
- WSGI entry point `app.py` compatible with Gunicorn / Waitress.
- Production guidelines for Render, PythonAnywhere, and AWS EC2.
