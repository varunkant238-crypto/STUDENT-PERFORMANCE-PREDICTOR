"""
SQLAlchemy Database Models for Student Performance Predictor.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'admin' or 'student'
    full_name = db.Column(db.String(100), nullable=False)
    student_code = db.Column(db.String(30), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    predictions = db.relationship('Prediction', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password: str):
        """Hash and store password securely."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Validate candidate password against stored hash."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == 'admin'

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    student_code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    gender = db.Column(db.String(20), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Student {self.student_code}>"


class Prediction(db.Model):
    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    student_code = db.Column(db.String(30), nullable=False, index=True)
    
    # 5 Selected Feature Inputs
    study_hours = db.Column(db.Integer, nullable=False)
    attendance_rate = db.Column(db.Float, nullable=False)
    past_scores = db.Column(db.Integer, nullable=False)
    parental_education = db.Column(db.String(50), nullable=False)
    extracurricular = db.Column(db.String(10), nullable=False)

    # Outputs
    predicted_score = db.Column(db.Float, nullable=False)
    pass_fail = db.Column(db.String(10), nullable=False)
    performance_category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'student_code': self.student_code,
            'study_hours': self.study_hours,
            'attendance_rate': self.attendance_rate,
            'past_scores': self.past_scores,
            'parental_education': self.parental_education,
            'extracurricular': self.extracurricular,
            'predicted_score': round(self.predicted_score, 1),
            'pass_fail': self.pass_fail,
            'performance_category': self.performance_category,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else ''
        }

    def __repr__(self):
        return f"<Prediction {self.id} for {self.student_code}: {self.predicted_score} ({self.pass_fail})>"
