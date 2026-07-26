"""
sections/dashboard.py — لوحة التحكم

Top-level KPIs, revenue trend, class distribution and recent activity.
Edit this file only to change what appears on the dashboard.
"""

import streamlit as st

import ui
import helpers as H


def render(conn):
    ui.section_header("📊", "لوحة التحكم", "نظرة سريعة وشاملة على أداء الروضة")

    total_students = ui.df(conn, "SELECT COUNT(*) c FROM students").iloc[0]['c']
    total_teachers = ui.df(conn, "SELECT COUNT(*) c FROM teachers").iloc[0]['c']
    total_classes = ui.df(conn, "SELECT COUNT(*) c FROM classes").iloc[0]['c']
    total_revenue = ui.df(conn, "SELECT COALESCE(SUM(amount),0) s FROM payments").iloc[0]['s']
    pending = ui.df(conn, f"SELECT COUNT(*) c FROM registrations WHERE status = '{H.STATUS_NEW}'").iloc[0]['c']

    c1, c2, c3, c4, c5 = st.columns(5)
    ui.kpi(c1, "🎒", "إجمالي الطلاب", total_students, "#E9F5EC", "#219044")
    ui.kpi(c2, "👩‍🏫", "المعلمون", total_teachers, "#FBF3E3", "#D7A431")
    ui.kpi(c3, "🏷️", "الصفوف", total_classes, "#E9F5EC", "#163D22")
    ui.kpi(c4, "💰", "إجمالي المقبوضات", H.format_money(total_revenue), "#FDECEC", "#E62031")
    ui.kpi(c5, "⏳", "بانتظار رسوم التسجيل", pending, "#FBF3E3", "#B4790C")

    st.write("")
    left, right = st.columns([1.3, 1])

    with left:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("##### 📈 المقبوضات آخر 6 أشهر")
        rev = ui.df(conn, """
            SELECT strftime('%Y-%m', payment_date) AS الشهر, SUM(amount) AS المبلغ
            FROM payments
            GROUP BY الشهر
            ORDER BY الشهر DESC
            LIMIT 6
        """).sort_values("الشهر")
        if rev.empty:
            ui.empty_state("لا توجد مقبوضات مسجلة بعد.")
        else:
            st.bar_chart(rev.set_index("الشهر"))
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("##### 🏷️ توزيع الطلاب على الصفوف")
        dist = ui.df(conn, """
            SELECT (c.class_type || ' ' || c.section) AS الصف, COUNT(r.registration_id) AS العدد
            FROM classes c
            LEFT JOIN registrations r ON r.class_id = c.class_id
                AND r.year_id = (SELECT year_id FROM academic_years ORDER BY start_date DESC LIMIT 1)
            GROUP BY c.class_id
        """)
        if dist.empty:
            ui.empty_state("لا توجد صفوف بعد.")
        else:
            st.bar_chart(dist.set_index("الصف"))
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
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
    st.markdown("</div>", unsafe_allow_html=True)
