"""
Flask Routes and View Tests.
Validates all 7 required website pages and permission guards.
"""

import pytest
from app import create_app
from config import Config
from backend.database.models import db, User

class TestRouteConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test_secret'

@pytest.fixture
def client():
    app = create_app(TestRouteConfig)
    with app.app_context():
        db.create_all()
        # Seed test admin & student
        admin = User(username='testadmin', email='adm@test.com', full_name='Test Admin', role='admin')
        admin.set_password('AdminPass123')
        student = User(username='teststudent', email='stu@test.com', full_name='Test Student', role='student', student_code='S100')
        student.set_password('StudentPass123')
        db.session.add_all([admin, student])
        db.session.commit()

        with app.test_client() as client:
            yield client
            
        db.session.remove()
        db.drop_all()

# Page 1: Home
def test_home_page_renders(client):
    res = client.get('/')
    assert res.status_code == 200
    assert b"Student Academic Performance Predictor" in res.data

# Page 6: About
def test_about_page_renders(client):
    res = client.get('/about')
    assert res.status_code == 200
    assert b"About the Project" in res.data

# Page 7: Login
def test_login_page_renders(client):
    res = client.get('/login')
    assert res.status_code == 200
    assert b"Sign In" in res.data

# Protected Pages: Redirect unauthenticated users
def test_protected_pages_redirect_guest(client):
    for endpoint in ['/dashboard', '/predict', '/records', '/graphs']:
        res = client.get(endpoint, follow_redirects=False)
        assert res.status_code == 302, f"Endpoint {endpoint} allowed guest access"
        assert '/login' in res.location

# Authenticated Session Navigation
def test_authenticated_student_flows(client):
    # Log in as student
    login_res = client.post('/login', data={'username': 'teststudent', 'password': 'StudentPass123'}, follow_redirects=True)
    assert login_res.status_code == 200

    # Page 2: Dashboard
    res = client.get('/dashboard')
    assert res.status_code == 200
    assert b"Dashboard" in res.data

    # Page 3: Prediction Form GET & POST
    res = client.get('/predict')
    assert res.status_code == 200
    assert b"Student Performance Prediction Form" in res.data

    post_res = client.post('/predict', data={
        'student_code': 'S100',
        'study_hours': '25',
        'attendance_rate': '85.0',
        'past_scores': '75',
        'parental_education': 'Bachelors',
        'extracurricular': 'Yes'
    }, follow_redirects=True)
    assert post_res.status_code == 200
    assert b"Predicted Academic Status" in post_res.data

    # Page 4: Student Records
    res = client.get('/records')
    assert res.status_code == 200
    assert b"Student Records" in res.data

    # Page 5: Graphs
    res = client.get('/graphs')
    assert res.status_code == 200
    assert b"Performance Graphs" in res.data

    # API Health Check
    api_res = client.get('/api/health')
    assert api_res.status_code == 200
    assert api_res.json['status'] == 'healthy'

# Multi-Device & Account Switch Resilience Flow
def test_cross_device_account_switch_flow(client):
    # 1. Log in initially as teststudent
    login_res = client.post('/login', data={'username': 'teststudent', 'password': 'StudentPass123'}, follow_redirects=True)
    assert login_res.status_code == 200
    assert b"Test Student" in login_res.data

    # 2. Re-visiting /login must render 200 OK (never block or silently redirect)
    switch_view_res = client.get('/login')
    assert switch_view_res.status_code == 200
    assert b"Sign In to Account" in switch_view_res.data
    assert b"Active Session Detected" in switch_view_res.data or b"Test Student" in switch_view_res.data

    # 3. Switching accounts by logging in as testadmin seamlessly succeeds
    switch_login_res = client.post('/login', data={'username': 'testadmin', 'password': 'AdminPass123'}, follow_redirects=True)
    assert switch_login_res.status_code == 200
    assert b"Test Admin" in switch_login_res.data

    # 4. Visiting /register while authenticated also renders 200 OK
    reg_view_res = client.get('/register')
    assert reg_view_res.status_code == 200
    assert b"Create Student Account" in reg_view_res.data

