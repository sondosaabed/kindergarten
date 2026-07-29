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
    new_status = compute_registration_status(conn, registration_id)
    cur = conn.cursor()
    cur.execute(
        "UPDATE registrations SET status = %s WHERE registration_id = %s",
        (new_status, registration_id)
    )
    conn.commit()
    cur.close()
    return new_status


def compute_paid_toward_tuition(conn, registration_id):
    """Sum of payments that count toward the yearly tuition (registration
    fee + installments) — excludes 'آخر' (miscellaneous) payments."""
    cur = conn.cursor()
    placeholders = ",".join("%s" for _ in TUITION_PAYMENT_TYPES)
    cur.execute(
        f"SELECT COALESCE(SUM(amount),0) AS s FROM payments "
        f"WHERE registration_id = %s AND payment_for IN ({placeholders})",
        (registration_id, *TUITION_PAYMENT_TYPES)
    )
    res = cur.fetchone()
    cur.close()
    return float(res["s"]) if res else 0.0


def compute_remaining_balance(conn, registration_id):
    """How much of the ANNUAL_TUITION is still owed for this registration."""
    paid = compute_paid_toward_tuition(conn, registration_id)
    return max(ANNUAL_TUITION - paid, 0.0)


def format_money(amount):
    try:
        return f"{float(amount):,.2f}"
    except (TypeError, ValueError):
        return "0.00"