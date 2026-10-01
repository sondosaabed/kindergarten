"""
sections/salaries.py — قسم رواتب المعلمات وسلفهم
"""

import streamlit as st
import ui
import helpers as H
import teacher_receipt
from datetime import datetime


def render(conn):
    ui.section_header("💸", "رواتب المعلمات والسلف", "إدارة الرواتب، تسجيل السلف الشهرية، والتحكم بالقسائم")

    teachers_df = ui.df(conn, "SELECT national_id, full_name, salary FROM teachers ORDER BY full_name")
    
    if teachers_df.empty:
        ui.empty_state("لا توجد معلمات مسجلات بعد. قم بإضافة معلمات أولاً من قسم «المعلمون».")
        return

    tab_pay, tab_advances, tab_log = st.tabs(["➕ صرف راتب شهري", "💵 إدارة وسلف المعلمات", "📋 سجل الرواتب والإعادة"])

    teacher_map = {f"{r.full_name} ({r.national_id})": (r.national_id, float(r.salary), r.full_name) for r in teachers_df.itertuples()}

    # -------------------------------------------------- TAB 1: DISBURSE SALARY --
    with tab_pay:
        st.markdown("##### 📝 تسجيل دفعة راتب جديدة")
        
        selected_teacher_label = st.selectbox("اختر المعلمة *", list(teacher_map.keys()), key="pay_teacher_select")
        t_id, default_salary, t_name = teacher_map[selected_teacher_label]

        current_month = datetime.now().strftime("%Y-%m")

        # Fetch pending (undeducted) advances for this teacher for the current month
        try:
            advances_df = ui.df(conn, """
                SELECT advance_id, amount, advance_date, notes 
                FROM teacher_advances 
                WHERE national_id = %s AND salary_month = %s AND is_deducted = FALSE
            """ % (t_id, f"'{current_month}'")) # or via safe parameterized query if supported by ui.df, but let's calculate total pending:
        except Exception:
            advances_df = None

        # Let's query securely using cursor for total pending advances for this month
        pending_advances_total = 0.0
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT COALESCE(SUM(amount), 0.0) AS total_adv 
                FROM teacher_advances 
                WHERE national_id = %s AND salary_month = %s AND is_deducted = FALSE
            """, (t_id, current_month))
            row_adv = cur.fetchone()
            if row_adv:
                pending_advances_total = float(row_adv['total_adv'])
            cur.close()
        except Exception:
            pending_advances_total = 0.0

        if pending_advances_total > 0:
            st.warning(, icon="⚠️")

        with st.form("disburse_salary_form"):
            col1, col2, col3 = st.columns(3)
            salary_month = col1.text_input("عن شهر (YYYY-MM) *", value=current_month)
            base_salary = col2.number_input("الراتب الأساسي (شيكل)", min_value=0.0, value=default_salary, step=50.0)
            bonus = col3.number_input("مكافأة / إضافي (شيكل)", min_value=0.0, value=0.0, step=50.0)

            col4, col5, col6 = st.columns(3)
            deductions = col4.number_input("خصومات أخرى (شيكل)", min_value=0.0, value=0.0, step=50.0)
            auto_advance = col5.number_input("سلف مستقطعة لهذا الشهر (شيكل)", min_value=0.0, value=pending_advances_total, step=50.0)
            notes = col6.text_input("ملاحظات إضافية (اختياري)")

            net_salary = max(0.0, base_salary + bonus - deductions - auto_advance)
            st.info(f"💵 **صافي الراتب المستحق للصرف:** {H.format_money(net_salary)} شيكل")

            pay_submitted = st.form_submit_button("🧾 تسجيل الصرف وطباعة قسيمة الراتب", type="primary", use_container_width=True)

        if pay_submitted:
            today = H.today_str()
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO teacher_payments (national_id, amount, payment_date, salary_month, base_salary, bonus, deductions, advance, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING payment_id
                """, (t_id, net_salary, today, salary_month, base_salary, bonus, deductions, auto_advance, notes))
                payment_id = cur.fetchone()['payment_id']

                # Mark pending advances for this teacher & month as deducted
                cur.execute("""
                    UPDATE teacher_advances 
                    SET is_deducted = TRUE 
                    WHERE national_id = %s AND salary_month = %s AND is_deducted = FALSE
                """, (t_id, salary_month))

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
                    advance=auto_advance,
                    net_amount=net_salary,
                    notes=notes
                )
            except Exception as e:
                conn.rollback()
                st.error(f"❌ حدث خطأ أثناء تسديد الراتب: {e}")

    # ------------------------------------------------ TAB 2: ADVANCES MANAGEMENT --
    with tab_advances:
        st.markdown("##### 💵 تسجيل سلفة جديدة لمعلمة (قبل موعد الراتب)")
        
        with st.form("add_advance_form", clear_on_submit=True):
            adv_teacher_label = st.selectbox("اختر المعلمة *", list(teacher_map.keys()), key="adv_teacher_select")
            adv_t_id, _, _ = teacher_map[adv_teacher_label]

            ac1, ac2, ac3 = st.columns(3)
            adv_amount = ac1.number_input("مبلغ السلفة (شيكل) *", min_value=0.0, value=100.0, step=50.0)
            adv_month = ac2.text_input("تخصم من راتب شهر (YYYY-MM) *", value=current_month)
            adv_date = ac3.date_input("تاريخ طلب/صرف السلفة")

            adv_notes = st.text_input("سبب أو ملاحظات السلفة (اختياري)")

            adv_submitted = st.form_submit_button("💾 حفظ وتسجيل السلفة", type="primary", use_container_width=True)

            if adv_submitted:
                if adv_amount <= 0:
                    st.error("⚠️ يرجى إدخال مبلغ سلفة صحيح.")
                else:
                    try:
                        cur = conn.cursor()
                        cur.execute("""
                            INSERT INTO teacher_advances (national_id, amount, advance_date, salary_month, notes, is_deducted)
                            VALUES (%s, %s, %s, %s, %s, FALSE)
                        """, (adv_t_id, adv_amount, str(adv_date), adv_month, adv_notes))
                        conn.commit()
                        cur.close()
                        st.success("✅ تم تسجيل السلفة بنجاح وسيتم خصمها تلقائياً عند صرف راتب الشهر المحدد.")
                        st.rerun()
                    except Exception as e:
                        conn.rollback()
                        st.error(f"❌ حدث خطأ أثناء حفظ السلفة: {e}")

        st.markdown("---")
        st.markdown("##### 📋 جدول السلف المسجلة (المعلقة والمخصومة)")
        
        advances_log_df = ui.df(conn, """
            SELECT ta.advance_id, t.full_name AS "المعلمة", ta.amount AS "مبلغ السلفة",
                   ta.advance_date AS "تاريخ السلفة", ta.salary_month AS "تخصم من شهر",
                   CASE WHEN ta.is_deducted THEN 'نعم (مخصومة)' ELSE 'لا (معلقة)' END AS "حالة الاستقطاع",
                   ta.notes AS "ملاحظات"
            FROM teacher_advances ta
            JOIN teachers t ON t.national_id = ta.national_id
            ORDER BY ta.advance_id DESC
        """)

        if advances_log_df.empty:
            ui.empty_state("لا توجد سلف مسجلة حتى الآن.")
        else:
            st.dataframe(advances_log_df.drop(columns=['advance_id']), use_container_width=True, hide_index=True)
            
            # Option to delete/cancel a pending advance
            st.markdown("##### ⚙️ حذف سلفة مسجلة")
            adv_options = [
                (int(r['advance_id']), f"سلفة #{int(r['advance_id'])} — {r['المعلمة']} — {r['مبلغ السلفة']} شيكل (شهر {r['تخصم من شهر']})")
                for _, r in advances_log_df.iterrows()
            ]
            sel_adv_to_del = st.selectbox("اختر السلفة للحذف أو الإلغاء", options=adv_options, format_func=lambda x: x[1] if x else "اختر...", index=None, placeholder="اختر سلفة...")
            if sel_adv_to_del:
                if st.button("🗑️ حذف السلفة المحددة", type="secondary"):
                    try:
                        cur = conn.cursor()
                        cur.execute("DELETE FROM teacher_advances WHERE advance_id = %s", (sel_adv_to_del[0],))
                        conn.commit()
                        cur.close()
                        st.success("🗑️ تم حذف السلفة بنجاح.")
                        st.rerun()
                    except Exception as e:
                        conn.rollback()
                        st.error(f"❌ حدث خطأ أثناء الحذف: {e}")

    # ---------------------------------- TAB 3: LOG, REPRINT, EDIT & DELETE --
    with tab_log:
        salary_logs = ui.df(conn, """
            SELECT tp.payment_id, tp.national_id, t.full_name AS "المعلمة",
                   tp.salary_month AS "عن شهر", tp.base_salary AS "الأساسي",
                   tp.bonus AS "المكافأة", tp.deductions AS "الخصم",
                   COALESCE(tp.advance, 0) AS "السلفة المستقطعة",
                   tp.amount AS "الصافي المدفوع", tp.payment_date AS "تاريخ الصرف",
                   tp.notes AS "ملاحظات"
            FROM teacher_payments tp
            JOIN teachers t ON t.national_id = tp.national_id
            ORDER BY tp.payment_id DESC
        """)

        if salary_logs.empty:
            ui.empty_state("لا توجد رواتب مدفوعة مسجلة بعد.")
        else:
            search = st.text_input("🔍 ابحث باسم المعلمة أو الشهر", key="search_salary_log")
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
                        advance=float(sal_row['السلفة المستقطعة']),
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

                        ec4, ec5, ec6 = st.columns(3)
                        e_deductions = ec4.number_input("الخصومات", min_value=0.0, value=float(sal_row['الخصم']), step=50.0)
                        e_advance = ec5.number_input("السلفة المستقطعة", min_value=0.0, value=float(sal_row['السلفة المستقطعة']), step=50.0)
                        e_notes = ec6.text_input("ملاحظات", value=sal_row['ملاحظات'] or "")

                        e_net = max(0.0, e_base + e_bonus - e_deductions - e_advance)
                        st.caption(f"💡 صافي الراتب الجديد بعد التعديل: **{H.format_money(e_net)} شيكل**")

                        btn1, btn2 = st.columns(2)
                        save_edit = btn1.form_submit_button("💾 حفظ التعديلات", type="primary", use_container_width=True)
                        delete_sal = btn2.form_submit_button("🗑️ حذف قسيمة الراتب", use_container_width=True)

                        if save_edit:
                            try:
                                cur = conn.cursor()
                                cur.execute("""
                                    UPDATE teacher_payments 
                                    SET salary_month=%s, base_salary=%s, bonus=%s, deductions=%s, advance=%s, amount=%s, notes=%s
                                    WHERE payment_id=%s
                                """, (e_month, e_base, e_bonus, e_deductions, e_advance, e_net, e_notes, p_id))
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