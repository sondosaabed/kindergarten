"""
sections/reports.py — التقارير والتصدير

Filtered report views with direct browser printing (PDF) and Excel/CSV exports.
"""

import io
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import ui
import helpers as H


def _to_excel(df: pd.DataFrame) -> bytes:
    """Helper to convert DataFrame to Excel binary stream."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='التقرير')
    return output.getvalue()


def _render_printable_roster_pdf(
    class_name: str,
    academic_year: str,
    df: pd.DataFrame,
    include_attendance: bool,
):
    """Renders a print-ready iframe with a 'Print/Save to PDF' button."""
    
    headers_html = "".join([f"<th>{col}</th>" for col in df.columns])
    
    rows_html = ""
    for _, row in df.iterrows():
        cells = "".join([f"<td>{str(val) if pd.notna(val) else ''}</td>" for val in row])
        rows_html += f"<tr>{cells}</tr>"

    logo_b64 = ui._logo_base64()
    logo_img_tag = f'<img src="data:image/png;base64,{logo_b64}" />' if logo_b64 else ""

    html_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
    <meta charset="utf-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
        
        * {{
            box-sizing: border-box;
            font-family: 'Cairo', 'Segoe UI', Tahoma, sans-serif;
        }}
        body {{
            direction: rtl;
            text-align: right;
            margin: 0;
            padding: 15px;
            background: #fff;
            color: #1F2A22;
        }}
        .print-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 2px solid #163D22;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }}
        .header-brand {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .header-brand img {{
            width: 48px;
            height: 48px;
            border-radius: 50%;
        }}
        .brand-titles .ar {{ font-size: 15px; font-weight: 800; color: #163D22; }}
        .brand-titles .en {{ font-size: 10px; color: #7C8A7E; }}
        .report-meta {{
            text-align: left;
            font-size: 12px;
            color: #475569;
        }}
        .report-title {{
            text-align: center;
            font-size: 18px;
            font-weight: 800;
            color: #163D22;
            margin: 10px 0 15px 0;
            background: #FAF9F5;
            padding: 6px;
            border-radius: 6px;
            border: 1px dashed #D7A431;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
            margin-top: 5px;
        }}
        th, td {{
            border: 1px solid #CBD5E1;
            padding: 6px 8px;
            text-align: center;
        }}
        th {{
            background-color: #163D22;
            color: white;
            font-weight: 700;
            font-size: 12px;
        }}
        tr:nth-child(even) {{
            background-color: #F8FAFC;
        }}
        .print-btn {{
            display: block;
            width: 100%;
            background: #163D22;
            color: white;
            border: none;
            padding: 10px 0;
            font-size: 14px;
            font-weight: 700;
            border-radius: 8px;
            cursor: pointer;
            margin-bottom: 15px;
        }}
        .print-btn:hover {{
            opacity: 0.9;
        }}

        @media print {{
            .print-btn {{ display: none; }}
            body {{ padding: 0; }}
            @page {{
                size: A4 {"landscape" if include_attendance else "portrait"};
                margin: 10mm;
            }}
        }}
    </style>
    </head>
    <body>
        <button class="print-btn" onclick="window.print()">🖨️ اضغط هنا للطباعة أو الحفظ كـ PDF</button>

        <div class="print-header">
            <div class="header-brand">
                {logo_img_tag}
                <div class="brand-titles">
                    <div class="ar">روضة مؤسسة شباب البيرة</div>
                    <div class="en">Al-Bireh Youth Foundation Kindergarten</div>
                </div>
            </div>
            <div class="report-meta">
                <div><strong>الصف:</strong> {class_name}</div>
                <div><strong>السنة الدراسية:</strong> {academic_year}</div>
                <div><strong>تاريخ الاستخراج:</strong> {H.today_str()}</div>
            </div>
        </div>

        <div class="report-title">
            كشف أسماء الطلاب {"والحضور" if include_attendance else ""} — {class_name} ({len(df)} طالب)
        </div>

        <table>
            <thead>
                <tr>{headers_html}</tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </body>
    </html>
    """
    
    height = 650 if len(df) > 10 else 450
    components.html(html_content, height=height, scrolling=True)


