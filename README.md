# Student Performance Predictor

An intelligent, professional academic decision-support web application built with **Python Flask**, **MySQL**, and **Supervised Machine Learning** (Random Forest & Gradient Boosting).

Designed for B.Tech Computer Science & Engineering (CSE) academic project demonstration.

---

## 1. Project Overview & Features

- **Accurate Supervised ML**: Uses strictly **5 validated input features** (Study Hours, Attendance Rate, Past Exam Scores, Parental Education, and Extracurricular Participation) selected via mathematical correlation and mutual information ranking.
- **Triple Output Architecture**:
  1. **Continuous Final Exam Marks** (0 to 100).
  2. **Pass / Fail Classification** (Calibrated with dataset ground truth cutoff at $\ge 60$ marks).
  3. **Qualitative Performance Category** (Grade A: $\ge 70$, Grade B: $65-69$, Grade C: $60-64$, Grade F: $<60$) with targeted academic recommendations.
- **Role-Based Authentication**:
  - **Administrator Portal**: Institution-wide KPI metrics, global prediction activity, and model diagnostic telemetry.
  - **Student Portal**: Personalized prediction submission, real-time feedback, and private prediction history.
- **Enterprise-Grade MySQL Persistence**: Stores all student prediction events with relational timestamps and snapshot parameters. Includes resilient SQLite fallback for offline local demonstrations.
- **Modern Responsive UI**: Built with Bootstrap 5.3, interactive Chart.js widgets, and high-resolution diagnostic plots.
- **7 Core Web Pages**:
  1. `Home` (`/`)
  2. `Dashboard` (`/dashboard`)
  3. `Student Prediction` (`/predict`)
  4. `Student Records` (`/records`)
  5. `Graphs & Diagnostics` (`/graphs`)
  6. `About Project` (`/about`)
  7. `Authentication Portal` (`/login` & `/register`)

---

## 2. Dataset Specification

