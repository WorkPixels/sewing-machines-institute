import csv
import io
from werkzeug.security import generate_password_hash
from models import get_db

COURSE_KEYWORD_MAP = {
    'correspondence': 'protraining-1-correspondence',
    'protraining 1': 'protraining-1-correspondence',
    'pro training 1': 'protraining-1-correspondence',
    'computerized': 'protraining-2-computerized',
    'electronic': 'protraining-2-computerized',
    'protraining 2': 'protraining-2-computerized',
    'live': 'live-5-day-bench-companion',
    '5-day': 'live-5-day-bench-companion',
    'immersion': 'live-5-day-bench-companion',
    'industrial': 'industrial-lockstitch-mastery',
    'lockstitch': 'industrial-lockstitch-mastery',
    'free': 'free-7-step-maintenance',
    '7-step': 'free-7-step-maintenance'
}

def match_course_slug(purchase_text, default_slug='protraining-1-correspondence'):
    if not purchase_text:
        return default_slug
    lower_text = purchase_text.lower()
    for kw, slug in COURSE_KEYWORD_MAP.items():
        if kw in lower_text:
            return slug
    return default_slug

def import_wix_csv(csv_content_or_file, default_password="SMIstudent2026!"):
    if isinstance(csv_content_or_file, bytes):
        text_stream = io.StringIO(csv_content_or_file.decode('utf-8', errors='ignore'))
    elif isinstance(csv_content_or_file, str):
        text_stream = io.StringIO(csv_content_or_file)
    else:
        text_stream = io.TextIOWrapper(csv_content_or_file, encoding='utf-8', errors='ignore')

    reader = csv.DictReader(text_stream)
    
    # Normalize headers
    normalized_fields = {}
    if reader.fieldnames:
        for f in reader.fieldnames:
            clean = f.strip().lower()
            normalized_fields[clean] = f

    report = {
        'total_rows': 0,
        'created_count': 0,
        'updated_count': 0,
        'skipped_count': 0,
        'created_users': [],
        'updated_users': [],
        'skipped_rows': [],
        'errors': []
    }

    conn = get_db()
    cur = conn.cursor()

    # Pre-fetch course mapping
    cur.execute("SELECT id, slug, title FROM courses")
    courses = {row['slug']: row['id'] for row in cur.fetchall()}
    default_pw_hash = generate_password_hash(default_password)

    for row_idx, row in enumerate(reader, start=1):
        report['total_rows'] += 1
        
        # Extract email
        email = None
        for key in ['email', 'e-mail', 'contact email', 'customer email']:
            if key in normalized_fields:
                val = row.get(normalized_fields[key], '').strip()
                if '@' in val:
                    email = val.lower()
                    break
        
        if not email:
            report['skipped_count'] += 1
            report['skipped_rows'].append({'row': row_idx, 'reason': 'No valid email address found in row'})
            continue

        # Extract name
        name = ""
        first_name = row.get(normalized_fields.get('first name', ''), '').strip()
        last_name = row.get(normalized_fields.get('last name', ''), '').strip()
        if first_name or last_name:
            name = f"{first_name} {last_name}".strip()
        elif 'name' in normalized_fields:
            name = row.get(normalized_fields['name'], '').strip()
        
        if not name:
            name = email.split('@')[0].capitalize()

        # Extract purchased product / plan
        purchased_item = ""
        for pkey in ['purchased course', 'course', 'product', 'item name', 'plan', 'order name', 'tags']:
            if pkey in normalized_fields:
                purchased_item = row.get(normalized_fields[pkey], '').strip()
                if purchased_item:
                    break

        matched_slug = match_course_slug(purchased_item)
        target_course_id = courses.get(matched_slug, courses.get('protraining-1-correspondence'))

        # Check if user exists
        cur.execute("SELECT id, name FROM users WHERE email = ?", (email,))
        existing_user = cur.fetchone()

        if existing_user:
            user_id = existing_user['id']
            # Grant course enrollment
            cur.execute('''
                INSERT OR IGNORE INTO enrollments (user_id, course_id, granted_by, status)
                VALUES (?, ?, 'wix_migration', 'active')
            ''', (user_id, target_course_id))
            
            report['updated_count'] += 1
            report['updated_users'].append({
                'name': existing_user['name'],
                'email': email,
                'course_slug': matched_slug,
                'status': 'Enrolled in course'
            })
        else:
            # Create user
            cur.execute('''
                INSERT INTO users (name, email, password_hash, role, status, source, notes)
                VALUES (?, ?, ?, 'student', 'active', 'wix_migration', ?)
            ''', (name, email, default_pw_hash, f'Migrated from Wix export (Order: {purchased_item or "General"})'))
            user_id = cur.lastrowid

            # Enroll in matched course
            cur.execute('''
                INSERT INTO enrollments (user_id, course_id, granted_by, status)
                VALUES (?, ?, 'wix_migration', 'active')
            ''', (user_id, target_course_id))

            # Also enroll in Free Course automatically
            free_id = courses.get('free-7-step-maintenance')
            if free_id and free_id != target_course_id:
                cur.execute('''
                    INSERT OR IGNORE INTO enrollments (user_id, course_id, granted_by, status)
                    VALUES (?, ?, 'wix_migration', 'active')
                ''', (user_id, free_id))

            report['created_count'] += 1
            report['created_users'].append({
                'name': name,
                'email': email,
                'course_slug': matched_slug,
                'temp_password': default_password
            })

    conn.commit()
    conn.close()
    return report
