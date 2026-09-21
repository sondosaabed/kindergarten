"""
sections/dashboard.py — لوحة التحكم (الرئيسية)
"""

import streamlit as st
import ui
import helpers as H
import plotly.express as px
from datetime import datetime


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
    ui.section_header("📊", "الرئيسية", "نظرة سريعة وشاملة على أداء الروضة والمالية")

    current_month = datetime.now().strftime("%Y-%m")

    # Fetch KPI metrics directly
    total_students = int(_get_scalar(conn, "SELECT COUNT(*) FROM students"))
    total_teachers = int(_get_scalar(conn, "SELECT COUNT(*) FROM teachers"))
    total_classes = int(_get_scalar(conn, "SELECT COUNT(*) FROM classes"))
    total_revenue = float(_get_scalar(conn, "SELECT COALESCE(SUM(amount), 0) FROM payments"))
    pending = int(_get_scalar(conn, "SELECT COUNT(*) FROM registrations WHERE status = %s", (H.STATUS_NEW,)))

    # Dynamically calculated total outstanding tuition
    total_outstanding = float(_get_scalar(conn, """
        SELECT COALESCE(SUM(GREATEST(0, COALESCE(r.annual_tuition, 3500.0) - COALESCE(p.paid, 0))), 0)
        FROM registrations r
        LEFT JOIN (
            SELECT registration_id, SUM(amount) AS paid
            FROM payments
            WHERE payment_for IN ('رسوم تسجيل', 'أقساط تعليمية')
            GROUP BY registration_id
        ) p ON p.registration_id = r.registration_id
        WHERE r.year_id = (SELECT year_id FROM academic_years ORDER BY start_date DESC LIMIT 1)
    """))

    # Payroll & Monthly Cash Flow Indicators
    monthly_salaries_due = float(_get_scalar(conn, "SELECT COALESCE(SUM(salary), 0) FROM teachers"))
    
    monthly_student_income = float(_get_scalar(conn, """
        SELECT COALESCE(SUM(amount), 0) 
        FROM payments 
        WHERE TO_CHAR(payment_date::date, 'YYYY-MM') = %s
    """, (current_month,)))

    monthly_salaries_paid = float(_get_scalar(conn, """
        SELECT COALESCE(SUM(amount), 0) 
        FROM teacher_payments 
        WHERE salary_month = %s
    """, (current_month,)))

    # ------------------------------------------------------------------
    # KPI Grid Row 1: Key Operational Counts
    # ------------------------------------------------------------------
    r1_col1, r1_col2, r1_col3 = st.columns(3)
    ui.kpi(r1_col1, "🎒", "إجمالي الطلاب", total_students, bg="#E9F5EC", fg="#219044")
    ui.kpi(r1_col2, "👩‍🏫", "المعلمون", total_teachers, bg="#F0F9FF", fg="#0284C7")
    ui.kpi(r1_col3, "🏷️", "الصفوف", total_classes, bg="#F5F3FF", fg="#7C3AED")

    st.write("")

    # ------------------------------------------------------------------
    # KPI Grid Row 2: Financial Metrics & Pending Registrations
    # ------------------------------------------------------------------
    r2_col1, r2_col2, r2_col3 = st.columns(3)
    ui.kpi(r2_col1, "💰", "إجمالي المقبوضات (الكلي)", H.format_money(total_revenue), bg="#ECFDF5", fg="#059669")
    ui.kpi(r2_col2, "⏳", "بانتظار التسجيل", pending, bg="#FEF3C7", fg="#D97706")
    ui.kpi(r2_col3, "🧾", "إجمالي الديون المتبقية", H.format_money(total_outstanding), bg="#FFE4E6", fg="#E11D48")

    st.write("")

    # ------------------------------------------------------------------
    # KPI Grid Row 3: Monthly Payroll & Cash Flow Health Check
    # ------------------------------------------------------------------
    st.markdown(f"##### 🗓️ الميزانية التشغيلية لشهر ({current_month})")
    p1, p2, p3 = st.columns(3)
    ui.kpi(p1, "💵", "مقبوضات الطلاب (هذا الشهر)", H.format_money(monthly_student_income), bg="#E0F2FE", fg="#0369A1")
    ui.kpi(p2, "📋", "إجمالي استحقاق الرواتب (شهرياً)", H.format_money(monthly_salaries_due), bg="#FEF2F2", fg="#991B1B")
    ui.kpi(p3, "✅", "الرواتب المدفوعة (هذا الشهر)", H.format_money(monthly_salaries_paid), bg="#F0FDF4", fg="#166534")

    # Income vs Salary Comparison Alert
    net_monthly_margin = monthly_student_income - monthly_salaries_due
    st.write("")
    if monthly_student_income < monthly_salaries_due:
        st.error(
            f"⚠️ **تنبيه سيولة مالية:** تحصيلات الطلاب لهذا الشهر ({H.format_money(monthly_student_income)} شيكل) "
            f"**أقل من** إجمالي رواتب المعلمات المطلوبة ({H.format_money(monthly_salaries_due)} شيكل) "
            f"بعدجز قدره: **{H.format_money(abs(net_monthly_margin))} شيكل**."
        )
    else:
        st.success(
            f"✅ **السيولة المالية ممتازة:** دخل الطلاب لهذا الشهر يستوعب إجمالي الرواتب "
            f"بفائض تشغيلي قدره **{H.format_money(net_monthly_margin)} شيكل**."
        )

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
                rev_sorted = rev.sort_values("الشهر")
                rev_sorted["الشهر"] = rev_sorted["الشهر"].astype(str)
                
                fig_rev = px.bar(rev_sorted, x="الشهر", y="المبلغ", text_auto=True, height=280)
                fig_rev.update_traces(marker_color="#10B981", marker_line_color="#059669", marker_line_width=1.5, textposition="outside")
                fig_rev.update_layout(xaxis_title="", yaxis_title="", xaxis=dict(type='category'), margin=dict(l=10, r=10, t=25, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Cairo", size=12))
                st.plotly_chart(fig_rev, use_container_width=True, config={"displayModeBar": False})

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
                dist["الصف"] = dist["الصف"].astype(str)
                fig_dist = px.bar(dist, x="الصف", y="العدد", text_auto=True, height=280)
                fig_dist.update_traces(marker_color="#0284C7", marker_line_color="#0369A1", marker_line_width=1.5, textposition="outside")
                fig_dist.update_layout(xaxis_title="", yaxis_title="", xaxis=dict(type='category'), yaxis=dict(dtick=1), margin=dict(l=10, r=10, t=25, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Cairo", size=12))
                st.plotly_chart(fig_dist, use_container_width=True, config={"displayModeBar": False})