"""
sections/reports.py — التقارير والتصدير

Filtered report views with an Excel export button.
"""

import io
import pandas as pd
import streamlit as st

import ui
import helpers as H


def _to_excel(d):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        d.to_excel(writer, index=False, sheet_name='Report')
    return output.getvalue()


def render(conn):
    ui.section_header(" 📈 ", "التقارير والتصدير", "استخراج بيانات مفلترة إلى Excel")

    report_type = st.radio(
        "اختر نوع التقرير",
        ["سجل المقبوضات المالية", "قائمة الطلاب وأولياء الأمور", "قائمة التسجيلات"],
        horizontal=True,
    )

    if report_type == "سجل المقبوضات المالية":
        c1, c2, c3 = st.columns(3)
        date_from = c1.date_input("من تاريخ", value=None)
        date_to = c2.date_input("إلى تاريخ", value=None)
        reason_filter = c3.selectbox("مقابل", ["الكل"] + H.PAYMENT_FOR)

        query = """
            SELECT p.receipt_number AS "رقم الوصل", s.full_name AS "اسم الطالب",
                   p.amount AS "المبلغ", p.payment_date AS "تاريخ الدفع",
                   p.payer_name AS "اسم الدافع", p.payment_for AS "مقابل"
            FROM payments p
            JOIN registrations r ON p.registration_id = r.registration_id
            JOIN students s ON r.student_id = s.student_id
            WHERE 1=1
        """
        params = []
        if date_from:
            query += " AND p.payment_date >= %s"
            params.append(str(date_from))
        if date_to:
            query += " AND p.payment_date <= %s"
            params.append(str(date_to))
        if reason_filter != "الكل":
            query += " AND p.payment_for = %s"
            params.append(reason_filter)
        query += " ORDER BY p.payment_date DESC"
        result = ui.df(conn, query, tuple(params))

        if not result.empty:
            st.metric("💰 إجمالي المبلغ", H.format_money(result['المبلغ'].sum()))

    elif report_type == "قائمة الطلاب وأولياء الأمور":
        result = ui.df(conn, """
            SELECT s.student_id AS "رقم هوية الطالب", s.full_name AS "اسم الطالب",
                   s.birth_date AS "تاريخ الميلاد", s.gender AS "الجنس",
                   p.father_name AS "اسم الأب", p.father_mobile AS "جوال الأب",
                   p.mother_name AS "اسم الأم", p.address AS "العنوان"
            FROM students s JOIN parents p ON s.father_id = p.father_id
        """)

    else:  # registrations
        years_df = ui.df(conn, "SELECT year_id FROM academic_years")
        year_list = years_df['year_id'].tolist() if not years_df.empty else []
        year_filter = st.selectbox("تصفية حسب السنة", ["الكل"] + year_list)

        query = """
            SELECT s.full_name AS "اسم الطالب", (c.class_type || ' ' || c.section) AS "الصف",
                   r.year_id AS "السنة الدراسية", r.status AS "الحالة", r.registration_date AS "تاريخ التسجيل"
            FROM registrations r
            JOIN students s ON s.student_id = r.student_id
            JOIN classes c ON c.class_id = r.class_id
            WHERE 1=1
        """
        params = []
        if year_filter != "الكل":
            query += " AND r.year_id = %s"
            params.append(year_filter)
        result = ui.df(conn, query, tuple(params))

    st.dataframe(result, use_container_width=True, hide_index=True)

    if not result.empty:
        st.download_button(
            "📥 تحميل التقرير كملف Excel",
            data=_to_excel(result),
            file_name=f"report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        ui.empty_state("لا توجد بيانات مطابقة للفلاتر المحددة.")