- **Official Source**: Amr Maree — [Student Performance Prediction on Kaggle](https://www.kaggle.com/datasets/amrmaree/student-performance-prediction)
- **Local Location**: `dataset/student_performance_dataset.csv`
- **Rows**: 708 raw entries (500 unique student profiles)
- **Features Used in Prediction (5)**:
  1. `Study_Hours_per_Week` (Integer: 10–40 hrs/wk)
  2. `Attendance_Rate` (Float: 50.0–100.0%)
  3. `Past_Exam_Scores` (Integer: 50–100 marks)
  4. `Parental_Education_Level` (Categorical: High School, Bachelors, Masters, PhD)
  5. `Extracurricular_Activities` (Categorical: Yes, No)

---

## 3. Prerequisites

Before running the application, make sure you have:
1. **Windows 10 / 11** laptop or PC.
2. **Python 3.10 to 3.13** installed ([Download Python](https://www.python.org/downloads/)).
   - *Ensure "Add Python to PATH" is checked during installation.*
3. **VS Code** (Visual Studio Code).
4. **MySQL Server** or **XAMPP** (Optional for local testing; SQLite fallback operates automatically if MySQL is offline).

---

## 4. Step-by-Step Local Setup & Execution Guide

Open PowerShell or Command Prompt in the project folder (`c:\Users\dell\OneDrive\Desktop\MINI PROJECT`):

### Step 1: Open Project in VS Code
```powershell
code .
```

### Step 2: Install Python Dependencies
Run the following command in the VS Code terminal:
```powershell
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Open `.env` in VS Code and verify your settings. If you have a local MySQL installation, update `DB_PASSWORD` to your local root password.

### Step 4: (Optional) Setup MySQL Database
If using MySQL (via MySQL Command Line Client or XAMPP MySQL):
```sql
CREATE DATABASE student_predictor_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
Then run the automated database initialization script:
```powershell
python init_db.py
```
*(Note: If MySQL is not installed or not running, the application will automatically engage its built-in SQLite engine so you can still run and demonstrate the complete website immediately!)*

### Step 5: Train & Evaluate the Machine Learning Models
Execute the training script to preprocess the Kaggle dataset, fit the models, and persist the artifacts:
```powershell
python model_training/train_model.py
```
To run evaluation diagnostics and refresh static visual charts:
```powershell
python model_training/evaluate_model.py
```

### Step 6: Launch the Web Application
Start the Flask development server:
```powershell
python app.py
```

### Step 7: Open the Application in your Browser
Navigate to:
```
http://127.0.0.1:5000
```

---

## 5. Demo Login Credentials

The database comes pre-seeded with initial accounts for testing:

| Role | Username | Password | Access Privileges |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `AdminPassword@2026` | Full institution statistics, all student records, ML metrics |
| **Student** | `student1` | `StudentPassword@2026` | Personal dashboard, prediction form, private history |

*You can also register a brand new student account directly on the `/login` page.*

---

## 6. Running Automated Tests

To run the complete automated test suite (17 comprehensive tests verifying dataset, preprocessing, models, database, and all 7 pages):
```powershell
pytest -v
```

---

## 7. Project Folder Structure

```
MINI PROJECT/
│
├── app.py                     # Main Flask application entry point
├── config.py                  # Central configuration & environment loader
├── init_db.py                 # MySQL database initializer & seeder
├── requirements.txt           # Python package dependencies
├── .env                       # Active local environment variables
├── .env.example               # Template environment configuration
├── .gitignore                 # Git ignore rules
│
├── dataset/
│   ├── README.md              # Dataset origin & validation details
│   └── student_performance_dataset.csv # Official Kaggle dataset
│
├── analysis/
│   └── data_analysis.py       # Comprehensive exploratory data analysis script
│
├── preprocessing/
│   ├── __init__.py
│   └── preprocessing.py       # Single-source feature definitions & pipelines
│
├── feature_selection/
│   ├── __init__.py
│   └── feature_selection.py   # Mathematical MI & F-score ranking script
│
├── model_training/
│   ├── __init__.py
│   ├── train_model.py         # Supervised ML training pipeline
│   ├── evaluate_model.py      # Model evaluation & holdout testing script
│   └── saved_models/
│       ├── rf_regressor.joblib # Serialized best regression model
│       ├── rf_classifier.joblib# Serialized best classification model
│       ├── preprocessor.joblib # Serialized ColumnTransformer
│       └── model_metadata.json # Production metrics & parameter records
│
├── backend/
│   ├── authentication/
│   │   └── auth.py            # Password hashing & role-based decorators
│   ├── database/
│   │   ├── models.py          # SQLAlchemy User, Student, Prediction models
│   │   └── connection.py      # MySQL connector with resilient SQLite fallback
│   ├── prediction/
│   │   └── predictor.py       # Runtime inference & recommendation engine
│   ├── routes/
│   │   ├── main_routes.py     # 7 required page endpoints
│   │   ├── auth_routes.py     # Login, Register, Logout routes
│   │   └── api_routes.py      # RESTful prediction & analytics API
│   └── services/
│       └── student_service.py # Business logic & analytics aggregations
│
├── frontend/
│   ├── templates/
│   │   ├── base.html          # Base layout with navbar & footer
│   │   ├── home.html          # Page 1: Landing page
│   │   ├── dashboard.html     # Page 2: Role-based dashboard
│   │   ├── prediction.html    # Page 3: 5-feature prediction form
│   │   ├── student_records.html # Page 4: Filterable records table
│   │   ├── graphs.html        # Page 5: Visual analytics & charts
│   │   ├── about.html         # Page 6: Academic project report
│   │   └── login.html         # Page 7: Authentication interface
│   └── static/
│       ├── css/style.css      # Custom modern styling
│       ├── js/main.js         # Interactive Chart.js scripts
│       └── images/            # Generated high-resolution diagnostic plots
│
├── tests/
│   ├── test_dataset.py        # Kaggle dataset integrity tests
│   ├── test_preprocessing.py  # Feature validation & range tests
│   ├── test_model.py          # Machine learning inference tests
│   ├── test_database.py       # User, Student, Prediction ORM tests
│   └── test_routes.py         # All 7 pages & API route tests
│
└── deployment/
    ├── DEPLOYMENT_GUIDE.md    # Render, PythonAnywhere, AWS deployment guide
    ├── Procfile               # Cloud WSGI runner declaration
    └── wsgi.py                # Production WSGI application wrapper
```

---

## 8. Troubleshooting

- **Issue: `ModuleNotFoundError: No module named 'flask'`**
  - **Solution**: Ensure your virtual environment is active and run `pip install -r requirements.txt`.
- **Issue: MySQL connection refused (`Can't connect to MySQL server on 'localhost'`)**
  - **Solution**: The application automatically handles this by activating its SQLite engine so local testing continues uninterrupted! If you want to use MySQL, start MySQL service via Windows Services (`services.msc`) or start MySQL in XAMPP Control Panel.
- **Issue: Model files not found**
  - **Solution**: Execute `python model_training/train_model.py` to regenerate the model artifacts in `model_training/saved_models/`.
