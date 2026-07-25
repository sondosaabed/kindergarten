"""
db.py — Database layer for the Kindergarten Management System
نظام قاعدة البيانات لإدارة الروضة

Handles connection + schema creation + light, non-destructive migrations
so existing data in school_data.db is never wiped.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "school_data.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def _safe_add_column(cursor, table, column_def):
    """Add a column if it doesn't already exist. Never destroys data."""
    col_name = column_def.split()[0]
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column_def}")
    except sqlite3.OperationalError as e:
        if "duplicate column" not in str(e).lower():
            raise


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. ولي الأمر — Parents
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parents (
            father_id TEXT PRIMARY KEY,
            mother_id TEXT,
            father_name TEXT NOT NULL,
            mother_name TEXT NOT NULL,
            father_job TEXT NOT NULL,
            mother_job TEXT NOT NULL,
            mother_work_type TEXT,
            father_id_type TEXT NOT NULL,
            mother_id_type TEXT NOT NULL,
            address TEXT NOT NULL,
            landline TEXT,
            status_refugee TEXT NOT NULL,
            father_work_phone TEXT,
            mother_work_phone TEXT,
            father_mobile TEXT NOT NULL,
            mother_mobile TEXT NOT NULL,
            emergency_contact TEXT,
            marital_status TEXT NOT NULL,
            created_at TEXT
        )
    ''')
    _safe_add_column(cursor, "parents", "emergency_contact_name TEXT")
    _safe_add_column(cursor, "parents", "emergency_contact_phone TEXT")
    _safe_add_column(cursor, "parents", "created_at TEXT")

    # 2. الطالب — Students
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            birth_date TEXT NOT NULL,
            birth_place TEXT NOT NULL,
            gender TEXT NOT NULL,
            id_type TEXT NOT NULL,
            nationality TEXT NOT NULL,
            has_medical_condition INTEGER NOT NULL DEFAULT 0,
            medical_details TEXT,
            father_id TEXT NOT NULL,
            created_at TEXT,
            FOREIGN KEY (father_id) REFERENCES parents (father_id) ON DELETE CASCADE
        )
    ''')
    _safe_add_column(cursor, "students", "created_at TEXT")

    # 3. المعلم — Teachers
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            national_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            salary REAL NOT NULL,
            mobile TEXT NOT NULL,
            address TEXT NOT NULL,
            hire_date TEXT NOT NULL,
            experience_years INTEGER NOT NULL,
            degree TEXT NOT NULL,
            specialization TEXT
        )
    ''')

    # 4. الصف — Classes  (class_type + section = composite natural key)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            class_id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_type TEXT NOT NULL,
            section TEXT NOT NULL,
            class_name TEXT,
            teacher_id TEXT,
            UNIQUE(class_type, section),
            FOREIGN KEY (teacher_id) REFERENCES teachers (national_id) ON DELETE SET NULL
        )
    ''')

    # 5. السنة الدراسية — Academic Years
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS academic_years (
            year_id TEXT PRIMARY KEY,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            cohort_name TEXT
        )
    ''')

    # 6. التسجيل — Registrations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            registration_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            class_id INTEGER NOT NULL,
            year_id TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'مسجل جديد',
            registration_date TEXT,
            FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE,
            FOREIGN KEY (class_id) REFERENCES classes (class_id),
            FOREIGN KEY (year_id) REFERENCES academic_years (year_id)
        )
    ''')
    _safe_add_column(cursor, "registrations", "registration_date TEXT")
    cursor.execute('''
        CREATE UNIQUE INDEX IF NOT EXISTS uniq_student_year
        ON registrations(student_id, year_id)
    ''')

    # 7. الدفعات المالية — Payments
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            receipt_number INTEGER PRIMARY KEY AUTOINCREMENT,
            registration_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_date TEXT NOT NULL,
            payment_method TEXT DEFAULT 'كاش',
            payer_name TEXT NOT NULL,
            payment_for TEXT NOT NULL,
            payment_for_other TEXT,
            FOREIGN KEY (registration_id) REFERENCES registrations (registration_id) ON DELETE CASCADE
        )
    ''')

    # Helpful indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_father ON students(father_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reg_student ON registrations(student_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reg_class ON registrations(class_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reg_year ON registrations(year_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pay_reg ON payments(registration_id)")

    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
    print("Database structure created / verified successfully.")
