"""
db.py — Database initialization and connection management.
Uses st.cache_resource to maintain a persistent connection to PostgreSQL/Supabase.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st


@st.cache_resource
def get_connection():
    """
    Returns a cached PostgreSQL database connection.
    st.cache_resource ensures the TCP connection to Supabase stays alive
    and is reused across page reruns instead of reconnecting on every click.
    """
    if "postgres" in st.secrets:
        conn = psycopg2.connect(
            st.secrets["postgres"]["url"],
            cursor_factory=RealDictCursor
        )
    else:
        conn = psycopg2.connect(
            host="YOUR_SUPABASE_HOST",
            database="postgres",
            user="postgres",
            password="YOUR_PASSWORD",
            port="5432",
            cursor_factory=RealDictCursor
        )
    
    conn.autocommit = True
    return conn


def init_db():
    """
    Ensures required PostgreSQL tables exist on startup.
    Runs fast schema checks.
    """
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS academic_years (
                year_id VARCHAR(20) PRIMARY KEY,
                start_date DATE,
                end_date DATE,
                cohort_name VARCHAR(100)
            );

            CREATE TABLE IF NOT EXISTS teachers (
                national_id VARCHAR(20) PRIMARY KEY,
                full_name VARCHAR(100) NOT NULL,
                salary NUMERIC(10, 2) DEFAULT 0.00,
                mobile VARCHAR(20),
                address TEXT,
                hire_date DATE,
                experience_years INT DEFAULT 0,
                degree VARCHAR(50),
                specialization VARCHAR(100)
            );

            CREATE TABLE IF NOT EXISTS classes (
                class_id SERIAL PRIMARY KEY,
                class_type VARCHAR(50) NOT NULL,
                section VARCHAR(10) NOT NULL,
                class_name VARCHAR(100),
                teacher_id VARCHAR(20) REFERENCES teachers(national_id) ON DELETE SET NULL,
                UNIQUE(class_type, section)
            );

            CREATE TABLE IF NOT EXISTS parents (
                father_id VARCHAR(20) PRIMARY KEY,
                mother_id VARCHAR(20),
                father_name VARCHAR(100) NOT NULL,
                mother_name VARCHAR(100),
                father_job VARCHAR(100),
                mother_job VARCHAR(100),
                mother_work_type VARCHAR(100),
                father_id_type VARCHAR(50),
                mother_id_type VARCHAR(50),
                address TEXT,
                landline VARCHAR(20),
                status_refugee VARCHAR(50),
                father_work_phone VARCHAR(20),
                mother_work_phone VARCHAR(20),
                father_mobile VARCHAR(20),
                mother_mobile VARCHAR(20),
                emergency_contact_name VARCHAR(100),
                emergency_contact_phone VARCHAR(20),
                marital_status VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS students (
                student_id VARCHAR(20) PRIMARY KEY,
                full_name VARCHAR(100) NOT NULL,
                birth_date DATE,
                birth_place VARCHAR(100),
                gender VARCHAR(10),
                id_type VARCHAR(50),
                nationality VARCHAR(50),
                has_medical_condition INT DEFAULT 0,
                medical_details TEXT,
                father_id VARCHAR(20) REFERENCES parents(father_id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS registrations (
                registration_id SERIAL PRIMARY KEY,
                student_id VARCHAR(20) REFERENCES students(student_id) ON DELETE CASCADE,
                class_id INT REFERENCES classes(class_id) ON DELETE RESTRICT,
                year_id VARCHAR(20) REFERENCES academic_years(year_id) ON DELETE RESTRICT,
                status VARCHAR(50) NOT NULL,
                registration_date DATE DEFAULT CURRENT_DATE,
                annual_tuition NUMERIC(10, 2) DEFAULT 3500.00,
                UNIQUE(student_id, year_id)
            );

            CREATE TABLE IF NOT EXISTS teacher_payments (
                payment_id SERIAL PRIMARY KEY,
                national_id VARCHAR(20) REFERENCES teachers(national_id) ON DELETE CASCADE,
                amount NUMERIC(10, 2) NOT NULL,
                payment_date DATE DEFAULT CURRENT_DATE,
                salary_month VARCHAR(7) NOT NULL,
                base_salary NUMERIC(10, 2) DEFAULT 0.00,
                bonus NUMERIC(10, 2) DEFAULT 0.00,
                deductions NUMERIC(10, 2) DEFAULT 0.00,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            ALTER TABLE registrations 
            ADD COLUMN IF NOT EXISTS annual_tuition NUMERIC(10, 2) DEFAULT 3500.00;

            CREATE TABLE IF NOT EXISTS payments (
                receipt_number SERIAL PRIMARY KEY,
                registration_id INT REFERENCES registrations(registration_id) ON DELETE CASCADE,
                amount NUMERIC(10, 2) NOT NULL,
                payment_date DATE DEFAULT CURRENT_DATE,
                payment_method VARCHAR(50) DEFAULT 'كاش',
                payer_name VARCHAR(100),
                payment_for VARCHAR(50),
                payment_for_other TEXT
            );

            -- -------------------------------------------------------------
            -- NEW: OPERATIONAL EXPENSES TABLE
            -- -------------------------------------------------------------
            CREATE TABLE IF NOT EXISTS expenses (
                expense_id SERIAL PRIMARY KEY,
                expense_date DATE DEFAULT CURRENT_DATE,
                category VARCHAR(100) NOT NULL,
                amount NUMERIC(10, 2) NOT NULL,
                payment_method VARCHAR(50) DEFAULT 'كاش',
                payee VARCHAR(150),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- -------------------------------------------------------------
            -- NEW: CAPITAL ASSETS & EQUIPMENT TABLE
            -- -------------------------------------------------------------
            CREATE TABLE IF NOT EXISTS assets (
                asset_id SERIAL PRIMARY KEY,
                purchase_date DATE DEFAULT CURRENT_DATE,
                item_name VARCHAR(150) NOT NULL,
                category VARCHAR(100) NOT NULL,
                quantity INT DEFAULT 1,
                unit_cost NUMERIC(10, 2) NOT NULL,
                total_cost NUMERIC(10, 2) NOT NULL,
                condition_status VARCHAR(50) DEFAULT 'ممتازة',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)