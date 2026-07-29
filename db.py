"""
db.py — Database layer for the Kindergarten Management System
نظام قاعدة البيانات لإدارة الروضة
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st


def get_connection():
    """
    Connects to PostgreSQL using secrets configured in Streamlit Cloud (.streamlit/secrets.toml)
    or falls back to an environment variable DATABASE_URL.
    """
    db_url = None

    # 1. Check Streamlit secrets first
    if "postgres" in st.secrets and "url" in st.secrets["postgres"]:
        db_url = st.secrets["postgres"]["url"]
    # 2. Check system environment variable second
    elif "DATABASE_URL" in os.environ:
        db_url = os.environ["DATABASE_URL"]

    # Fail explicitly if no database configuration is present
    if not db_url:
        raise ValueError(
            "Database URL not configured! Please check your Streamlit Cloud secrets configuration."
        )

    # Automatically append sslmode=require for cloud PostgreSQL hosts if missing
    if "sslmode" not in db_url:
        separator = "&" if "?" in db_url else "?"
        db_url = f"{db_url}{separator}sslmode=require"

    conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    conn.autocommit = False
    return conn


def _safe_add_column(cursor, table, column_def):
    """
    Add a column if it doesn't already exist.
    Uses PostgreSQL native 'IF NOT EXISTS' to avoid transaction-aborting errors.
    """
    cursor.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {column_def};")


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    try:
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
            );
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
            );
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
            );
        ''')

        # 4. الصف — Classes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS classes (
                class_id SERIAL PRIMARY KEY,
                class_type TEXT NOT NULL,
                section TEXT NOT NULL,
                class_name TEXT,
                teacher_id TEXT,
                UNIQUE(class_type, section),
                FOREIGN KEY (teacher_id) REFERENCES teachers (national_id) ON DELETE SET NULL
            );
        ''')

        # 5. السنة الدراسية — Academic Years
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS academic_years (
                year_id TEXT PRIMARY KEY,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                cohort_name TEXT
            );
        ''')

        # 6. التسجيل — Registrations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registrations (
                registration_id SERIAL PRIMARY KEY,
                student_id TEXT NOT NULL,
                class_id INTEGER NOT NULL,
                year_id TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'مسجل جديد',
                registration_date TEXT,
                FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE,
                FOREIGN KEY (class_id) REFERENCES classes (class_id),
                FOREIGN KEY (year_id) REFERENCES academic_years (year_id)
            );
        ''')
        _safe_add_column(cursor, "registrations", "registration_date TEXT")

        cursor.execute('''
            CREATE UNIQUE INDEX IF NOT EXISTS uniq_student_year
            ON registrations(student_id, year_id);
        ''')

        # 7. الدفعات المالية — Payments
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                receipt_number SERIAL PRIMARY KEY,
                registration_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_date TEXT NOT NULL,
                payment_method TEXT DEFAULT 'كاش',
                payer_name TEXT NOT NULL,
                payment_for TEXT NOT NULL,
                payment_for_other TEXT,
                FOREIGN KEY (registration_id) REFERENCES registrations (registration_id) ON DELETE CASCADE
            );
        ''')

        # Indexes for fast lookups
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_father ON students(father_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_reg_student ON registrations(student_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_reg_class ON registrations(class_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_reg_year ON registrations(year_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pay_reg ON payments(registration_id);")

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    init_db()
    print("PostgreSQL database structure created / verified successfully.")