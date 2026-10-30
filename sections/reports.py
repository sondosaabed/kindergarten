"""
sections/reports.py — التقارير والتصدير

Filtered report views with robust filtering (by class, year, date ranges), 
customizable column selection, summary metrics, landscape PDF printouts, 
and a comprehensive executive management analysis report.
"""

import io
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
from datetime import datetime

import ui
import helpers as H


def _to_excel(df: pd.DataFrame) -> bytes:
    """Helper to convert DataFrame to Excel binary stream."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='التقرير')
    return output.getvalue()


def _render_printable_report_pdf(
    report_title: str,
    meta_info: dict,
    df: pd.DataFrame,
    summary_metrics: dict,
):
    """Renders a print-ready iframe with a landscape PDF layout, letterhead, and summary footer."""
    
    headers_html = "".join([f"<th>{col}</th>" for col in df.columns])
    
    rows_html = ""
    for _, row in df.iterrows():
        cells = "".join([f"<td>{str(val) if pd.notna(val) else ''}</td>" for val in row])
        rows_html += f"<tr>{cells}</tr>"

    logo_b64 = ui._logo_base64()
    logo_img_tag = f'<img src="data:image/png;base64,{logo_b64}" />' if logo_b64 else ""

    meta_html = "".join([f"<div><strong>{k}:</strong> {v}</div>" for k, v in meta_info.items()])

    summary_html = ""
    if summary_metrics:
        summary_items = "".join([f'<div class="summary-card"><span>{k}</span><strong>{v}</strong></div>' for k, v in summary_metrics.items()])
        summary_html = f"""
        <div class="summary-section">
            <div class="summary-title">📊 الملخص الإحصائي المالي والإداري</div>
            <div class="summary-grid">{summary_items}</div>
        </div>
        """

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
            margin-bottom: 15px;
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
        .summary-section {{
            margin-top: 20px;
            border: 1px solid #163D22;
            border-radius: 8px;
            padding: 10px;
            background: #FAF9F5;
        }}
        .summary-title {{
            font-size: 13px;
            font-weight: 800;
            color: #163D22;
            margin-bottom: 8px;
            text-align: center;
        }}
        .summary-grid {{
            display: flex;
            justify-content: space-around;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .summary-card {{
            background: #fff;
            border: 1px solid #D7A431;
            border-radius: 6px;
            padding: 6px 14px;
            text-align: center;
            min-width: 140px;
        }}
        .summary-card span {{
            display: block;
            font-size: 11px;
            color: #7C8A7E;
        }}
        .summary-card strong {{
            display: block;
            font-size: 14px;
            color: #163D22;
            margin-top: 2px;
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
                size: A4 landscape;
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
                    <div class="ar">روضة أحلام الطفولة</div>
                    <div class="en">Childhood Dreams Kindergarten</div>
                </div>
            </div>
            <div class="report-meta">
                {meta_html}
                <div><strong>تاريخ الاستخراج:</strong> {H.today_str()}</div>
            </div>
        </div>

        <div class="report-title">
            {report_title} ({len(df)} سجل)
        </div>

        <table>
            <thead>
                <tr>{headers_html}</tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>

        {summary_html}
    </body>
    </html>
    """
    
    height = 720 if len(df) > 10 else 520
    components.html(html_content, height=height, scrolling=True)


