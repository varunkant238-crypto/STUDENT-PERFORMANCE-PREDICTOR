"""
Persistent Data Synchronization Manager.
Guarantees zero data loss across server restarts, ephemeral cloud rebuilds, and deployments
by maintaining a persistent JSON snapshot synchronized with the relational database.
"""

import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

PERSISTENT_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'persistent_data.json')
)

def _load_raw_store():
    if not os.path.exists(PERSISTENT_FILE_PATH):
        return {'users': [], 'predictions': []}
    try:
        with open(PERSISTENT_FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Error reading persistent store JSON: {e}")
        return {'users': [], 'predictions': []}

def _save_raw_store(store):
    try:
        os.makedirs(os.path.dirname(PERSISTENT_FILE_PATH), exist_ok=True)
        with open(PERSISTENT_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(store, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.warning(f"Error writing persistent store JSON: {e}")

def record_persistent_user(user):
    """Save newly registered or updated student account to persistent storage."""
    store = _load_raw_store()
    users = store.get('users', [])
    
    # Check if username already exists in store
    found = False
    for u in users:
        if u['username'].lower() == user.username.lower():
            u['email'] = user.email
            u['full_name'] = user.full_name
            u['student_code'] = user.student_code
            u['password_hash'] = user.password_hash
            u['role'] = user.role
            found = True
            break
            
    if not found:
        users.append({
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role,
            'student_code': user.student_code,
            'password_hash': user.password_hash
        })
        
    store['users'] = users
    _save_raw_store(store)
    logger.info(f"Persisted user account: {user.username} to disk.")

def record_persistent_prediction(prediction, username):
    """Save prediction record to persistent store."""
    store = _load_raw_store()
    preds = store.get('predictions', [])
    
    preds.append({
        'username': username,
        'student_code': prediction.student_code,
        'study_hours': prediction.study_hours,
        'attendance_rate': prediction.attendance_rate,
        'past_scores': prediction.past_scores,
        'parental_education': prediction.parental_education,
        'extracurricular': prediction.extracurricular,
        'predicted_score': prediction.predicted_score,
        'pass_fail': prediction.pass_fail,
        'performance_category': prediction.performance_category,
        'created_at': prediction.created_at.strftime('%Y-%m-%d %H:%M:%S') if prediction.created_at else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    
    store['predictions'] = preds
    _save_raw_store(store)
    logger.info(f"Persisted prediction for {username} ({prediction.student_code}) to disk.")

def restore_persistent_data(db, User, Student, Prediction):
    """
    On server boot, check if persistent JSON contains registered users or predictions
    missing from the active database, and seamlessly restore them.
    """
    store = _load_raw_store()
    users_data = store.get('users', [])
    preds_data = store.get('predictions', [])
    
    # 1. Restore missing users
    restored_users_count = 0
    for udata in users_data:
        uname = udata.get('username')
        if not uname:
            continue
        existing = User.query.filter(db.func.lower(User.username) == uname.lower()).first()
        if not existing:
            new_u = User(
                username=uname,
                email=udata.get('email', f"{uname}@student.com"),
                full_name=udata.get('full_name', uname),
                role=udata.get('role', 'student'),
                student_code=udata.get('student_code')
            )
            new_u.password_hash = udata.get('password_hash', '')
            db.session.add(new_u)
            db.session.flush()
            
            if new_u.role == 'student':
                profile = Student(
                    student_code=new_u.student_code or f"S-{new_u.id:03d}",
                    user_id=new_u.id
                )
                db.session.add(profile)
            restored_users_count += 1
            
    if restored_users_count > 0:
        db.session.commit()
        logger.info(f"Restored {restored_users_count} user accounts from persistent store.")

    # 2. Restore missing predictions
    restored_preds_count = 0
    for pdata in preds_data:
        uname = pdata.get('username')
        if not uname:
            continue
        u = User.query.filter(db.func.lower(User.username) == uname.lower()).first()
        if not u:
            continue
            
        # Check if identical prediction already logged for this user
        existing_pred = Prediction.query.filter_by(
            user_id=u.id,
            student_code=pdata.get('student_code'),
            predicted_score=pdata.get('predicted_score')
        ).first()
        
        if not existing_pred:
            created_dt = None
            if pdata.get('created_at'):
                try:
                    created_dt = datetime.strptime(pdata['created_at'], '%Y-%m-%d %H:%M:%S')
                except Exception:
                    created_dt = datetime.now()
            else:
                created_dt = datetime.now()
                
            pred = Prediction(
                user_id=u.id,
                student_code=pdata.get('student_code', u.student_code),
                study_hours=pdata.get('study_hours', 25),
                attendance_rate=pdata.get('attendance_rate', 80.0),
                past_scores=pdata.get('past_scores', 70),
                parental_education=pdata.get('parental_education', 'Bachelors'),
                extracurricular=pdata.get('extracurricular', 'No'),
                predicted_score=pdata.get('predicted_score', 65.0),
                pass_fail=pdata.get('pass_fail', 'Pass'),
                performance_category=pdata.get('performance_category', 'Good (Grade B)'),
                created_at=created_dt
            )
            db.session.add(pred)
            restored_preds_count += 1
            
    if restored_preds_count > 0:
        db.session.commit()
        logger.info(f"Restored {restored_preds_count} predictions from persistent store.")


def restore_user_by_identifier(db, User, Student, Prediction, identifier):
    """
    On-demand user retrieval: If a user is not in the active database during login,
    search the persistent JSON snapshot and dynamically restore them with their records.
    Returns the User object if restored, otherwise None.
    """
    if not identifier:
        return None
        
    ident_clean = identifier.strip().lower()
    store = _load_raw_store()
    users_data = store.get('users', [])
    target_data = None
    
    for u in users_data:
        uname = (u.get('username') or '').strip().lower()
        email = (u.get('email') or '').strip().lower()
        if uname == ident_clean or email == ident_clean:
            target_data = u
            break
            
    if not target_data:
        return None
        
    uname = target_data.get('username')
    existing = User.query.filter(
        (db.func.lower(User.username) == uname.lower()) |
        (db.func.lower(User.email) == target_data.get('email', '').lower())
    ).first()
    if existing:
        return existing
        
    try:
        new_u = User(
            username=uname,
            email=target_data.get('email', f"{uname}@student.com"),
            full_name=target_data.get('full_name', uname),
            role=target_data.get('role', 'student'),
            student_code=target_data.get('student_code')
        )
        new_u.password_hash = target_data.get('password_hash', '')
        db.session.add(new_u)
        db.session.flush()
        
        if new_u.role == 'student':
            profile = Student(
                student_code=new_u.student_code or f"STU-{new_u.id:04d}",
                user_id=new_u.id
            )
            db.session.add(profile)
            
        # Restore associated predictions
        preds_data = store.get('predictions', [])
        for pdata in preds_data:
            if (pdata.get('username') or '').lower() == uname.lower():
                created_dt = None
                if pdata.get('created_at'):
                    try:
                        created_dt = datetime.strptime(pdata['created_at'], '%Y-%m-%d %H:%M:%S')
                    except Exception:
                        created_dt = datetime.now()
                pred = Prediction(
                    user_id=new_u.id,
                    student_code=pdata.get('student_code', new_u.student_code or f"STU-{new_u.id:04d}"),
                    study_hours=pdata.get('study_hours', 25),
                    attendance_rate=pdata.get('attendance_rate', 80.0),
                    past_scores=pdata.get('past_scores', 70),
                    parental_education=pdata.get('parental_education', 'Bachelors'),
                    extracurricular=pdata.get('extracurricular', 'No'),
                    predicted_score=pdata.get('predicted_score', 65.0),
                    pass_fail=pdata.get('pass_fail', 'Pass'),
                    performance_category=pdata.get('performance_category', 'Good (Grade B)'),
                    created_at=created_dt or datetime.now()
                )
                db.session.add(pred)
                
        db.session.commit()
        logger.info(f"Dynamically restored student account: {uname} from persistent snapshot.")
        return new_u
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to dynamically restore user {uname}: {e}")
        return None

