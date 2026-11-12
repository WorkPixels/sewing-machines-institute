import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'smi_university.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'student',
        status TEXT DEFAULT 'active',
        source TEXT DEFAULT 'web',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        notes TEXT
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        price REAL DEFAULT 0.0,
        badge TEXT,
        thumbnail_url TEXT,
        published INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS modules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
        title TEXT NOT NULL,
        sort_order INTEGER DEFAULT 0
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS lessons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        module_id INTEGER NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
        course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
        title TEXT NOT NULL,
        description TEXT,
        video_source TEXT,
        duration_mins INTEGER DEFAULT 15,
        notes_md TEXT,
        attachment_pdf TEXT,
        is_preview INTEGER DEFAULT 0,
        sort_order INTEGER DEFAULT 0
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
        granted_by TEXT DEFAULT 'manual_admin',
        granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,
        status TEXT DEFAULT 'active',
        UNIQUE(user_id, course_id)
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS lesson_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        lesson_id INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
        course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
        completed INTEGER DEFAULT 0,
        last_position_seconds INTEGER DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, lesson_id)
    )
    ''')

    conn.commit()
    conn.close()

def seed_db():
    conn = get_db()
    cur = conn.cursor()

    # Check if admin exists
    cur.execute("SELECT id FROM users WHERE email = 'admin@sewingmachinesinstitute.com'")
    if not cur.fetchone():
        admin_pass = generate_password_hash("SMIadmin2026!")
        cur.execute('''
            INSERT INTO users (name, email, password_hash, role, status, source, notes)
            VALUES (?, ?, ?, 'admin', 'active', 'system', 'Master Administrator - Jeremiah Trumble / SMI University Lead')
        ''', ('Jeremiah Trumble (Admin)', 'admin@sewingmachinesinstitute.com', admin_pass))

        cur.execute('''
            INSERT INTO users (name, email, password_hash, role, status, source, notes)
            VALUES (?, ?, ?, 'admin', 'active', 'system', 'Master Administrator - Joyanna Dunaway / SMI Director')
        ''', ('Joyanna Dunaway (Admin)', 'joyanna@sewingmachinesinstitute.com', admin_pass))

        student_pass = generate_password_hash("Student2026!")
        cur.execute('''
            INSERT INTO users (name, email, password_hash, role, status, source, notes)
            VALUES (?, ?, ?, 'student', 'active', 'web', 'Demonstration Student Account')
        ''', ('Sarah Jenkins (Sample Student)', 'student@sewingmachinesinstitute.com', student_pass))

    # Check if courses exist
    cur.execute("SELECT COUNT(*) FROM courses")
    if cur.fetchone()[0] == 0:
        courses_data = [
            (
                'free-7-step-maintenance',
                'Free 7-Step Sewing Machine Maintenance Blueprint',
                'Foundational',
                'The essential mechanical checkpoints every sewer and aspiring technician must know before ever calling a repair shop. Demystify thread tension, rotary hook timing, and motor care.',
                0.0,
                'Free Access',
                '/static/media/student-inspection.jpg'
            ),
            (
                'protraining-1-correspondence',
                'ProTraining 1: Complete Home Correspondence Course',
                'Core Certification',
                'The renowned 16-lesson FSMI home study program. Master brand-agnostic diagnosis, hook-to-needle clearance, shuttle races, bobbin cases, and motor speed controllers.',
                699.0,
                'Flagship Home Study',
                '/static/media/technician-repair.jpg'
            ),
            (
                'protraining-2-computerized',
                'ProTraining 2: Advanced Electronic & Computerized Diagnostics',
                'Advanced Electronics',
                'Bridge mechanical gears with modern electronics. Covers motherboard diagnostics, stepper motors, optical encoder sensors, and LCD touchscreen assemblies.',
                499.0,
                'Computerized Systems',
                '/static/media/computerized-chassis.png'
            ),
            (
                'live-5-day-bench-companion',
                '5-Day Live Master Technician Bench Companion',
                'Live Workshop',
                'Supplemental training materials, workshop checklists, and tool schematics exclusively for graduates and attendees of our Temple, TX live bench immersion classes.',
                0.0,
                'Classroom Exclusive',
                '/static/media/live-class-bench.jpg'
            ),
            (
                'industrial-lockstitch-mastery',
                'Industrial & Walking Foot Lockstitch Mastery',
                'Commercial',
                'In-depth servicing for heavy-duty industrial sewing machines, compound needle feeds, walking feet, clutch/servo motors, and automated bartack systems.',
                399.0,
                'Heavy Duty',
                '/static/media/industrial-machine.png'
            )
        ]

        for slug, title, cat, desc, price, badge, thumb in courses_data:
            cur.execute('''
                INSERT INTO courses (slug, title, category, description, price, badge, thumbnail_url, published)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            ''', (slug, title, cat, desc, price, badge, thumb))

        conn.commit()

        # Seed Modules and Lessons for Course 1: Free Course
        cur.execute("SELECT id FROM courses WHERE slug = 'free-7-step-maintenance'")
        free_course_id = cur.fetchone()[0]

        cur.execute("INSERT INTO modules (course_id, title, sort_order) VALUES (?, 'Core Machine Care & Fundamentals', 1)", (free_course_id,))
        mod1_id = cur.lastrowid

        free_lessons = [
            ("Lesson 1: Anatomy of the Sewing Machine & Essential Tools", "Tour the casting, arm shaft, handwheel, and essential non-magnetic screwdrivers and gauges.", 12, 1, 1),
            ("Lesson 2: Cleaning the Shuttle Race & Bobbin Case", "How hardened lint and dried lubricant lock up mechanical movements, and proper brass brush techniques.", 15, 2, 0),
            ("Lesson 3: Needle-to-Hook Timing Demystified", "Understanding the universal loop-forming principle that governs 99% of all sewing machines.", 18, 3, 0),
            ("Lesson 4: Calibrating Upper & Lower Thread Tension", "Fixing bird's nests, looping underside stitches, and tension disc spring calibration.", 14, 4, 0),
            ("Lesson 5: Feed Dog Height & Material Transport", "Ensuring flat feeding without puckering fine fabrics or stalling on heavy denim seams.", 16, 5, 0),
            ("Lesson 6: Motor Drive Belts & Lubrication Chemistry", "Why 3-in-1 oil ruins machines, and the exact synthetic white oils and lithium greases to use.", 20, 6, 0),
            ("Lesson 7: The Master Diagnostic Checklist", "A printable 7-step checklist to systematically diagnose any machine that crosses your bench.", 15, 7, 0)
        ]
        for title, desc, dur, sort, is_prev in free_lessons:
            cur.execute('''
                INSERT INTO lessons (module_id, course_id, title, description, video_source, duration_mins, notes_md, is_preview, sort_order)
                VALUES (?, ?, ?, ?, 'smi-video-demo', ?, '### Bench Technician Notes\n\n* Keep non-magnetic tools handy.\n* Always turn handwheel toward you (counter-clockwise on standard machines).\n* Inspect hook tip under 10x magnification for burrs.', ?, ?)
            ''', (mod1_id, free_course_id, title, desc, dur, is_prev, sort))

        # Seed Modules and Lessons for Course 2: ProTraining 1 Correspondence Course (16 modules)
        cur.execute("SELECT id FROM courses WHERE slug = 'protraining-1-correspondence'")
        pro1_course_id = cur.fetchone()[0]

        pro1_modules = [
            ("Module A: Universal Machine Mechanics & Theory", [
                ("Module 1: The Physics of Stitch Formation", "Rotary vs. oscillating vs. transverse shuttle mechanics.", 25),
                ("Module 2: Complete Disassembly of Mechanical Castings", "Removing face plates, bed covers, and motor housings without damaging fasteners.", 35),
                ("Module 3: Needle Bar Rise & Loop Formation Timing", "Setting exact 2.0mm - 2.5mm rise after bottom dead center.", 40),
                ("Module 4: Hook Point Clearance to Needle Scarf", "Setting 0.05mm - 0.1mm clearance to prevent skipped stitches and needle strikes.", 30),
            ]),
            ("Module B: Tension, Feeding & Bobbin Systems", [
                ("Module 5: Rotary Hook vs. Oscillating Shuttle Synchronization", "Timing gears, eccentric cams, and drive belts.", 45),
                ("Module 6: Feed Dog Height, Stroke & Drop Calibration", "Aligning feed dogs flush with needle plate at correct stroke angles.", 30),
                ("Module 7: Upper Tension Release Mechanism & Check Spring", "Setting check spring travel and tension disc release pins.", 25),
                ("Module 8: Bobbin Case Latch, Springs & Thread Clearance", "Checking finger clearance for unrestricted thread passage.", 28),
            ]),
            ("Module C: Zig-Zag, Cam Timing & Presser Systems", [
                ("Module 9: Zig-Zag Bight Cam Timing & Center Needle Position", "Synchronizing needle pendulum swing with hook sweep.", 38),
                ("Module 10: Reverse Stitch Feed Balance Calibration", "Equalizing forward and reverse stitch length on utility/stretch cams.", 32),
                ("Module 11: Presser Bar Height & Alignment with Feed Dogs", "Setting 6mm clearance for standard presser foot lifting.", 25),
                ("Module 12: Bobbin Winder Assemblies & Auto-Stop Mechanism", "Tire friction, spindle engagement, and stop-motion clutch washers.", 22),
            ]),
            ("Module D: Electrical, Sergers & Professional Bench Operations", [
                ("Module 13: Foot Controllers, Carbon Piles & Electronic Speed Pedals", "Diagnosing hot pedals, dead spots, and resistor networks.", 35),
                ("Module 14: Universal Motor Brushes, Commutators & Belts", "Inspecting carbon brushes, cleaning copper armatures, and belt tensioning.", 40),
                ("Module 15: Introduction to 3/4-Thread Serger & Overlock Timing", "Upper and lower looper clearance, chaining, and feed differential.", 50),
                ("Module 16: Launching Your Bench Business: Pricing, Invoicing & Liability", "Charging $110/repair, intake inspections, and customer guarantees.", 45),
            ])
        ]

        sort_mod = 1
        for mod_title, lesson_list in pro1_modules:
            cur.execute("INSERT INTO modules (course_id, title, sort_order) VALUES (?, ?, ?)", (pro1_course_id, mod_title, sort_mod))
            m_id = cur.lastrowid
            sort_mod += 1

            sort_les = 1
            for l_title, l_desc, l_dur in lesson_list:
                cur.execute('''
                    INSERT INTO lessons (module_id, course_id, title, description, video_source, duration_mins, notes_md, is_preview, sort_order)
                    VALUES (?, ?, ?, ?, 'smi-video-demo', ?, '### Professional Workbench Blueprint\n\n* **Timing Tolerance:** 0.05mm clearance\n* **Lubrication:** High-viscosity synthetic grease on metal bevel gears only\n* **Safety:** Disconnect power cord before accessing internal motor wiring.', ?, ?)
                ''', (m_id, pro1_course_id, l_title, l_desc, l_dur, 1 if sort_les == 1 and sort_mod == 2 else 0, sort_les))
                sort_les += 1

        conn.commit()

        # Enroll demo student into Free Course and ProTraining 1
        cur.execute("SELECT id FROM users WHERE email = 'student@sewingmachinesinstitute.com'")
        student_id = cur.fetchone()[0]

        cur.execute('''
            INSERT OR IGNORE INTO enrollments (user_id, course_id, granted_by, status)
            VALUES (?, ?, 'manual_admin', 'active')
        ''', (student_id, free_course_id))

        cur.execute('''
            INSERT OR IGNORE INTO enrollments (user_id, course_id, granted_by, status)
            VALUES (?, ?, 'wix_migration', 'active')
        ''', (student_id, pro1_course_id))

        # Seed some progress
        cur.execute("SELECT id FROM lessons WHERE course_id = ? LIMIT 3", (free_course_id,))
        for row in cur.fetchall():
            cur.execute('''
                INSERT OR IGNORE INTO lesson_progress (user_id, lesson_id, course_id, completed, last_position_seconds)
                VALUES (?, ?, ?, 1, 600)
            ''', (student_id, row[0], free_course_id))

        conn.commit()

    conn.close()

if __name__ == '__main__':
    init_db()
    seed_db()
    print("Database initialized and seeded successfully!")