def render(conn):
    ui.section_header("📈", "التقارير والتصدير", "استخراج بيانات مفلترة وتصديرها إلى Excel")

    report_type = st.radio(
        "اختر نوع التقرير",
        [
            "🏫 كشف الطلاب حسب الصف (للحضور والغياب)",
            "💵 سجل المقبوضات المالية",
            "👨‍👩‍👧‍👦 قائمة الطلاب وأولياء الأمور",
            "📋 قائمة التسجيلات",
            "⚠️ كشف الديون والذمم المتبقية",
        ],
        horizontal=True,
    )

    st.markdown("---")

    result = pd.DataFrame()

    # --------------------------------------------------------------------------
    # 1. CLASS ROSTER & ATTENDANCE SHEET REPORT
    # --------------------------------------------------------------------------
    if report_type == "🏫 كشف الطلاب حسب الصف (للحضور والغياب)":
        classes_df = ui.df(conn, """
            SELECT c.class_id, (c.class_type || ' ' || c.section) AS class_name
            FROM classes c
            ORDER BY c.class_type, c.section
        """)

        if classes_df.empty:
            ui.empty_state("لا توجد صفوف معرفة في النظام.")
            return

        c1, c2, c3 = st.columns(3)
        class_options = dict(zip(classes_df['class_name'], classes_df['class_id']))
        selected_class_name = c1.selectbox("اختر الصف *", list(class_options.keys()))
        selected_class_id = class_options[selected_class_name]

        years = ui.df(conn, "SELECT year_id FROM academic_years ORDER BY year_id DESC")
        year_list = years['year_id'].tolist() if not years.empty else [H.CURRENT_YEAR_DEFAULT]
        selected_year = c2.selectbox("السنة الدراسية", year_list)

        include_attendance_cols = c3.checkbox("إضافة أعمدة لتسجيل الحضور والغياب (للطباعة)", value=True)

        query = """
            SELECT 
                s.student_id AS "رقم الهوية",
                s.full_name AS "اسم الطالب",
                s.gender AS "الجنس",
                s.birth_date AS "تاريخ الميلاد",
                p.father_name AS "اسم الأب",
                p.father_mobile AS "جوال الأب",
                p.mother_name AS "اسم الأم",
                r.status AS "حالة التسجيل"
            FROM registrations r
            JOIN students s ON r.student_id = s.student_id
            JOIN parents p ON s.father_id = p.father_id
            WHERE r.class_id = %s AND r.year_id = %s
            ORDER BY s.full_name ASC
        """
        result = ui.df(conn, query, (selected_class_id, selected_year))

        if not result.empty:
            result.insert(0, "م", range(1, len(result) + 1))

            if include_attendance_cols:
                for day in ["الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "ملاحظات"]:
                    result[day] = ""

            st.success(f"📋 عدد الطلاب في **{selected_class_name}**: **{len(result)} طالب/طالبة**")

            with st.expander("🖨️ معاينة وتوليد طباعة كشف الأسماء (PDF)", expanded=False):
                _render_printable_roster_pdf(
                    selected_class_name,
                    selected_year,
                    result,
                    include_attendance_cols,
                )

    # --------------------------------------------------------------------------
    # 2. FINANCIAL CASH RECEIPTS REPORT
    # --------------------------------------------------------------------------
    elif report_type == "💵 سجل المقبوضات المالية":
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
            st.metric("💰 إجمالي المبلغ المقبوض", H.format_money(result['المبلغ'].sum()))

    # --------------------------------------------------------------------------
    # 3. STUDENTS & GUARDIANS REGISTRY
    # --------------------------------------------------------------------------
    elif report_type == "👨‍👩‍👧‍👦 قائمة الطلاب وأولياء الأمور":
        result = ui.df(conn, """
            SELECT s.student_id AS "رقم هوية الطالب", s.full_name AS "اسم الطالب",
                   s.birth_date AS "تاريخ الميلاد", s.gender AS "الجنس",
                   p.father_name AS "اسم الأب", p.father_mobile AS "جوال الأب",
                   p.mother_name AS "اسم الأم", p.address AS "العنوان"
            FROM students s JOIN parents p ON s.father_id = p.father_id
            ORDER BY s.full_name ASC
        """)

    # --------------------------------------------------------------------------
    # 4. REGISTRATION LIST
    # --------------------------------------------------------------------------
    elif report_type == "📋 قائمة التسجيلات":
        years_df = ui.df(conn, "SELECT year_id FROM academic_years ORDER BY year_id DESC")
        year_list = years_df['year_id'].tolist() if not years_df.empty else []
        year_filter = st.selectbox("تصفية حسب السنة", ["الكل"] + year_list)

        query = """
            SELECT s.full_name AS "اسم الطالب", (c.class_type || ' ' || c.section) AS "الصف",
                   r.year_id AS "السنة الدراسية", r.status AS "الحالة", r.registration_date AS "تاريخ التسجيل"
            FROM registrations r
            JOIN students s ON r.student_id = s.student_id
            JOIN classes c ON c.class_id = r.class_id
            WHERE 1=1
        """
        params = []
        if year_filter != "الكل":
            query += " AND r.year_id = %s"
            params.append(year_filter)
        query += " ORDER BY r.registration_id DESC"
        result = ui.df(conn, query, tuple(params))

    # --------------------------------------------------------------------------
    # 5. OUTSTANDING BALANCES / DEBTORS REPORT
    # --------------------------------------------------------------------------
    else:  # "⚠️ كشف الديون والذمم المتبقية"
        years_df = ui.df(conn, "SELECT year_id FROM academic_years ORDER BY year_id DESC")
        year_list = years_df['year_id'].tolist() if not years_df.empty else [H.CURRENT_YEAR_DEFAULT]
        selected_year = st.selectbox("السنة الدراسية", year_list, key="debt_year")

        regs = ui.df(conn, """
            SELECT r.registration_id, s.full_name AS student_name, p.father_name, p.father_mobile,
                   (c.class_type || ' ' || c.section) AS class_label, r.status
            FROM registrations r
            JOIN students s ON s.student_id = r.student_id
            JOIN classes c ON c.class_id = r.class_id
            JOIN parents p ON p.father_id = s.father_id
            WHERE r.year_id = %s AND r.status != 'انسحب'
            ORDER BY s.full_name ASC
        """, (selected_year,))

        debt_rows = []
        if not regs.empty:
            for _, row in regs.iterrows():
                reg_id = int(row['registration_id'])
                paid = H.compute_paid_toward_tuition(conn, reg_id)
                remaining = H.compute_remaining_balance(conn, reg_id)

                if remaining > 0:
                    debt_rows.append({
                        "اسم الطالب": row['student_name'],
                        "الصف": row['class_label'],
                        "اسم ولي الأمر": row['father_name'],
                        "جوال الأب": row['father_mobile'],
                        "المدفوع (شيكل)": paid,
                        "المتبقي عليه (شيكل)": remaining,
                        "حالة التسجيل": row['status'],
                    })

        result = pd.DataFrame(debt_rows)

        if not result.empty:
            k1, k2 = st.columns(2)
            k1.metric("عدد الطلاب المتبقي عليهم مبالغ", len(result))
            k2.metric("إجمالي الديون المتبقية", H.format_money(result["المتبقي عليه (شيكل)"].sum()))

    # --------------------------------------------------------------------------
    # RENDER DATAFRAME & EXPORT CONTROLS
    # --------------------------------------------------------------------------
    if not result.empty:
        st.dataframe(result, use_container_width=True, hide_index=True)

        st.markdown("##### 📥 تصدير التقرير")
        c1, c2 = st.columns(2)
        c1.download_button(
            "📊 تحميل التقرير كملف Excel",
            data=_to_excel(result),
            file_name=f"report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

        csv_data = result.to_csv(index=False).encode('utf-8-sig')
        c2.download_button(
            "📄 تحميل التقرير كملف CSV",
            data=csv_data,
            file_name=f"report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        ui.empty_state("لا توجد بيانات مطابقة للفلاتر المحددة.")