"""
sections/salaries.py — قسم رواتب المعلمات
"""

import streamlit as st
import ui
import helpers as H
import teacher_receipt
from datetime import datetime


def render(conn):
    ui.section_header("💸", "رواتب المعلمات", "إدارة صرف وتعديل وإعادة طباعة قسائم الرواتب الشهرية")

    teachers_df = ui.df(conn, "SELECT national_id, full_name, salary FROM teachers ORDER BY full_name")
    
    if teachers_df.empty:
        ui.empty_state("لا توجد معلمات مسجلات بعد. قم بإضافة معلمات أولاً من قسم «المعلمون».")
        return

    tab_pay, tab_log = st.tabs(["➕ صرف راتب شهري", "📋 سجل الرواتب والإعادة"])

    teacher_map = {f"{r.full_name} ({r.national_id})": (r.national_id, float(r.salary), r.full_name) for r in teachers_df.itertuples()}

    # -------------------------------------------------- TAB 1: DISBURSE SALARY --
    with tab_pay:
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

    # ---------------------------------- TAB 2: LOG, REPRINT, EDIT & DELETE --
    with tab_log:
        salary_logs = ui.df(conn, """
            SELECT tp.payment_id, tp.national_id, t.full_name AS "المعلمة",
                   tp.salary_month AS "عن شهر", tp.base_salary AS "الأساسي",
                   tp.bonus AS "المكافأة", tp.deductions AS "الخصم",
                   tp.amount AS "الصافي المدفوع", tp.payment_date AS "تاريخ الصرف",
                   tp.notes AS "ملاحظات"
            FROM teacher_payments tp
            JOIN teachers t ON t.national_id = tp.national_id
            ORDER BY tp.payment_id DESC
        """)

        if salary_logs.empty:
            ui.empty_state("لا توجد رواتب مدفوعة مسجلة بعد.")
        else:
            search = st.text_input("🔍 ابحث باسم المعلمة أو الشهر")
            shown = salary_logs.copy()
            if search:
                shown = shown[shown["المعلمة"].str.contains(search, na=False) |
                              shown["عن شهر"].str.contains(search, na=False)]

            display_df = shown.drop(columns=['payment_id', 'national_id'])
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            st.metric("💰 مجموع الرواتب المدفوعة المعروضة", f"{H.format_money(shown['الصافي المدفوع'].sum())} شيكل")

            st.markdown("---")
            st.markdown("##### ⚙️ إدارة القسيمة المحددة (إعادة طباعة / تعديل / حذف)")

            sal_options = [
                (
                    int(row['payment_id']),
                    f"قسيمة #{int(row['payment_id'])} — {row['المعلمة']} — شهر {row['عن شهر']} — صافي: {H.format_money(row['الصافي المدفوع'])} شيكل"
                )
                for _, row in salary_logs.iterrows()
            ]

            selected_sal = st.selectbox(
                "اختر قسيمة الراتب",
                options=sal_options,
                format_func=lambda x: x[1] if x else "اختر...",
                index=None,
                placeholder="اختر قسيمة...",
                key="salary_select_edit"
            )

            if selected_sal:
                p_id = selected_sal[0]
                sal_row = salary_logs[salary_logs['payment_id'] == p_id].iloc[0]

                # 🖨️ Reprint Option
                if st.button("🖨️ إعادة عرض / طباعة القسيمة المحددة", use_container_width=True):
                    teacher_receipt.render_salary_slip(
                        payment_id=p_id,
                        teacher_name=sal_row['المعلمة'],
                        national_id=sal_row['national_id'],
                        payment_date=str(sal_row['تاريخ الصرف']),
                        salary_month=sal_row['عن شهر'],
                        base_salary=float(sal_row['الأساسي']),
                        bonus=float(sal_row['المكافأة']),
                        deductions=float(sal_row['الخصم']),
                        net_amount=float(sal_row['الصافي المدفوع']),
                        notes=sal_row['ملاحظات'] or ""
                    )

                # ✏️ Edit & Delete Form
                with st.expander(f"✏️ تعديل بيانات القسيمة #{p_id}", expanded=False):
                    with st.form("edit_salary_form"):
                        ec1, ec2, ec3 = st.columns(3)
                        e_month = ec1.text_input("عن شهر", value=sal_row['عن شهر'])
                        e_base = ec2.number_input("الراتب الأساسي", min_value=0.0, value=float(sal_row['الأساسي']), step=50.0)
                        e_bonus = ec3.number_input("المكافأة", min_value=0.0, value=float(sal_row['المكافأة']), step=50.0)

                        ec4, ec5 = st.columns(2)
                        e_deductions = ec4.number_input("الخصومات", min_value=0.0, value=float(sal_row['الخصم']), step=50.0)
                        e_notes = ec5.text_input("ملاحظات", value=sal_row['ملاحظات'] or "")

                        e_net = max(0.0, e_base + e_bonus - e_deductions)
                        st.caption(f"💡 صافي الراتب الجديد بعد التعديل: **{H.format_money(e_net)} شيكل**")

                        btn1, btn2 = st.columns(2)
                        save_edit = btn1.form_submit_button("💾 حفظ التعديلات", type="primary", use_container_width=True)
                        delete_sal = btn2.form_submit_button("🗑️ حذف قسيمة الراتب", use_container_width=True)

                        if save_edit:
                            try:
                                cur = conn.cursor()
                                cur.execute("""
                                    UPDATE teacher_payments 
                                    SET salary_month=%s, base_salary=%s, bonus=%s, deductions=%s, amount=%s, notes=%s
                                    WHERE payment_id=%s
                                """, (e_month, e_base, e_bonus, e_deductions, e_net, e_notes, p_id))
                                conn.commit()
                                cur.close()
                                st.success("✅ تم حفظ التعديلات وإعادة حساب الراتب الصافي بنجاح!")
                                st.rerun()
                            except Exception as e:
                                conn.rollback()
                                st.error(f"❌ حدث خطأ أثناء الحفظ: {e}")

                        if delete_sal:
                            try:
                                cur = conn.cursor()
                                cur.execute("DELETE FROM teacher_payments WHERE payment_id=%s", (p_id,))
                                conn.commit()
                                cur.close()
                                st.warning("🗑️ تم حذف عملية صرف الراتب بنجاح!")
                                st.rerun()
                            except Exception as e:
                                conn.rollback()
                                st.error(f"❌ حدث خطأ أثناء الحذف: {e}")