"""
sections/reports.py — التقارير والتصدير

Filtered report views with Excel/CSV export buttons and an in-browser printable roster sheet.
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


def _render_printable_attendance_sheet(class_name: str, year_id: str, df: pd.DataFrame):
    """Generates an in-iframe HTML template with a window.print() button for printing a clean roster sheet."""
    logo_b64 = ui._logo_base64()
    logo_img_tag = f'<img src="data:image/png;base64,{logo_b64}" />' if logo_b64 else ""

    rows_html = ""
    for _, row in df.iterrows():
        rows_html += f"""
        <tr>
            <td style="text-align:center;">{row['م']}</td>
            <td><b>{row['اسم الطالب']}</b></td>
            <td style="text-align:center;">{row['الجنس']}</td>
            <td>{row['اسم الأب']}</td>
            <td style="direction:ltr; text-align:right;">{row['جوال الأب']}</td>
            <td class="att-cell"></td>
            <td class="att-cell"></td>
            <td class="att-cell"></td>
            <td class="att-cell"></td>
            <td class="att-cell"></td>
            <td class="notes-cell"></td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
    <meta charset="utf-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
        * {{ box-sizing: border-box; font-family: 'Cairo', sans-serif; }}
        body {{ direction: rtl; text-align: right; margin: 0; padding: 10px; background: #fff; }}
        
        .header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 2px solid #163D22;
            padding-bottom: 8px;
            margin-bottom: 12px;
        }}
        .header-logo {{ display: flex; align-items: center; gap: 10px; }}
        .header-logo img {{ width: 48px; height: 48px; border-radius: 50%; }}
        .header-title h2 {{ margin: 0; color: #163D22; font-size: 18px; }}
        .header-title p {{ margin: 2px 0 0 0; color: #666; font-size: 12px; }}
        .meta-info {{ font-size: 13px; font-weight: bold; color: #333; }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
            margin-top: 10px;
        }}
        th, td {{
            border: 1px solid #163D22;
            padding: 5px 6px;
            vertical-align: middle;
        }}
        th {{
            background-color: #f2f7f4;
            color: #163D22;
            font-weight: 700;
            text-align: center;
        }}
        .att-cell {{ width: 38px; }}
        .notes-cell {{ width: 90px; }}

        .print-btn {{
            display: block;
            width: 100%;
            background: #163D22;
            color: #fff;
            border: none;
            border-radius: 8px;
            padding: 10px 0;
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            margin-bottom: 12px;
        }}
        .print-btn:hover {{ opacity: .9; }}

        @media print {{
            .print-btn {{ display: none; }}
            body {{ padding: 0; }}
            @page {{ size: A4 portrait; margin: 8mm; }}
        }}
    </style>
    </head>
    <body>
        <button class="print-btn" onclick="window.print()">🖨️ طباعة كشف الحضور والغياب (A4)</button>
        
        <div class="header">
            <div class="header-logo">
                {logo_img_tag}
                <div class="header-title">
                    <h2>روضة مؤسسة شباب البيرة</h2>
                    <p>Al-Bireh Youth Foundation Kindergarten</p>
                </div>
            </div>
            <div class="meta-info">
                <div>كشف حضور وغياب — <b>{class_name}</b></div>
                <div>السنة الدراسية: <b>{year_id}</b></div>
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th style="width:25px;">م</th>
                    <th>اسم الطالب</th>
                    <th style="width:40px;">الجنس</th>
                    <th>اسم ولي الأمر</th>
                    <th>رقم التواصل</th>
                    <th class="att-cell">الأحد</th>
                    <th class="att-cell">الإثنين</th>
                    <th class="att-cell">الثلاثاء</th>
                    <th class="att-cell">الأربعاء</th>
                    <th class="att-cell">الخميس</th>
                    <th class="notes-cell">ملاحظات</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </body>
    </html>
    """
    components.html(html_content, height=650, scrolling=True)


def render(conn):
    ui.section_header("📈", "التقارير والتصدير", "استخراج بيانات مفلترة وتصديرها إلى Excel أو طباعتها")

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

        c1, c2 = st.columns(2)
        class_options = dict(zip(classes_df['class_name'], classes_df['class_id']))
        selected_class_name = c1.selectbox("اختر الصف *", list(class_options.keys()))
        selected_class_id = class_options[selected_class_name]

        years = ui.df(conn, "SELECT year_id FROM academic_years ORDER BY is_current DESC, year_id DESC")
        year_list = years['year_id'].tolist() if not years.empty else [H.CURRENT_YEAR_DEFAULT]
        selected_year = c2.selectbox("السنة الدراسية", year_list)

        query = """
            SELECT 
                s.national_id AS "رقم الهوية",
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
            st.success(f"📋 عدد الطلاب في **{selected_class_name}**: **{len(result)} طالب/طالبة**")

            # Expandable Section to Print Attendance Sheet directly from browser
            with st.expander("🖨️ المعاينة والطباعة المباشرة لكشف الحضور (ورقي)", expanded=True):
                _render_printable_attendance_sheet(selected_class_name, selected_year, result)

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
        years_df = ui.df(conn, "SELECT year_id FROM academic_years ORDER BY is_current DESC, year_id DESC")
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
    # DATAFRAME DISPLAY & DOWNLOAD BUTTONS (EXCEL / CSV)
    # --------------------------------------------------------------------------
    if not result.empty:
        st.markdown("##### 📊 جدول البيانات")
        st.dataframe(result, use_container_width=True, hide_index=True)

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