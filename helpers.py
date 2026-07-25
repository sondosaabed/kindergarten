"""
helpers.py — shared lookup lists, calculations and small business-logic
functions used across the app.
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
    STATUS_NEW: "#FFB84D",     # amber — waiting on registration fee
    STATUS_ACTIVE: "#4CAF7D",  # green — active / paid
}


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
    Recomputed from payment history so it can never drift out of sync.
    """
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) AS c FROM payments WHERE registration_id = ? AND payment_for = ?",
        (registration_id, "رسوم تسجيل")
    )
    has_reg_fee = cur.fetchone()["c"] > 0
    return STATUS_ACTIVE if has_reg_fee else STATUS_NEW


def refresh_registration_status(conn, registration_id):
    new_status = compute_registration_status(conn, registration_id)
    conn.execute(
        "UPDATE registrations SET status = ? WHERE registration_id = ?",
        (new_status, registration_id)
    )
    conn.commit()
    return new_status


def format_money(amount):
    try:
        return f"{float(amount):,.2f}"
    except (TypeError, ValueError):
        return "0.00"
