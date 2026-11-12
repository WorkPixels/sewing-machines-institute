from functools import wraps
from flask import session, redirect, url_for, flash, request, g
from werkzeug.security import check_password_hash, generate_password_hash
from models import get_db

def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, name, email, role, status, created_at, last_login FROM users WHERE id = ?", (user_id,))
        g.user = cur.fetchone()
        conn.close()

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash("Please sign in to access your SMI University classroom.", "warning")
            return redirect(url_for('login', next=request.url))
        return view(**kwargs)
    return wrapped_view

def admin_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash("Admin authentication required.", "danger")
            return redirect(url_for('login', next=request.url))
        if g.user['role'] != 'admin':
            flash("Access denied. Administrator privileges required.", "danger")
            return redirect(url_for('dashboard'))
        return view(**kwargs)
    return wrapped_view

def authenticate_user(email, password):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ? COLLATE NOCASE", (email.strip(),))
    user = cur.fetchone()

    if user and check_password_hash(user['password_hash'], password):
        if user['status'] != 'active':
            conn.close()
            return None, "This account has been deactivated. Please contact admissions."
        
        # Update last login
        cur.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user['id'],))
        conn.commit()
        conn.close()
        return user, None
    
    conn.close()
    return None, "Invalid email address or password."

def register_user(name, email, password, role='student', source='web'):
    conn = get_db()
    cur = conn.cursor()
    try:
        pw_hash = generate_password_hash(password)
        cur.execute('''
            INSERT INTO users (name, email, password_hash, role, status, source)
            VALUES (?, ?, ?, ?, 'active', ?)
        ''', (name.strip(), email.strip().lower(), pw_hash, role, source))
        user_id = cur.lastrowid

        # Auto-grant access to Free 7-Step course
        cur.execute("SELECT id FROM courses WHERE slug = 'free-7-step-maintenance'")
        free_course = cur.fetchone()
        if free_course:
            cur.execute('''
                INSERT OR IGNORE INTO enrollments (user_id, course_id, granted_by, status)
                VALUES (?, ?, 'automatic_registration', 'active')
            ''', (user_id, free_course['id']))

        conn.commit()
        conn.close()
        return user_id, None
    except Exception as e:
        conn.close()
        if 'UNIQUE constraint failed' in str(e):
            return None, "An account with this email address already exists."
        return None, f"Error registering user: {str(e)}"
