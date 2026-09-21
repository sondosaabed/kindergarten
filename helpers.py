"""
helpers.py — shared lookup lists, calculations and small business-logic
functions used across the app.
Updated for PostgreSQL `%s` placeholders.
"""

from datetime import datetime, date

# ---------------------------------------------------------------- lookups --
GENDERS = ["أنثى", "ذكر"]

STUDENT_ID_TYPES = ["ضفة", "قدس", "آخر"]
PARENT_ID_TYPES = ["ضفة", "غزة", "قدس"]

NATIONALITIES = ["فلسطيني", "أردني", "مصري", "سوري", "أخرى"]

RESIDENCY_STATUS = ["مواطن", "لاجئ"]
MARITAL_STATUS = ["قائم", "منفصل", "مطلق", "أرمل"]
MOTHER_JOB_STATUS = ["ربة منزل", "تعمل"]

DEGREES = ["دبلوم", "بكالوريوس", "ماجستير", "دكتوراه", "أخرى"]

CLASS_TYPES = ["تمهيدي", "بستان"]
SECTIONS = ["أ", "ب", "ج", "د"]

PAYMENT_FOR = ["رسوم تسجيل", "أقساط تعليمية", "آخر"]
PAYMENT_METHODS = ["كاش"]

STATUS_NEW = "مسجل جديد"
STATUS_ACTIVE = "منتظم"

STATUS_COLORS = {
    STATUS_NEW: "#D7A431",     # gold — waiting on registration fee
    STATUS_ACTIVE: "#219044",  # brand green — active / paid
}

# Total tuition owed per student per academic year, registration fee included.
ANNUAL_TUITION = 3500.0
TUITION_PAYMENT_TYPES = ("رسوم تسجيل", "أقساط تعليمية")


# ------------------------------------------------------------------ dates --
def calculate_age(birth_date_str):
    """Return a human string like '٣ سنوات و٤ أشهر' given YYYY-MM-DD."""
    if not birth_date_str:
        return "—"
    try:
        b = datetime.strptime(str(birth_date_str), "%Y-%m-%d").date()
    except ValueError:
        return "—"
    today = date.today()
    years = today.year - b.year
    months = today.month - b.month
    if today.day < b.day:
        months -= 1
    if months < 0:
        years -= 1
        months += 12
    if years < 0:
        return "—"
    return f"{years} سنة و {months} شهر" if years > 0 else f"{months} شهر"


def today_str():
    return datetime.today().strftime('%Y-%m-%d')


def now_str():
    return datetime.today().strftime('%Y-%m-%d %H:%M:%S')


# --------------------------------------------------------------- business --
def compute_registration_status(conn, registration_id):
    """
    A registration starts as 'مسجل جديد' and becomes 'منتظم' the moment
    a registration-fee payment (رسوم تسجيل) has been recorded against it.
    Updated for PostgreSQL %s placeholders.
    """
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) AS c FROM payments WHERE registration_id = %s AND payment_for = %s",
        (registration_id, "رسوم تسجيل")
    )
    res = cur.fetchone()
    cur.close()
    has_reg_fee = (res["c"] > 0) if res else False
    return STATUS_ACTIVE if has_reg_fee else STATUS_NEW

def refresh_registration_status(conn, registration_id):
    """Refreshes and updates registration status based on payments."""
    paid = compute_paid_toward_tuition(conn, registration_id)
    new_status = STATUS_ACTIVE if paid > 0 else STATUS_NEW

    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE registrations 
            SET status = %s 
            WHERE registration_id = %s AND status != %s
        """, (new_status, registration_id, STATUS_WITHDRAWN))
        conn.commit()
        cur.close()
    except Exception:
        conn.rollback()

    return new_status


def compute_paid_toward_tuition(conn, registration_id):
    """Computes total payments made toward registration or tuition fees for a registration ID."""
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM payments
            WHERE registration_id = %s
              AND payment_for IN ('رسوم تسجيل', 'أقساط تعليمية')
        """, (registration_id,))
        res = cur.fetchone()
        cur.close()
        if res is None:
            return 0.0
        val = res['total'] if isinstance(res, dict) else res[0]
        return float(val) if val is not None else 0.0
    except Exception:
        return 0.0


def compute_remaining_balance(conn, registration_id):
    """Computes the remaining tuition balance dynamically based on the registration's custom annual tuition."""
    paid = compute_paid_toward_tuition(conn, registration_id)
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT COALESCE(annual_tuition, 3500.0) AS annual_tuition 
            FROM registrations 
            WHERE registration_id = %s
        """, (registration_id,))
        res = cur.fetchone()
        cur.close()
        
        if res is None:
            tuition = 3500.0
        else:
            tuition = float(res['annual_tuition'] if isinstance(res, dict) else res[0])
    except Exception:
        tuition = 3500.0

    return max(0.0, tuition - paid)

def format_money(amount):
    try:
        return f"{float(amount):,.2f}"
    except (TypeError, ValueError):
        return "0.00"


def current_month_str():
    """Returns current month in YYYY-MM format (e.g. 2026-09)."""
    return datetime.now().strftime("%Y-%m-%d")[:7]

def get_arabic_month_name(yyyy_mm):
    """Converts '2026-09' to Arabic Month Name."""
    try:
        year, month = yyyy_mm.split("-")
        months_ar = [
            "كانون الثاني (1)", "شباط (2)", "آذار (3)", "نيسان (4)",
            "أيار (5)", "حزيران (6)", "تموز (7)", "آب (8)",
            "أيلول (9)", "تشرين الأول (10)", "تشرين الثاني (11)", "كانون الأول (12)"
        ]
        return f"{months_ar[int(month) - 1]} {year}"
    except Exception:
        return yyyy_mm