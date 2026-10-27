"""
Database and Authentication Unit Tests.
"""

import pytest
from app import create_app
from config import Config
from backend.database.models import db, User, Student, Prediction

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

@pytest.fixture
def app_instance():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

def test_password_hashing(app_instance):
    user = User(username='teststudent', email='test@edu.com', full_name='Test Student', role='student')
    user.set_password('Secret123')
    assert user.password_hash != 'Secret123'
    assert user.check_password('Secret123') is True
    assert user.check_password('WrongPass') is False

def test_prediction_creation_and_cascade(app_instance):
    user = User(username='preduser', email='p@edu.com', full_name='Pred User', role='student')
    user.set_password('Pass123')
    db.session.add(user)
    db.session.commit()

    pred = Prediction(
        user_id=user.id,
        student_code='S999',
        study_hours=25,
        attendance_rate=80.0,
        past_scores=70,
        parental_education='Bachelors',
        extracurricular='Yes',
        predicted_score=68.5,
        pass_fail='Pass',
        performance_category='Good (Grade B)'
    )
    db.session.add(pred)
    db.session.commit()

    assert pred.id is not None
    assert user.predictions.count() == 1
    assert pred.user.username == 'preduser'
