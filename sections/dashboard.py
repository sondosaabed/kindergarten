"""
sections/dashboard.py — لوحة التحكم (الرئيسية)

Optimized for high performance with batch SQL queries.
Top-level KPIs, revenue trend, class distribution and recent activity.
"""

import streamlit as st

import ui
import helpers as H


def render(conn):
    ui.section_header("📊", "الرئيسية", "نظرة سريعة وشاملة على أداء الروضة")

    # Single batch query to calculate key counts and sums in one round-trip
    summary_df = ui.df(conn, """
        SELECT 
            (SELECT COUNT(*) FROM students) AS total_students,
            (SELECT COUNT(*) FROM teachers) AS total_teachers,
            (SELECT COUNT(*) FROM classes) AS total_classes,
            (SELECT COALESCE(SUM(amount), 0) FROM payments) AS total_revenue,
            (SELECT COUNT(*) FROM registrations WHERE status = %s) AS pending_regs
    """, (H.STATUS_NEW,))

    if not summary_df.empty:
        row = summary_df.iloc[0]
        total_students = row['total_students']
        total_teachers = row['total_teachers']
        total_classes = row['total_classes']
        total_revenue = row['total_revenue']
        pending = row['pending_regs']
    else:
        total_students = total_teachers = total_classes = pending = 0
        total_revenue = 0.0

    # Optimized SQL aggregation to calculate outstanding balances directly in DB
    outstanding_df = ui.df(conn, """
        SELECT COALESCE(SUM(GREATEST(0, %s - COALESCE(p.paid, 0))), 0) AS total_outstanding
        FROM registrations r
        LEFT JOIN (
            SELECT registration_id, SUM(amount) AS paid
            FROM payments
            WHERE payment_for IN ('رسوم تسجيل', 'أقساط تعليمية')
            GROUP BY registration_id
        ) p ON p.registration_id = r.registration_id
        WHERE r.year_id = (SELECT year_id FROM academic_years ORDER BY start_date DESC LIMIT 1)
    """, (H.ANNUAL_TUITION,))
    
    total_outstanding = outstanding_df.iloc[0]['total_outstanding'] if not outstanding_df.empty else 0.0

    # Render KPI Cards
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    ui.kpi(c1, "🎒", "إجمالي الطلاب", total_students, "#E9F5EC", "#219044")
    ui.kpi(c2, "👩‍🏫", "المعلمون", total_teachers, "#FBF3E3", "#D7A431")
    ui.kpi(c3, "🏷️", "الصفوف", total_classes, "#E9F5EC", "#163D22")
    ui.kpi(c4, "💰", "إجمالي المقبوضات", H.format_money(total_revenue), "#FDECEC", "#E62031")
    ui.kpi(c5, "⏳", "بانتظار رسوم التسجيل", pending, "#FBF3E3", "#B4790C")
    ui.kpi(c6, "🧾", "إجمالي المتبقي (السنة الحالية)", H.format_money(total_outstanding), "#FDECEC", "#E62031")

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
            """).sort_values("الشهر")
            if rev.empty:
                ui.empty_state("لا توجد مقبوضات مسجلة بعد.")
            else:
                st.bar_chart(rev.set_index("الشهر"))

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