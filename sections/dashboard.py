"""
sections/dashboard.py — لوحة التحكم (الرئيسية)

Top-level KPIs, revenue trend, class distribution and recent activity.
Updated for PostgreSQL / Supabase connection syntax.
"""

import streamlit as st

import ui
import helpers as H


def render(conn):
    ui.section_header("📊", "الرئيسية", "نظرة سريعة وشاملة على أداء الروضة")

    # Fetch KPI metrics safely
    df_st = ui.df(conn, "SELECT COUNT(*) AS c FROM students")
    total_students = df_st.iloc[0]['c'] if not df_st.empty else 0

    df_tc = ui.df(conn, "SELECT COUNT(*) AS c FROM teachers")
    total_teachers = df_tc.iloc[0]['c'] if not df_tc.empty else 0

    df_cl = ui.df(conn, "SELECT COUNT(*) AS c FROM classes")
    total_classes = df_cl.iloc[0]['c'] if not df_cl.empty else 0

    df_rev = ui.df(conn, "SELECT COALESCE(SUM(amount), 0) AS s FROM payments")
    total_revenue = df_rev.iloc[0]['s'] if not df_rev.empty else 0.0

    df_pen = ui.df(
        conn,
        "SELECT COUNT(*) AS c FROM registrations WHERE status = %s",
        (H.STATUS_NEW,)
    )
    pending = df_pen.iloc[0]['c'] if not df_pen.empty else 0

    # Outstanding balance across every registration in the latest academic year
    latest_year_regs = ui.df(conn, """
        SELECT registration_id FROM registrations
        WHERE year_id = (SELECT year_id FROM academic_years ORDER BY start_date DESC LIMIT 1)
    """)
    total_outstanding = sum(
        H.compute_remaining_balance(conn, int(rid)) for rid in latest_year_regs['registration_id']
    ) if not latest_year_regs.empty else 0.0

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
            # PostgreSQL syntax: TO_CHAR instead of strftime
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