def _get_scalar(conn, query, params=()):
    """Executes a scalar SQL query safely."""
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
    ui.section_header("📈", "التقارير والتصدير", "استخراج بيانات مفلترة وتصديرها وإدارتها")

    report_type = st.radio(
        "اختر نوع التقرير",
        [
            "📑 تقرير الإدارة العليا الشامل (التحليلي والمالي)",
            "🏫 كشف الطلاب حسب الصف (للحضور والغياب)",
            "💵 سجل المقبوضات المالية",
            "👨‍👩‍👧‍👦 قائمة الطلاب وأولياء الأمور",
            "📋 قائمة التسجيلات",
            "⚠️ كشف الديون والذمم المتبقية",
            "💼 سجل الرواتب والمستحقات",
            "💸 تقرير المصروفات التشغيلية",
            "🏛️ تقرير الأصول والموجودات الثابتة",
        ],
        horizontal=True,
    )

    st.markdown("---")

    result = pd.DataFrame()
    meta_info = {}
    report_title_str = ""
    summary_metrics = {}

    years_df = ui.df(conn, "SELECT year_id FROM academic_years ORDER BY year_id DESC")
    year_list = years_df['year_id'].tolist() if not years_df.empty else [H.CURRENT_YEAR_DEFAULT]

    classes_df = ui.df(conn, """
        SELECT c.class_id, (c.class_type || ' ' || c.section) AS class_name
        FROM classes c
        ORDER BY c.class_type, c.section
    """)

    # --------------------------------------------------------------------------
    # 0. EXECUTIVE MANAGEMENT COMPREHENSIVE REPORT
    # --------------------------------------------------------------------------
    if report_type == "📑 تقرير الإدارة العليا الشامل (التحليلي والمالي)":
        current_month = datetime.now().strftime("%Y-%m")
        
        total_students = int(_get_scalar(conn, "SELECT COUNT(*) FROM students"))
        total_teachers = int(_get_scalar(conn, "SELECT COUNT(*) FROM teachers"))
        total_classes = int(_get_scalar(conn, "SELECT COUNT(*) FROM classes"))
        total_revenue = float(_get_scalar(conn, "SELECT COALESCE(SUM(amount), 0) FROM payments"))
        total_expenses_paid = float(_get_scalar(conn, "SELECT COALESCE(SUM(amount_paid), 0) FROM expenses"))
        total_supplier_debts = float(_get_scalar(conn, "SELECT COALESCE(SUM(amount - amount_paid), 0) FROM expenses"))
        total_assets = float(_get_scalar(conn, "SELECT COALESCE(SUM(total_cost), 0) FROM assets"))
        
        monthly_student_income = float(_get_scalar(conn, """
            SELECT COALESCE(SUM(amount), 0) FROM payments WHERE TO_CHAR(payment_date::date, 'YYYY-MM') = %s
        """, (current_month,)))
        
        monthly_salaries_paid = float(_get_scalar(conn, """
            SELECT COALESCE(SUM(amount), 0) FROM teacher_payments WHERE salary_month = %s
        """, (current_month,)))
        
        monthly_expenses_paid = float(_get_scalar(conn, """
            SELECT COALESCE(SUM(amount_paid), 0) FROM expenses WHERE TO_CHAR(expense_date::date, 'YYYY-MM') = %s
        """, (current_month,)))
        
        total_monthly_cash_outflow = monthly_salaries_paid + monthly_expenses_paid
        net_monthly_margin = monthly_student_income - total_monthly_cash_outflow

        st.markdown("### 📑    تقرير أداء الروضة")
        st.markdown("تقرير إداري  مراجعة السيولة والعمليات التشغيلية.")

        # Top Executive Metrics
        e1, e2, e3, e4 = st.columns(4)
        e1.metric("إجمالي الطلاب المسجلين", total_students)
        e2.metric("إجمالي الإيرادات المحصلة", H.format_money(total_revenue))
        e3.metric("إجمالي المصروفات المدفوعة", H.format_money(total_expenses_paid))
        e4.metric("قيمة الأصول الثابتة", H.format_money(total_assets))

        st.markdown("---")

        # Visual Analytics Section
        st.markdown("#### 📊 الرسوم البيانية التوضيحية للأداء")
        left, right = st.columns(2)

        with left:
            with st.container(border=True):
                st.markdown("##### 📈 اتجاه المقبوضات آخر 6 أشهر")
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
                st.markdown("##### 🏷️ الكثافة الطلابية في الصفوف")
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

        # Breakdown Pie Charts
        exp_col, ast_col = st.columns(2)

        with exp_col:
            with st.container(border=True):
                st.markdown("##### 💸 هيكل المصروفات التشغيلية")
                exp_chart_df = ui.df(conn, """
                    SELECT category AS "الفئة", SUM(amount_paid) AS "الإجمالي"
                    FROM expenses GROUP BY category ORDER BY "الإجمالي" DESC
                """)
                if exp_chart_df.empty:
                    ui.empty_state("لا توجد مصروفات مسجلة بعد.")
                else:
                    fig_exp = px.pie(exp_chart_df, names="الفئة", values="الإجمالي", hole=0.4, height=280, color_discrete_sequence=px.colors.qualitative.Set3)
                    fig_exp.update_traces(textinfo="percent+label")
                    fig_exp.update_layout(margin=dict(l=10, r=10, t=25, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Cairo", size=12), showlegend=False)
                    st.plotly_chart(fig_exp, use_container_width=True, config={"displayModeBar": False})

        with ast_col:
            with st.container(border=True):
                st.markdown("##### 🧸 توزيع الأصول والتجهيزات التعليمية")
                ast_chart_df = ui.df(conn, """
                    SELECT category AS "الفئة", SUM(total_cost) AS "الإجمالي"
                    FROM assets GROUP BY category ORDER BY "الإجمالي" DESC
                """)
                if ast_chart_df.empty:
                    ui.empty_state("لا توجد أصول أو ألعاب مسجلة بعد.")
                else:
                    fig_ast = px.pie(ast_chart_df, names="الفئة", values="الإجمالي", hole=0.4, height=280, color_discrete_sequence=px.colors.qualitative.Pastel)
                    fig_ast.update_traces(textinfo="percent+label")
                    fig_ast.update_layout(margin=dict(l=10, r=10, t=25, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Cairo", size=12), showlegend=False)
                    st.plotly_chart(fig_ast, use_container_width=True, config={"displayModeBar": False})

        st.markdown("---")
        st.markdown("#### 📝 التوصيات والتحليل المالي الختامي:")
        st.markdown(f"""
        - **الموقف التشغيلي:** تعمل الروضة بطاقة استيعابية موزعة على {total_classes} صفوف تحت إدارة وتحفيز {total_teachers} معلمات قديرات.
        - **حالة السيولة الشهرية ({current_month}):** حققت التحصيلات مبلغ **{H.format_money(monthly_student_income)} شيكل** مقابل منصرفات تشغيلية ورواتب بقيمة **{H.format_money(total_monthly_cash_outflow)} شيكل**، بصافي هامش تشغيلي بلغ **{H.format_money(net_monthly_margin)} شيكل**.
        - **التزامات الموردين:** إجمالي الالتزامات الآجلة القائمة للموردين تبلغ **{H.format_money(total_supplier_debts)} شيكل**.
        """)

        # Print / PDF Export Preview for Executive Summary Report
        st.markdown("---")
        st.markdown("##### 📥 تصدار وطباعة التقرير الشامل")
        if st.button("🖨️ معاينة و طباعة التقرير الشامل للإدارة (PDF)", use_container_width=True):
            st.session_state['show_exec_print_preview'] = True

        if st.session_state.get('show_exec_print_preview', False):
            # Build a summary dataframe table for formal PDF printing output
            exec_summary_df = pd.DataFrame([
                {"البند الرئيسي": "إجمالي الطلاب", "القيمة الإحصائية": str(total_students), "ملاحظات إدارية": "طالب/ة مسجلون"},
                {"البند الرئيسي": "إجمالي المعلمات", "القيمة الإحصائية": str(total_teachers), "ملاحظات إدارية": "معلمة في الكادر التعليمي"},
                {"البند الرئيسي": "إجمالي الصفوف", "القيمة الإحصائية": str(total_classes), "ملاحظات إدارية": "شعب صفية نشطة"},
                {"البند الرئيسي": "إجمالي المقبوضات", "القيمة الإحصائية": H.format_money(total_revenue), "ملاحظات إدارية": "إيرادات تراكمية"},
                {"البند الرئيسي": "المصروفات المدفوعة", "القيمة الإحصائية": H.format_money(total_expenses_paid), "ملاحظات إدارية": "مصروفات تشغيلية مدفوعة"},
                {"البند الرئيسي": "التزامات الموردين", "القيمة الإحصائية": H.format_money(total_supplier_debts), "ملاحظات إدارية": "ذمم دائنة آجلة"},
                {"البند الرئيسي": "إجمالي الأصول", "القيمة الإحصائية": H.format_money(total_assets), "ملاحظات إدارية": "تجهيزات وألعاب وممتلكات"},
                {"البند الرئيسي": f"سيولة شهر {current_month}", "القيمة الإحصائية": H.format_money(net_monthly_margin), "ملاحظات إدارية": "صافي الفائض التشغيلي"}
            ])
            exec_meta = {"نوع التقرير": "تقرير الإدارة  الشامل", "حالة الروضة": "مستقرة وتحت المتابعة"}
            exec_metrics = {
                "إجمالي الإيرادات": H.format_money(total_revenue),
                "إجمالي المصروفات": H.format_money(total_expenses_paid),
                "صافي سيولة الشهر": H.format_money(net_monthly_margin)
            }
            st.markdown("#### معاينة الطباعة الرسمية للتقرير الشامل:")
            _render_printable_report_pdf("تقرير الإدارة   والأداء ", exec_meta, exec_summary_df, exec_metrics)
        return

    # --------------------------------------------------------------------------
    # 1. CLASS ROSTER & ATTENDANCE SHEET REPORT
    # --------------------------------------------------------------------------
    elif report_type == "🏫 كشف الطلاب حسب الصف (للحضور والغياب)":
        if classes_df.empty:
            ui.empty_state("لا توجد صفوف معرفة في النظام.")
            return

        c1, c2, c3 = st.columns(3)
        class_options = dict(zip(classes_df['class_name'], classes_df['class_id']))
        selected_class_name = c1.selectbox("اختر الصف *", list(class_options.keys()))
        selected_class_id = class_options[selected_class_name]

        selected_year = c2.selectbox("السنة الدراسية", year_list)
        include_attendance_cols = c3.checkbox("إضافة أعمدة لتسجيل الحضور والغياب", value=True)

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

            meta_info = {"الصف": selected_class_name, "السنة الدراسية": selected_year}
            report_title_str = f"كشف أسماء الطلاب {'والحضور' if include_attendance_cols else ''} — {selected_class_name}"
            
            male_count = len(result[result['الجنس'] == 'ذكر']) if 'الجنس' in result.columns else 0
            female_count = len(result[result['الجنس'] == 'أنثى']) if 'الجنس' in result.columns else 0
            summary_metrics = {
                "إجمالي عدد الطلاب": f"{len(result)} طالب/ة",
                "عدد الذكور": f"{male_count}",
                "عدد الإناث": f"{female_count}"
            }

    # --------------------------------------------------------------------------
    # 2. FINANCIAL CASH RECEIPTS REPORT
    # --------------------------------------------------------------------------
    elif report_type == "💵 سجل المقبوضات المالية":
        c1, c2, c3, c4 = st.columns(4)
        date_from = c1.date_input("من تاريخ", value=None)
        date_to = c2.date_input("إلى تاريخ", value=None)
        reason_filter = c3.selectbox("مقابل", ["الكل"] + H.PAYMENT_FOR)
        
        class_filter_options = ["الكل"] + list(classes_df['class_name']) if not classes_df.empty else ["الكل"]
        selected_class_filter = c4.selectbox("تصفية حسب الصف", class_filter_options)

        query = """
            SELECT p.receipt_number AS "رقم الوصل", s.full_name AS "اسم الطالب",
                   (c.class_type || ' ' || c.section) AS "الصف",
                   r.year_id AS "السنة الدراسية",
                   p.amount AS "المبلغ", p.payment_date AS "تاريخ الدفع",
                   p.payer_name AS "اسم الدافع", p.payment_for AS "مقابل"
            FROM payments p
            JOIN registrations r ON p.registration_id = r.registration_id
            JOIN students s ON r.student_id = s.student_id
            JOIN classes c ON r.class_id = c.class_id
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
        if selected_class_filter != "الكل":
            query += " AND (c.class_type || ' ' || c.section) = %s"
            params.append(selected_class_filter)
            
        query += " ORDER BY p.payment_date DESC"
        result = ui.df(conn, query, tuple(params))

        if not result.empty:
            result.insert(0, "م", range(1, len(result) + 1))
            total_collected = result['المبلغ'].sum()
            meta_info = {
                "الفترة": f"{date_from or 'البداية'} إلى {date_to or 'النهاية'}", 
                "مقابل": reason_filter,
                "الصف": selected_class_filter
            }
            report_title_str = "سجل المقبوضات المالية"
            summary_metrics = {
                "إجمالي المقبوضات": H.format_money(total_collected),
                "عدد السندات": f"{len(result)} سند"
            }

    # --------------------------------------------------------------------------
    # 3. STUDENTS & GUARDIANS REGISTRY
    # --------------------------------------------------------------------------
    elif report_type == "👨‍👩‍👧‍👦 قائمة الطلاب وأولياء الأمور":
        c1, c2 = st.columns(2)
        gender_filter = c1.selectbox("الجنس", ["الكل", "ذكر", "أنثى"])
        class_filter_options = ["الكل"] + list(classes_df['class_name']) if not classes_df.empty else ["الكل"]
        selected_class_filter = c2.selectbox("تصفية حسب الصف الحالي", class_filter_options)

        query = """
            SELECT DISTINCT s.student_id AS "رقم هوية الطالب", s.full_name AS "اسم الطالب",
                   s.birth_date AS "تاريخ الميلاد", s.gender AS "الجنس",
                   p.father_name AS "اسم الأب", p.father_mobile AS "جوال الأب",
                   p.mother_name AS "اسم الأم", p.address AS "العنوان",
                   (c.class_type || ' ' || c.section) AS "الصف الحالي"
            FROM students s 
            JOIN parents p ON s.father_id = p.father_id
            LEFT JOIN registrations r ON s.student_id = r.student_id
            LEFT JOIN classes c ON r.class_id = c.class_id
            WHERE 1=1
        """
        params = []
        if gender_filter != "الكل":
            query += " AND s.gender = %s"
            params.append(gender_filter)
        if selected_class_filter != "الكل":
            query += " AND (c.class_type || ' ' || c.section) = %s"
            params.append(selected_class_filter)

        query += " ORDER BY s.full_name ASC"
        result = ui.df(conn, query, tuple(params))

        if not result.empty:
            result.insert(0, "م", range(1, len(result) + 1))
            meta_info = {"الجنس": gender_filter, "الصف": selected_class_filter}
            report_title_str = "قائمة الطلاب وأولياء الأمور"
            summary_metrics = {
                "إجمالي الطلاب": f"{len(result)} طالب/ة"
            }

    # --------------------------------------------------------------------------
    # 4. REGISTRATION LIST
    # --------------------------------------------------------------------------
    elif report_type == "📋 قائمة التسجيلات":
        c1, c2, c3 = st.columns(3)
        year_filter = c1.selectbox("السنة الدراسية", ["الكل"] + year_list)
        class_filter_options = ["الكل"] + list(classes_df['class_name']) if not classes_df.empty else ["الكل"]
        selected_class_filter = c2.selectbox("الصف", class_filter_options)
        status_filter = c3.selectbox("حالة التسجيل", ["الكل", "مسجل", "انسحب", "مؤجل"])

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
        if selected_class_filter != "الكل":
            query += " AND (c.class_type || ' ' || c.section) = %s"
            params.append(selected_class_filter)
        if status_filter != "الكل":
            query += " AND r.status = %s"
            params.append(status_filter)

        query += " ORDER BY r.registration_id DESC"
        result = ui.df(conn, query, tuple(params))

        if not result.empty:
            result.insert(0, "م", range(1, len(result) + 1))
            meta_info = {"السنة": year_filter, "الصف": selected_class_filter, "الحالة": status_filter}
            report_title_str = "قائمة التسجيلات"
            active_count = len(result[result['الحالة'] == 'مسجل']) if 'الحالة' in result.columns else len(result)
            summary_metrics = {
                "إجمالي التسجيلات": f"{len(result)} تسجيل",
                "الطلاب المنتظمين": f"{active_count}"
            }

    # --------------------------------------------------------------------------
    # 5. OUTSTANDING BALANCES / DEBTORS REPORT
    # --------------------------------------------------------------------------
    elif report_type == "⚠️ كشف الديون والذمم المتبقية":
        c1, c2 = st.columns(2)
        selected_year = c1.selectbox("السنة الدراسية", year_list, key="debt_year")
        class_filter_options = ["الكل"] + list(classes_df['class_name']) if not classes_df.empty else ["الكل"]
        selected_class_filter = c2.selectbox("تصفية حسب الصف", class_filter_options)

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
                if selected_class_filter != "الكل" and row['class_label'] != selected_class_filter:
                    continue
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
            result.insert(0, "م", range(1, len(result) + 1))
            total_debt = result["المتبقي عليه (شيكل)"].sum()
            total_paid = result["المدفوع (شيكل)"].sum()
            meta_info = {"السنة الدراسية": selected_year, "الصف": selected_class_filter}
            report_title_str = "كشف الديون والذمم المتبقية"
            summary_metrics = {
                "إجمالي الذمم المتبقية": H.format_money(total_debt),
                "إجمالي المدفوعات المسددة": H.format_money(total_paid),
                "عدد الطلاب أصحاب الديون": f"{len(result)} طالب"
            }

    # --------------------------------------------------------------------------
    # 6. TEACHER PAYMENTS REPORT
    # --------------------------------------------------------------------------
    elif report_type == "💼 سجل الرواتب والمستحقات":
        c1, c2 = st.columns(2)
        month_filter = c1.text_input("تصفية حسب شهر الراتب (مثال: 2026-10)", value="")
        
        teachers_df = ui.df(conn, "SELECT national_id, full_name FROM teachers ORDER BY full_name")
        teacher_options = {"الكل": "الكل"}
        if not teachers_df.empty:
            teacher_options.update(dict(zip(teachers_df['full_name'], teachers_df['national_id'])))
        selected_teacher_name = c2.selectbox("اختر المعلم/ة", list(teacher_options.keys()))

        query = """
            SELECT tp.payment_id AS "رقم القسيمة", t.full_name AS "اسم المعلم/ة",
                   tp.salary_month AS "شهر الراتب", tp.base_salary AS "الراتب الأساسي",
                   tp.bonus AS "المكافآت", tp.deductions AS "الخصومات", tp.amount AS "صافي الصرف",
                   tp.payment_date AS "تاريخ الصرف"
            FROM teacher_payments tp
            JOIN teachers t ON tp.national_id = t.national_id
            WHERE 1=1
        """
        params = []
        if month_filter.strip():
            query += " AND tp.salary_month = %s"
            params.append(month_filter.strip())
        if selected_teacher_name != "الكل":
            query += " AND tp.national_id = %s"
            params.append(teacher_options[selected_teacher_name])

        query += " ORDER BY tp.payment_date DESC"
        result = ui.df(conn, query, tuple(params))

        if not result.empty:
            result.insert(0, "م", range(1, len(result) + 1))
            total_salaries = result['صافي الصرف'].sum()
            meta_info = {"الشهر": month_filter or "الكل", "المعلم/ة": selected_teacher_name}
            report_title_str = "سجل رواتب المعلمين والمعلمات"
            summary_metrics = {
                "إجمالي الرواتب المصروفة": H.format_money(total_salaries),
                "عدد الحركات": f"{len(result)} حركة"
            }

    # --------------------------------------------------------------------------
    # 7. OPERATIONAL EXPENSES REPORT
    # --------------------------------------------------------------------------
    elif report_type == "💸 تقرير المصروفات التشغيلية":
        c1, c2, c3 = st.columns(3)
        date_from = c1.date_input("من تاريخ", value=None)
        date_to = c2.date_input("إلى تاريخ", value=None)
        status_filter = c3.selectbox("حالة الدفع", ["الكل", "مدفوع بالكامل", "متبقي جزء", "غير مدفوع"])

        query = """
            SELECT expense_id AS "رقم المصروف", expense_date AS "التاريخ",
                   category AS "التصنيف", amount AS "المبلغ الكلي",
                   amount_paid AS "المبلغ المدفوع", payment_status AS "حالة الدفع",
                   payee AS "الجهة المستفيدة", notes AS "ملاحظات"
            FROM expenses
            WHERE 1=1
        """
        params = []
        if date_from:
            query += " AND expense_date >= %s"
            params.append(str(date_from))
        if date_to:
            query += " AND expense_date <= %s"
            params.append(str(date_to))
        if status_filter != "الكل":
            query += " AND payment_status = %s"
            params.append(status_filter)

        query += " ORDER BY expense_date DESC"
        result = ui.df(conn, query, tuple(params))

        if not result.empty:
            result.insert(0, "م", range(1, len(result) + 1))
            total_exp = result['المبلغ الكلي'].sum()
            total_paid_exp = result['المبلغ المدفوع'].sum()
            meta_info = {"الفترة": f"{date_from or 'البداية'} إلى {date_to or 'النهاية'}", "الحالة": status_filter}
            report_title_str = "تقرير المصروفات التشغيلية"
            summary_metrics = {
                "إجمالي المصروفات": H.format_money(total_exp),
                "إجمالي المدفوع فعلياً": H.format_money(total_paid_exp)
            }

    # --------------------------------------------------------------------------
    # 8. ASSETS & EQUIPMENT REPORT
    # --------------------------------------------------------------------------
    else:  # "🏛️ تقرير الأصول والموجودات الثابتة"
        c1, c2 = st.columns(2)
        condition_filter = c1.selectbox("حالة الأصل", ["الكل", "ممتازة", "جيدة", "تحتاج صيانة", "تالفة"])
        category_input = c2.text_input("تصفية حسب التصنيف", value="")

        query = """
            SELECT asset_id AS "رقم الأصل", item_name AS "اسم الصنف",
                   category AS "التصنيف", quantity AS "الكمية",
                   unit_cost AS "سعر الوحدة", total_cost AS "التكلفة الكلية",
                   condition_status AS "الحالة", purchase_date AS "تاريخ الشراء"
            FROM assets
            WHERE 1=1
        """
        params = []
        if condition_filter != "الكل":
            query += " AND condition_status = %s"
            params.append(condition_filter)
        if category_input.strip():
            query += " AND category ILIKE %s"
            params.append(f"%{category_input.strip()}%")

        query += " ORDER BY purchase_date DESC"
        result = ui.df(conn, query, tuple(params))

        if not result.empty:
            result.insert(0, "م", range(1, len(result) + 1))
            total_assets_cost = result['التكلفة الكلية'].sum()
            total_items_count = result['الكمية'].sum()
            meta_info = {"الحالة": condition_filter, "التصنيف": category_input or "الكل"}
            report_title_str = "تقرير الأصول والموجودات الثابتة"
            summary_metrics = {
                "إجمالي قيمة الأصول": H.format_money(total_assets_cost),
                "إجمالي عدد القطع": f"{total_items_count} قطعة"
            }

    # --------------------------------------------------------------------------
    # ATTRIBUTE SELECTION & EXPORT CONTROLS (For tabular reports)
    # --------------------------------------------------------------------------
    if not result.empty:
        st.markdown("---")
        st.subheader("⚙️ تخصيص الأعمدة المعروضة")
        
        all_columns = list(result.columns)
        selected_columns = st.multiselect(
            "اختر الحقول/العمود المراد إظهارها في التقرير والطباعة:",
            options=all_columns,
            default=all_columns
        )

        if selected_columns:
            display_df = result[selected_columns]
        else:
            display_df = result

        st.markdown("---")
        st.subheader("👀 معاينة التقرير والملخصات")
        
        if summary_metrics:
            cols = st.columns(len(summary_metrics))
            for i, (k, v) in enumerate(summary_metrics.items()):
                cols[i].metric(label=k, value=v)
            st.markdown("")

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        st.markdown("##### 📥 خيارات الطباعة والتصدير")
        c1, c2 = st.columns(2)
        
        with c1:
            st.download_button(
                "📊 تحميل التقرير كملف Excel",
                data=_to_excel(display_df),
                file_name=f"report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

        with c2:
            if st.button("🖨️ معاينة و طباعة التقرير ( PDF)", use_container_width=True):
                st.session_state['show_report_print_preview'] = True

        if st.session_state.get('show_report_print_preview', False):
            st.markdown("---")
            st.markdown("#### معاينة الطباعة الرسمية :")
            _render_printable_report_pdf(report_title_str, meta_info, display_df, summary_metrics)
    elif report_type != "📑 تقرير الأداء العام  ":
        ui.empty_state("لا توجد بيانات مطابقة للفلاتر المحددة.")