"""
sections/dashboard.py — لوحة التحكم (الرئيسية)

Uses direct cursor evaluation for KPI values to prevent pandas DataFrame conversion errors.
KPI cards are arranged in a 3x2 grid to prevent horizontal overflow when the sidebar opens.
"""

import streamlit as st
import ui
import helpers as H


def _get_scalar(conn, query, params=()):
    """Executes a scalar SQL query directly via cursor safely."""
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        res = cur.fetchone()
        cur.close()
        if res is None:
            return 0
        if isinstance(res, dict):
            val = list(res.values())[0]
        elif isinstance(res, (tuple, list)):
            val = res[0]
        else:
            val = res
        return val if val is not None else 0
    except Exception:
        return 0


def render(conn):
    ui.section_header("📊", "الرئيسية", "نظرة سريعة وشاملة على أداء الروضة")

    # Fetch KPI metrics directly
    total_students = int(_get_scalar(conn, "SELECT COUNT(*) FROM students"))
    total_teachers = int(_get_scalar(conn, "SELECT COUNT(*) FROM teachers"))
    total_classes = int(_get_scalar(conn, "SELECT COUNT(*) FROM classes"))
    total_revenue = float(_get_scalar(conn, "SELECT COALESCE(SUM(amount), 0) FROM payments"))
    pending = int(_get_scalar(conn, "SELECT COUNT(*) FROM registrations WHERE status = %s", (H.STATUS_NEW,)))

    total_outstanding = float(_get_scalar(conn, """
        SELECT COALESCE(SUM(GREATEST(0, %s - COALESCE(p.paid, 0))), 0)
        FROM registrations r
        LEFT JOIN (
            SELECT registration_id, SUM(amount) AS paid
            FROM payments
            WHERE payment_for IN ('رسوم تسجيل', 'أقساط تعليمية')
            GROUP BY registration_id
        ) p ON p.registration_id = r.registration_id
        WHERE r.year_id = (SELECT year_id FROM academic_years ORDER BY start_date DESC LIMIT 1)
    """, (H.ANNUAL_TUITION,)))

    # ------------------------------------------------------------------
    # KPI Grid Row 1: Key Operational Counts
    # ------------------------------------------------------------------
    r1_col1, r1_col2, r1_col3 = st.columns(3)
    ui.kpi(r1_col1, "🎒", "إجمالي الطلاب", total_students, bg="#E9F5EC", fg="#219044")
    ui.kpi(r1_col2, "👩‍🏫", "المعلمون", total_teachers, bg="#F0F9FF", fg="#0284C7")
    ui.kpi(r1_col3, "🏷️", "الصفوف", total_classes, bg="#F5F3FF", fg="#7C3AED")

    st.write("")  # Vertical spacer between rows

    # ------------------------------------------------------------------
    # KPI Grid Row 2: Financial Metrics & Pending Registrations
    # ------------------------------------------------------------------
    r2_col1, r2_col2, r2_col3 = st.columns(3)
    ui.kpi(r2_col1, "💰", "إجمالي المقبوضات", H.format_money(total_revenue), bg="#ECFDF5", fg="#059669")
    ui.kpi(r2_col2, "⏳", "بانتظار التسجيل", pending, bg="#FEF3C7", fg="#D97706")
    ui.kpi(r2_col3, "🧾", "إجمالي المتبقي", H.format_money(total_outstanding), bg="#FFE4E6", fg="#E11D48")

    st.write("")
    
    # ------------------------------------------------------------------
    # Charts Section
    # ------------------------------------------------------------------
    left, right = st.columns([1.3, 1])

    with left:
        with st.container(border=True):
            st.markdown("##### 📈 المقبوضات آخر 6 أشهر")
            rev = ui.df(conn, """
                SELECT TO_CHAR(payment_date::date, 'YYYY-MM') AS "الشهر", SUM(amount) AS "المبلغ"
                FROM payments
                GROUP BY TO_CHAR(payment_date::date, 'YYYY-MM')
                ORDER BY TO_CHAR(payment_date::date, 'YYYY-MM') DESC
                LIMIT 6
            """)
            if rev.empty:
                ui.empty_state("لا توجد مقبوضات مسجلة بعد.")
            else:
                st.bar_chart(rev.sort_values("الشهر").set_index("الشهر"))

    with right:
        with st.container(border=True):
            st.markdown("##### 🏷️ توزيع الطلاب على الصفوف")
            dist = ui.df(conn, """
                SELECT (c.class_type || ' ' || c.section) AS "الصف", COUNT(r.registration_id) AS "العدد"
                FROM classes c
                LEFT JOIN registrations r ON r.class_id = c.class_id
                    AND r.year_id = (SELECT year_id FROM academic_years ORDER BY start_date DESC LIMIT 1)
                GROUP BY c.class_id, c.class_type, c.section
            """)
            if dist.empty:
                ui.empty_state("لا توجد صفوف بعد.")
            else:
                st.bar_chart(dist.set_index("الصف"))

    # ------------------------------------------------------------------
    # Recent Activity Table
    # ------------------------------------------------------------------
    with st.container(border=True):
        st.markdown("##### 🕓 آخر عمليات التسجيل")
        recent = ui.df(conn, """
            SELECT s.full_name AS "اسم الطالب", (c.class_type || ' ' || c.section) AS "الصف",
                   r.year_id AS "السنة الدراسية", r.status AS "الحالة"
            FROM registrations r
            JOIN students s ON s.student_id = r.student_id
            JOIN classes c ON c.class_id = r.class_id
            ORDER BY r.registration_id DESC LIMIT 8
        """)
        if recent.empty:
            ui.empty_state("لا توجد تسجيلات بعد.")
        else:
            st.dataframe(recent, use_container_width=True, hide_index=True)