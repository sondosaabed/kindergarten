"""
sections/teachers.py — إدارة المعلمات وصرف الرواتب
"""

import streamlit as st
import ui
import helpers as H
import teacher_receipt
from datetime import datetime


def render(conn):
    ui.section_header("👩‍🏫", "المعلمات والرواتب", "إدارة بيانات المعلمات وصرف الرواتب الشهرية")

    tab_add, tab_view, tab_salary = st.tabs([
        "➕ إضافة معلمة", 
        "📋 قائمة المعلمات", 
        "💵 صرف الرواتب وقسيمة الدفع"
    ])

    # -------------------------------------------------- TAB 1: ADD TEACHER --
    with tab_add:
        with st.form("add_teacher_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            national_id = c1.text_input("رقم الهوية *").strip()
            full_name = c2.text_input("الاسم الرباعي *").strip()

            c3, c4, c5 = st.columns(3)
            salary = c3.number_input("الراتب الشهري (شيكل) *", min_value=0.0, value=2000.0, step=100.0)
            mobile = c4.text_input("رقم الجوال").strip()
            hire_date = c5.date_input("تاريخ التعيين")

            address = st.text_input("العنوان السكني").strip()

            submitted = st.form_submit_button("💾 حفظ المعلمة", type="primary", use_container_width=True)

            if submitted:
                if not national_id or not full_name:
                    st.error("⚠️ يرجى إدخال رقم الهوية والاسم الرباعي.")
                else:
                    try:
                        cur = conn.cursor()
                        cur.execute("""
                            INSERT INTO teachers (national_id, full_name, salary, mobile, address, hire_date)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (national_id, full_name, salary, mobile, address, str(hire_date)))
                        conn.commit()
                        cur.close()
                        st.success(f"✅ تم إضافة المعلمة ({full_name}) بنجاح!")
                        st.rerun()
                    except Exception as e:
                        conn.rollback()
                        st.error(f"❌ حدث خطأ أثناء الحفظ: {e}")

    # -------------------------------------------------- TAB 2: VIEW TEACHERS --
    with tab_view:
        teachers = ui.df(conn, "SELECT national_id, full_name, salary, mobile, address, hire_date FROM teachers ORDER BY full_name")
        if teachers.empty:
            ui.empty_state("لا توجد معلمات مسجلات بعد.")
        else:
            st.dataframe(teachers.rename(columns={
                'national_id': 'رقم الهوية',
                'full_name': 'الاسم',
                'salary': 'الراتب الشهري',
                'mobile': 'الجوال',
                'address': 'العنوان',
                'hire_date': 'تاريخ التعيين'
            }), use_container_width=True, hide_index=True)

    # -------------------------------------------------- TAB 3: SALARY DISBURSEMENT --
    with tab_salary:
        teachers_df = ui.df(conn, "SELECT national_id, full_name, salary FROM teachers ORDER BY full_name")
        
        if teachers_df.empty:
            ui.empty_state("يرجى إضافة معلمات أولاً لتتمكن من صرف الرواتب.")
            return

        teacher_map = {f"{r.full_name} ({r.national_id})": (r.national_id, float(r.salary), r.full_name) for r in teachers_df.itertuples()}
        
        st.markdown("##### 📝 تسجيل دفعة راتب جديدة")
        
        selected_teacher_label = st.selectbox("اختر المعلمة *", list(teacher_map.keys()))
        t_id, default_salary, t_name = teacher_map[selected_teacher_label]

        current_month = datetime.now().strftime("%Y-%m")

        with st.form("disburse_salary_form"):
            col1, col2, col3 = st.columns(3)
            salary_month = col1.text_input("عن شهر (YYYY-MM) *", value=current_month)
            base_salary = col2.number_input("الراتب الأساسي (شيكل)", min_value=0.0, value=default_salary, step=50.0)
            bonus = col3.number_input("مكافأة / إضافي (شيكل)", min_value=0.0, value=0.0, step=50.0)

            col4, col5 = st.columns(2)
            deductions = col4.number_input("خصومات (شيكل)", min_value=0.0, value=0.0, step=50.0)
            notes = col5.text_input("ملاحظات إضافية (اختياري)")

            net_salary = max(0.0, base_salary + bonus - deductions)
            st.info(f"💵 **صافي الراتب المستحق للصرف:** {H.format_money(net_salary)} شيكل")

            pay_submitted = st.form_submit_button("🧾 تسجيل الصرف وطباعة قسيمة الراتب", type="primary", use_container_width=True)

        if pay_submitted:
            today = H.today_str()
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO teacher_payments (national_id, amount, payment_date, salary_month, base_salary, bonus, deductions, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING payment_id
                """, (t_id, net_salary, today, salary_month, base_salary, bonus, deductions, notes))
                payment_id = cur.fetchone()['payment_id']
                conn.commit()
                cur.close()

                st.success(f"✅ تم تسجيل صرف الراتب بنجاح! رقم القسيمة: #{payment_id}")

                teacher_receipt.render_salary_slip(
                    payment_id=payment_id,
                    teacher_name=t_name,
                    national_id=t_id,
                    payment_date=today,
                    salary_month=salary_month,
                    base_salary=base_salary,
                    bonus=bonus,
                    deductions=deductions,
                    net_amount=net_salary,
                    notes=notes
                )
            except Exception as e:
                conn.rollback()
                st.error(f"❌ حدث خطأ أثناء تسديد الراتب: {e}")

        st.markdown("---")
        st.markdown("##### 📋 سجل رواتب المعلمات المدفوعة")
        
        salary_logs = ui.df(conn, """
            SELECT tp.payment_id AS "رقم القسيمة", t.full_name AS "المعلمة",
                   tp.salary_month AS "عن شهر", tp.amount AS "الصافي المدفوع",
                   tp.payment_date AS "تاريخ الصرف", tp.notes AS "ملاحظات"
            FROM teacher_payments tp
            JOIN teachers t ON t.national_id = tp.national_id
            ORDER BY tp.payment_id DESC
        """)

        if salary_logs.empty:
            ui.empty_state("لا توجد رواتب مدفوعة مسجلة بعد.")
        else:
            st.dataframe(salary_logs, use_container_width=True, hide_index=True)