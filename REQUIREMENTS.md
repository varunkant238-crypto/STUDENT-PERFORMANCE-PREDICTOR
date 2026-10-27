# Functional & Non-Functional Requirements Specification

## 1. System Overview
The **Student Performance Predictor** is a web-based decision support system designed to predict a student's final examination score, pass/fail status, and qualitative performance category using a trained supervised machine learning model.

---

## 2. Functional Requirements (FR)

### FR-1: Dataset Management & Verification
- **FR-1.1**: The system must load and validate the official Amr Maree Kaggle student performance dataset.
- **FR-1.2**: Data preprocessing must systematically handle missing values, encode categorical variables, and normalize numerical features.
- **FR-1.3**: Dataset duplicates must be recognized and processed to prevent cross-validation leakage.

### FR-2: Feature Selection & Model Inference
- **FR-2.1**: The prediction pipeline must strictly utilize exactly 5 designated features:
  1. `Study_Hours_per_Week`
  2. `Attendance_Rate`
  3. `Past_Exam_Scores`
  4. `Parental_Education_Level`
  5. `Extracurricular_Activities`
- **FR-2.2**: Predictions must be executed in real-time from serialized models without re-training on each request.
- **FR-2.3**: Model outputs must provide:
  - Numerical final score (continuous scale 0-100, bounded to realistic range).
  - Pass/Fail status based on verified dataset passing criteria ($\ge 60$ marks).
  - Performance category (Excellent, Good, Average, Needs Improvement).

### FR-3: User Authentication & Role Management
- **FR-3.1**: Secure user registration for students and credentialed login for both Admins and Students.
- **FR-3.2**: Password hashing using cryptographic one-way salted hashing.
- **FR-3.3**: Protected routes enforcing role authorization.
- **FR-3.4**: Session timeout and secure logout mechanism.

### FR-4: Prediction Submission & Database Persistence
- **FR-4.1**: Input validation enforcing bounded numerical ranges (e.g., Attendance between 0% and 100%).
- **FR-4.2**: Storage of every valid prediction query into MySQL (`predictions` table) with student identifier and timestamp.
- **FR-4.3**: Multi-tenant isolation ensuring students can only query their own historical prediction logs.

### FR-5: Analytics & Visualizations
- **FR-5.1**: Dedicated analytical charts displaying dataset distribution, correlation matrix, and feature importances.
- **FR-5.2**: Dashboard metrics displaying live counts of predictions, students, pass rates, and model metrics.

---

## 3. Non-Functional Requirements (NFR)

### NFR-1: Performance & Latency
- Prediction response time under 100 milliseconds.
- Dashboard and records queries optimized with indexed keys.

### NFR-2: Security
- SQL Injection mitigation via SQLAlchemy ORM parameterized queries.
- Cross-Site Scripting (XSS) mitigation via Jinja2 auto-escaping.
- Sensitive credentials isolated in `.env` files.

### NFR-3: Reliability & Error Handling
- Robust fallback when external MySQL services are unreachable or unconfigured.
- Graceful error messaging to end-users without exposing database connection strings or stack traces.

### NFR-4: Usability & Responsiveness
- Intuitive Bootstrap 5 UI supporting mobile, tablet, and desktop viewports.
- Clear contextual tooltips and descriptive form labels.
