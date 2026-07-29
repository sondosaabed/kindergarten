"""
sections/dashboard.py — لوحة التحكم (الرئيسية)

Optimized performance with explicit Arabic KPI binding and safe positional metric fetches.
"""

import pandas as pd
import streamlit as st
import ui
import helpers as H


def _safe_int(df):
    if not df.empty and pd.notna(df.iloc[0, 0]):
        try:
            return int(df.iloc[0, 0])
        except (ValueError, TypeError):
            return 0
    return 0


def _safe_float(df):
    if not df.empty and pd.notna(df.iloc[0, 0]):
        try:
            return float(df.iloc[0, 0])
        except (ValueError, TypeError):
            return 0.0
    return 0.0


def render(conn):
    ui.section_header("📊", "الرئيسية", "نظرة سريعة وشاملة على أداء الروضة")

    # Fetch aggregate counts safely
    total_students = _safe_int(ui.df(conn, "SELECT COUNT(*) FROM students"))
    total_teachers = _safe_int(ui.df(conn, "SELECT COUNT(*) FROM teachers"))
    total_classes = _safe_int(ui.df(conn, "SELECT COUNT(*) FROM classes"))
    total_revenue = _safe_float(ui.df(conn, "SELECT COALESCE(SUM(amount), 0) FROM payments"))
    pending = _safe_int(ui.df(conn, "SELECT COUNT(*) FROM registrations WHERE status = %s", (H.STATUS_NEW,)))

    # Calculate remaining balance using PostgreSQL safely
    outstanding_df = ui.df(conn, """
        SELECT COALESCE(SUM(GREATEST(0, %s - COALESCE(p.paid, 0))), 0)
        FROM registrations r
        LEFT JOIN (
            SELECT registration_id, SUM(amount) AS paid
            FROM payments
            WHERE payment_for IN ('رسوم تسجيل', 'أقساط تعليمية')
            GROUP BY registration_id
        ) p ON p.registration_id = r.registration_id
        WHERE r.year_id = (SELECT year_id FROM academic_years ORDER BY start_date DESC LIMIT 1)
    """, (H.ANNUAL_TUITION,))

    total_outstanding = _safe_float(outstanding_df)

    # Render KPI Cards in Arabic
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    ui.kpi(c1, "🎒", "إجمالي الطلاب", total_students, "#E9F5EC", "#219044")
    ui.kpi(c2, "👩‍🏫", "المعلمون", total_teachers, "#FBF3E3", "#D7A431")
    ui.kpi(c3, "🏷️", "الصفوف", total_classes, "#E9F5EC", "#163D22")
    ui.kpi(c4, "💰", "إجمالي المقبوضات", H.format_money(total_revenue), "#FDECEC", "#E62031")
    ui.kpi(c5, "⏳", "بانتظار رسوم التسجيل", pending, "#FBF3E3", "#B4790C")
    ui.kpi(c6, "🧾", "إجمالي المتبقي", H.format_money(total_outstanding), "#FDECEC", "#E62031")

    st.write("")
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