import os
import json
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, g, send_from_directory, abort, Response
from models import get_db, init_db, seed_db
from auth import load_logged_in_user, login_required, admin_required, authenticate_user, register_user
from video_security import user_can_access_lesson, stream_video_file
from wix_importer import import_wix_csv

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'smi_university_super_secret_key_2026_trumble')

# Register user loader
@app.before_request
def before_request():
    load_logged_in_user()

# ==============================================================================
# AUTHENTICATION & PUBLIC ROUTES
# ==============================================================================

@app.route('/')
def index():
    if g.user:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        user, err = authenticate_user(email, password)
        if err:
            flash(err, 'danger')
        else:
            session.clear()
            session['user_id'] = user['id']
            flash(f"Welcome back to SMI University, {user['name']}!", 'success')
            next_url = request.args.get('next')
            if next_url:
                return redirect(next_url)
            if user['role'] == 'admin':
                return redirect(url_for('admin_overview'))
            return redirect(url_for('dashboard'))

    return render_template('login.html', active_page='login')

@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name', '')
    email = request.form.get('email', '')
    password = request.form.get('password', '')

    user_id, err = register_user(name, email, password)
    if err:
        flash(err, 'danger')
        return redirect(url_for('login'))

    session.clear()
    session['user_id'] = user_id
    flash(f"Account successfully created! You have been granted free access to the 7-Step Blueprint course.", 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been signed out from SMI University.", "info")
    return redirect(url_for('login'))

# ==============================================================================
# STUDENT DASHBOARD & CLASSROOM
# ==============================================================================

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    cur = conn.cursor()

    # Fetch user's enrolled courses
    cur.execute('''
        SELECT c.*, e.granted_at, e.granted_by
        FROM courses c
        JOIN enrollments e ON c.id = e.course_id
        WHERE e.user_id = ? AND e.status = 'active'
        ORDER BY e.granted_at DESC
    ''', (g.user['id'],))
    enrolled_rows = cur.fetchall()

    enrolled_courses = []
    enrolled_ids = []
    for row in enrolled_rows:
        course_dict = dict(row)
        enrolled_ids.append(row['id'])

        # Calculate progress
        cur.execute("SELECT COUNT(*) FROM lessons WHERE course_id = ?", (row['id'],))
        total_lessons = cur.fetchone()[0] or 1

        cur.execute('''
            SELECT COUNT(*) FROM lesson_progress
            WHERE user_id = ? AND course_id = ? AND completed = 1
        ''', (g.user['id'], row['id']))
        completed_lessons = cur.fetchone()[0]

        percent = int((completed_lessons / total_lessons) * 100) if total_lessons else 0
        course_dict['total_lessons'] = total_lessons
        course_dict['completed_lessons'] = completed_lessons
        course_dict['progress_percent'] = min(100, percent)
        enrolled_courses.append(course_dict)

    # Fetch courses NOT enrolled in
    other_courses = []
    if enrolled_ids:
        placeholders = ','.join('?' for _ in enrolled_ids)
        cur.execute(f"SELECT * FROM courses WHERE id NOT IN ({placeholders}) AND published = 1", enrolled_ids)
        other_courses = [dict(r) for r in cur.fetchall()]
    else:
        cur.execute("SELECT * FROM courses WHERE published = 1")
        other_courses = [dict(r) for r in cur.fetchall()]

    # Find continue learning lesson
    cur.execute('''
        SELECT l.id, l.title, l.duration_mins, c.title AS course_title, c.slug AS course_slug, m.title AS module_title
        FROM lesson_progress lp
        JOIN lessons l ON lp.lesson_id = l.id
        JOIN courses c ON l.course_id = c.id
        JOIN modules m ON l.module_id = m.id
        WHERE lp.user_id = ? AND lp.completed = 0
        ORDER BY lp.updated_at DESC LIMIT 1
    ''', (g.user['id'],))
    continue_lesson = cur.fetchone()

    # If no in-progress lesson, pick first incomplete lesson of first enrolled course
    if not continue_lesson and enrolled_courses:
        first_course_id = enrolled_courses[0]['id']
        cur.execute('''
            SELECT l.id, l.title, l.duration_mins, c.title AS course_title, c.slug AS course_slug, m.title AS module_title
            FROM lessons l
            JOIN courses c ON l.course_id = c.id
            JOIN modules m ON l.module_id = m.id
            WHERE l.course_id = ?
            AND l.id NOT IN (SELECT lesson_id FROM lesson_progress WHERE user_id = ? AND completed = 1)
            ORDER BY m.sort_order ASC, l.sort_order ASC LIMIT 1
        ''', (first_course_id, g.user['id']))
        continue_lesson = cur.fetchone()

    conn.close()
    return render_template(
        'dashboard.html',
        active_page='dashboard',
        enrolled_courses=enrolled_courses,
        other_courses=other_courses,
        continue_lesson=continue_lesson
    )

@app.route('/catalog')
def catalog():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM courses WHERE published = 1 ORDER BY price ASC")
    courses_raw = cur.fetchall()

    enrolled_ids = set()
    if g.user:
        cur.execute("SELECT course_id FROM enrollments WHERE user_id = ? AND status = 'active'", (g.user['id'],))
        enrolled_ids = {r[0] for r in cur.fetchall()}

    courses = []
    for c in courses_raw:
        cd = dict(c)
        cd['is_enrolled'] = c['id'] in enrolled_ids
        cur.execute("SELECT COUNT(*) FROM lessons WHERE course_id = ?", (c['id'],))
        cd['lesson_count'] = cur.fetchone()[0]
        courses.append(cd)

    conn.close()
    return render_template('catalog.html', active_page='catalog', courses=courses)

@app.route('/enroll/free/<int:course_id>', methods=['POST'])
@login_required
def enroll_free(course_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, title, price FROM courses WHERE id = ?", (course_id,))
    course = cur.fetchone()
    if course and course['price'] == 0:
        cur.execute('''
            INSERT OR IGNORE INTO enrollments (user_id, course_id, granted_by, status)
            VALUES (?, ?, 'self_free_enrollment', 'active')
        ''', (g.user['id'], course_id))
        conn.commit()
        flash(f"You have been successfully enrolled in {course['title']}!", "success")
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/enroll/request/<course_slug>')
@login_required
def request_enrollment(course_slug):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM courses WHERE slug = ?", (course_slug,))
    course = cur.fetchone()
    conn.close()
    if not course:
        abort(404)
    flash(f"To enroll in {course['title']} (${int(course['price'])}), please contact our admissions office at (254) 294-7547 or register on the main site. Once registered, your account is provisioned instantly.", "info")
    return redirect(url_for('catalog'))

# ==============================================================================
# COURSERA / UDEMY 2-PANE VIDEO CLASSROOM
# ==============================================================================

@app.route('/classroom/<course_slug>')
@app.route('/classroom/<course_slug>/<int:lesson_id>')
@login_required
def classroom(course_slug, lesson_id=None):
    conn = get_db()
    cur = conn.cursor()

    # 1. Fetch course
    cur.execute("SELECT * FROM courses WHERE slug = ?", (course_slug,))
    course = cur.fetchone()
    if not course:
        conn.close()
        abort(404)

    # 2. Check enrollment access
    is_admin = g.user['role'] == 'admin'
    cur.execute('''
        SELECT id FROM enrollments 
        WHERE user_id = ? AND course_id = ? AND status = 'active'
    ''', (g.user['id'], course['id']))
    enrolled = cur.fetchone()

    # 3. Fetch modules and lessons
    cur.execute("SELECT * FROM modules WHERE course_id = ? ORDER BY sort_order ASC", (course['id'],))
    module_rows = cur.fetchall()

    modules = []
    all_lessons = []
    completed_lesson_ids = set()

    cur.execute('''
        SELECT lesson_id FROM lesson_progress 
        WHERE user_id = ? AND course_id = ? AND completed = 1
    ''', (g.user['id'], course['id']))
    completed_lesson_ids = {r[0] for r in cur.fetchall()}

    for m in module_rows:
        m_dict = dict(m)
        cur.execute("SELECT * FROM lessons WHERE module_id = ? ORDER BY sort_order ASC", (m['id'],))
        l_rows = cur.fetchall()
        lessons_list = []
        for l in l_rows:
            ld = dict(l)
            ld['is_completed'] = l['id'] in completed_lesson_ids
            lessons_list.append(ld)
            all_lessons.append(ld)
        m_dict['lessons'] = lessons_list
        modules.append(m_dict)

    if not all_lessons:
        conn.close()
        flash("This course curriculum is currently being assembled in the workshop.", "warning")
        return redirect(url_for('dashboard'))

    # Determine current lesson
    current_lesson = None
    if lesson_id:
        for l in all_lessons:
            if l['id'] == lesson_id:
                current_lesson = l
                break
    
    if not current_lesson:
        # Pick first uncompleted lesson, or first lesson
        for l in all_lessons:
            if not l['is_completed']:
                current_lesson = l
                break
        if not current_lesson:
            current_lesson = all_lessons[0]

    # Verify access to this specific lesson (if not enrolled, preview lessons are allowed)
    if not is_admin and not enrolled and not current_lesson.get('is_preview'):
        conn.close()
        flash("You do not have an active enrollment for this course. Please enroll or contact admissions to unlock.", "danger")
        return redirect(url_for('catalog'))

    # Find previous and next lessons
    curr_idx = -1
    for idx, l in enumerate(all_lessons):
        if l['id'] == current_lesson['id']:
            curr_idx = idx
            break

    prev_lesson = all_lessons[curr_idx - 1] if curr_idx > 0 else None
    next_lesson = all_lessons[curr_idx + 1] if curr_idx < len(all_lessons) - 1 else None

    # Fetch current module
    cur.execute("SELECT * FROM modules WHERE id = ?", (current_lesson['module_id'],))
    current_module = cur.fetchone()

    # Calculate overall course progress
    total_count = len(all_lessons)
    completed_count = len(completed_lesson_ids)
    progress_percent = int((completed_count / total_count) * 100) if total_count else 0

    conn.close()
    return render_template(
        'classroom.html',
        course=course,
        current_lesson=current_lesson,
        current_module=current_module,
        modules=modules,
        prev_lesson=prev_lesson,
        next_lesson=next_lesson,
        is_completed=current_lesson['id'] in completed_lesson_ids,
        course_progress={
            'total_count': total_count,
            'completed_count': completed_count,
            'percent': progress_percent
        }
    )

# ==============================================================================
# ANTI-DOWNLOAD PROTECTED VIDEO STREAMING API
# ==============================================================================

@app.route('/api/stream/<int:lesson_id>')
def stream_lesson(lesson_id):
    # Enforce active authentication
    if not g.user:
        abort(401)

    is_admin = g.user['role'] == 'admin'
    if not user_can_access_lesson(g.user['id'], lesson_id, is_admin=is_admin):
        abort(403)

    # Check for physical video file
    media_dir = os.path.join(app.root_path, 'static', 'media')
    sample_video = os.path.join(media_dir, 'sample_lesson.mp4')

    if os.path.exists(sample_video):
        return stream_video_file(sample_video)

    # If no MP4 file is found on disk, serve a simulated video stream container
    # so the browser video element renders without crashing
    dummy_mp4_header = b'\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00isommp42'
    resp = Response(dummy_mp4_header, 200, mimetype='video/mp4')
    resp.headers['Content-Disposition'] = 'inline'
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    return resp

@app.route('/api/progress/toggle', methods=['POST'])
@login_required
def toggle_progress():
    data = request.get_json() or {}
    lesson_id = data.get('lesson_id')
    course_id = data.get('course_id')
    completed = 1 if data.get('completed') else 0

    if not lesson_id or not course_id:
        return jsonify({'success': False, 'error': 'Missing parameters'}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO lesson_progress (user_id, lesson_id, course_id, completed, updated_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id, lesson_id) DO UPDATE SET
            completed = excluded.completed,
            updated_at = CURRENT_TIMESTAMP
    ''', (g.user['id'], lesson_id, course_id, completed))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'completed': bool(completed)})

@app.route('/api/progress/time', methods=['POST'])
@login_required
def save_time():
    data = request.get_json(silent=True) or {}
    lesson_id = data.get('lesson_id')
    seconds = data.get('seconds', 0)

    if lesson_id:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('''
            UPDATE lesson_progress 
            SET last_position_seconds = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND lesson_id = ?
        ''', (seconds, g.user['id'], lesson_id))
        conn.commit()
        conn.close()

    return '', 204

# ==============================================================================
# ADMIN STUDIO (MANAGEMENT, WIX MIGRATION, ACCESS CONTROL, COURSE BUILDER)
# ==============================================================================

@app.route('/admin')
@admin_required
def admin_overview():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'student'")
    total_students = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM enrollments WHERE status = 'active'")
    total_enrollments = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM courses")
    total_courses = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE source = 'wix_migration'")
    wix_migrated = cur.fetchone()[0]

    # Recent enrollments
    cur.execute('''
        SELECT e.*, u.name AS user_name, u.email AS user_email, c.title AS course_title
        FROM enrollments e
        JOIN users u ON e.user_id = u.id
        JOIN courses c ON e.course_id = c.id
        ORDER BY e.granted_at DESC LIMIT 8
    ''')
    recent_enrollments = cur.fetchall()
    conn.close()

    return render_template(
        'admin/overview.html',
        active_page='admin_overview',
        stats={
            'total_students': total_students,
            'total_enrollments': total_enrollments,
            'total_courses': total_courses,
            'wix_migrated': wix_migrated
        },
        recent_enrollments=recent_enrollments
    )

@app.route('/admin/users')
@admin_required
def admin_users():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM courses ORDER BY price ASC")
    all_courses = [dict(r) for r in cur.fetchall()]

    cur.execute("SELECT * FROM users ORDER BY created_at DESC")
    user_rows = cur.fetchall()

    users = []
    for u in user_rows:
        ud = dict(u)
        cur.execute("SELECT course_id FROM enrollments WHERE user_id = ? AND status = 'active'", (u['id'],))
        ud['enrolled_course_ids'] = {r[0] for r in cur.fetchall()}
        users.append(ud)

    conn.close()
    return render_template(
        'admin/users.html',
        active_page='admin_users',
        users=users,
        all_courses=all_courses
    )

@app.route('/admin/users/create', methods=['POST'])
@admin_required
def admin_create_user():
    name = request.form.get('name', '')
    email = request.form.get('email', '')
    password = request.form.get('password', 'SMIstudent2026!')
    initial_course_id = request.form.get('initial_course_id')

    user_id, err = register_user(name, email, password, role='student', source='admin_manual')
    if err:
        flash(err, 'danger')
    else:
        if initial_course_id:
            conn = get_db()
            cur = conn.cursor()
            cur.execute('''
                INSERT OR IGNORE INTO enrollments (user_id, course_id, granted_by, status)
                VALUES (?, ?, 'admin_manual', 'active')
            ''', (user_id, initial_course_id))
            conn.commit()
            conn.close()
        flash(f"Student account for {name} ({email}) created successfully!", "success")

    return redirect(url_for('admin_users'))

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    if user_id == g.user['id']:
        flash("You cannot delete your own master admin account.", "danger")
        return redirect(url_for('admin_users'))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    flash("Student account has been removed.", "info")
    return redirect(url_for('admin_users'))

@app.route('/api/admin/toggle_access', methods=['POST'])
@admin_required
def admin_toggle_access():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    course_id = data.get('course_id')

    if not user_id or not course_id:
        return jsonify({'success': False, 'error': 'Missing user_id or course_id'}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, status FROM enrollments WHERE user_id = ? AND course_id = ?", (user_id, course_id))
    existing = cur.fetchone()

    if existing and existing['status'] == 'active':
        # Revoke
        cur.execute("DELETE FROM enrollments WHERE id = ?", (existing['id'],))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'status': 'revoked'})
    else:
        # Grant
        cur.execute('''
            INSERT OR REPLACE INTO enrollments (user_id, course_id, granted_by, status, granted_at)
            VALUES (?, ?, 'admin_manual', 'active', CURRENT_TIMESTAMP)
        ''', (user_id, course_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'status': 'granted'})

@app.route('/admin/grant-self/<int:course_id>')
@admin_required
def admin_grant_self(course_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        INSERT OR IGNORE INTO enrollments (user_id, course_id, granted_by, status)
        VALUES (?, ?, 'admin_self_grant', 'active')
    ''', (g.user['id'], course_id))
    conn.commit()
    conn.close()
    flash("Course successfully unlocked on your admin profile.", "success")
    return redirect(url_for('dashboard'))

@app.route('/admin/wix-migration', methods=['GET', 'POST'])
@admin_required
def admin_wix_migration():
    report = None
    if request.method == 'POST':
        use_sample = request.form.get('use_sample') == 'true'
        default_pw = request.form.get('default_password', 'SMIstudent2026!')

        if use_sample:
            sample_path = os.path.join(app.root_path, 'static', 'sample_wix_export.csv')
            with open(sample_path, 'r', encoding='utf-8') as f:
                csv_data = f.read()
            report = import_wix_csv(csv_data, default_password=default_pw)
            flash(f"Sample Wix CSV successfully processed! Created {report['created_count']} accounts and updated {report['updated_count']}.", "success")
        else:
            file = request.files.get('csv_file')
            if not file or file.filename == '':
                flash("Please select a valid CSV file to upload.", "danger")
            else:
                csv_bytes = file.read()
                report = import_wix_csv(csv_bytes, default_password=default_pw)
                flash(f"Wix CSV import complete! {report['created_count']} accounts created, {report['updated_count']} enrollments granted.", "success")

    return render_template('admin/wix_migration.html', active_page='admin_wix', report=report)

@app.route('/admin/courses')
@admin_required
def admin_courses():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM courses ORDER BY price ASC")
    courses_raw = cur.fetchall()

    courses = []
    for c in courses_raw:
        cd = dict(c)
        cur.execute("SELECT * FROM modules WHERE course_id = ? ORDER BY sort_order ASC", (c['id'],))
        modules = []
        tot_lessons = 0
        for m in cur.fetchall():
            md = dict(m)
            cur.execute("SELECT * FROM lessons WHERE module_id = ? ORDER BY sort_order ASC", (m['id'],))
            md['lessons'] = [dict(l) for l in cur.fetchall()]
            tot_lessons += len(md['lessons'])
            modules.append(md)
        cd['modules'] = modules
        cd['total_lessons'] = tot_lessons
        courses.append(cd)

    conn.close()
    return render_template('admin/courses.html', active_page='admin_courses', courses=courses)

@app.route('/admin/courses/create', methods=['POST'])
@admin_required
def admin_create_course():
    title = request.form.get('title', '').strip()
    category = request.form.get('category', 'Specialized').strip()
    price = float(request.form.get('price', 0.0))
    desc = request.form.get('description', '').strip()

    import re
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')

    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO courses (slug, title, category, description, price, badge, published)
        VALUES (?, ?, ?, ?, ?, 'New Program', 1)
    ''', (slug, title, category, desc, price))
    new_course_id = cur.lastrowid

    # Add default module 1
    cur.execute("INSERT INTO modules (course_id, title, sort_order) VALUES (?, 'Module 1: Orientation & Fundamentals', 1)", (new_course_id,))
    conn.commit()
    conn.close()

    flash(f"Course '{title}' successfully created!", "success")
    return redirect(url_for('admin_courses'))

@app.route('/admin/lessons/add', methods=['POST'])
@admin_required
def admin_add_lesson():
    course_id = request.form.get('course_id')
    title = request.form.get('title', '').strip()
    duration = int(request.form.get('duration_mins', 15))
    is_preview = 1 if request.form.get('is_preview') else 0
    desc = request.form.get('description', '').strip()

    conn = get_db()
    cur = conn.cursor()

    # Get first module or create one
    cur.execute("SELECT id FROM modules WHERE course_id = ? ORDER BY sort_order ASC LIMIT 1", (course_id,))
    mod = cur.fetchone()
    if not mod:
        cur.execute("INSERT INTO modules (course_id, title, sort_order) VALUES (?, 'Core Workshop Modules', 1)", (course_id,))
        module_id = cur.lastrowid
    else:
        module_id = mod[0]

    cur.execute('''
        INSERT INTO lessons (module_id, course_id, title, description, video_source, duration_mins, is_preview, sort_order)
        VALUES (?, ?, ?, ?, 'smi-video-demo', ?, ?, 99)
    ''', (module_id, course_id, title, desc, duration, is_preview))
    conn.commit()
    conn.close()

    flash(f"Lesson '{title}' added to curriculum!", "success")
    return redirect(url_for('admin_courses'))

# ==============================================================================
# MAIN ENTRYPOINT
# ==============================================================================

if __name__ == '__main__':
    init_db()
    seed_db()
    port = int(os.environ.get('PORT', 5000))
    print(f"SMI University Learning Suite running on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
