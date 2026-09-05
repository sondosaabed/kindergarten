"""
sections/payments.py — الدفعات المالية

Records a cash payment against a registration, updates the registration's
status automatically, shows the remaining yearly balance, and offers a
one-click printable receipt. Also supports correcting or removing a
mistaken payment — following the same reliability/UX pattern as
parents.py: try/except + conn.rollback() around every write, (id, label)
tuple pickers, edit form in an expander.
"""

import streamlit as st

import ui
import helpers as H
import receipt


def render(conn):
    ui.section_header("💵", "الدفعات المالية", "تسجيل دفعة نقدية وطباعة وصل استلام")

    active_regs = ui.df(conn, """
        SELECT r.registration_id, s.full_name AS student_name, p.father_name,
               (c.class_type || ' ' || c.section) AS class_label, r.year_id, r.status
        FROM registrations r
        JOIN students s ON s.student_id = r.student_id
        JOIN classes c ON c.class_id = r.class_id
        JOIN parents p ON p.father_id = s.father_id
        ORDER BY r.registration_id DESC
    """)

    if active_regs.empty:
        ui.empty_state("لا يوجد طلاب مسجلون بعد. قم بتسجيل طالب أولاً من صفحة «التسجيل».")
        return

    tab_add, tab_view = st.tabs(["➕ تسجيل دفعة كاش", "📋 سجل الدفعات"])

    # -------------------------------------------------- TAB 1: ADD PAYMENT --
    with tab_add:
        active_regs['label'] = (active_regs['student_name'] + "  |  " + active_regs['class_label'] +
                                 "  |  " + active_regs['year_id'] + "  (" + active_regs['status'] + ")")
        reg_dict = dict(zip(active_regs['label'], active_regs['registration_id']))
        selected_label = st.selectbox("اختر الطالب والتسجيل", list(reg_dict.keys()))
        selected_row = active_regs[active_regs['label'] == selected_label].iloc[0]
        reg_id_preview = int(selected_row['registration_id'])

        paid_so_far = H.compute_paid_toward_tuition(conn, reg_id_preview)
        remaining_before = H.compute_remaining_balance(conn, reg_id_preview)
        i1, i2, i3 = st.columns(3)
        i1.metric("الرسوم السنوية", f"{H.format_money(H.ANNUAL_TUITION)}")
        i2.metric("المدفوع حتى الآن", f"{H.format_money(paid_so_far)}")
        i3.metric("المتبقي", f"{H.format_money(remaining_before)}")

        with st.form("add_payment_form"):
            c1, c2 = st.columns(2)
            amount = c1.number_input("المبلغ المدفوع (كاش) *", min_value=1.0, value=100.0, step=10.0)
            payer = c2.text_input("اسم الدافع (ولي الأمر) *", value=selected_row['father_name'])

            c3, c4 = st.columns(2)
            reason = c3.selectbox("مقابل *", H.PAYMENT_FOR)
            reason_other = c4.text_input("تفاصيل أخرى") if reason == "آخر" else ""

            submitted = st.form_submit_button("🧾 حفظ الدفعة وطباعة الوصل", type="primary", use_container_width=True)

        if submitted:
            reg_id = int(selected_row['registration_id'])
            today = H.today_str()
            try:
                cur = conn.cursor()
                cur.execute('''
                    INSERT INTO payments (registration_id, amount, payment_date, payment_method,
                        payer_name, payment_for, payment_for_other)
                    VALUES (%s, %s, %s, 'كاش', %s, %s, %s)
                    RETURNING receipt_number
                ''', (reg_id, amount, today, payer, reason, reason_other))
                receipt_id = cur.fetchone()['receipt_number']
                conn.commit()
                cur.close()
            except Exception as e:
                conn.rollback()
                st.error(f"❌ حدث خطأ أثناء حفظ الدفعة: {e}")
            else:
                new_status = H.refresh_registration_status(conn, reg_id)
                remaining_after = H.compute_remaining_balance(conn, reg_id)

                st.success(f"✅ تم حفظ الدفعة بنجاح! رقم الوصل: #{receipt_id} — حالة التسجيل الآن: {new_status}")

                receipt.render_receipt(
                    receipt_id=receipt_id,
                    date=today,
                    student_name=selected_row['student_name'],
                    payer=payer,
                    amount=H.format_money(amount),
                    reason=reason,
                    remaining=H.format_money(remaining_after),
                    reason_other=reason_other,
                )

    # ------------------------------------------- TAB 2: VIEW / EDIT / DELETE --
    with tab_view:
        payments = ui.df(conn, """
            SELECT p.receipt_number AS "رقم الوصل", s.full_name AS "اسم الطالب",
                   p.amount AS "المبلغ", p.payment_date AS "التاريخ",
                   p.payer_name AS "الدافع", p.payment_for AS "مقابل", p.registration_id
            FROM payments p
            JOIN registrations r ON p.registration_id = r.registration_id
            JOIN students s ON r.student_id = s.student_id
            ORDER BY p.receipt_number DESC
        """)
        if payments.empty:
            ui.empty_state("لا توجد دفعات مسجلة بعد.")
        else:
            search = st.text_input("🔍 ابحث باسم الطالب أو الدافع")
            shown = payments.copy()
            if search:
                shown = shown[shown["اسم الطالب"].str.contains(search, na=False) |
                               shown["الدافع"].str.contains(search, na=False)]
            st.dataframe(shown.drop(columns=["registration_id"]), use_container_width=True, hide_index=True)
            st.metric("💰 مجموع الدفعات المعروضة", H.format_money(shown["المبلغ"].sum()))

            st.markdown("---")
            st.markdown("##### ✏️ تعديل أو حذف دفعة (لتصحيح خطأ إدخال)")

            pay_options = [
                (int(row['رقم الوصل']), f"وصل #{int(row['رقم الوصل'])} — {row['اسم الطالب']} — {H.format_money(row['المبلغ'])}")
                for _, row in payments.iterrows()
            ]
            selected = st.selectbox(
                "اختر الدفعة", options=pay_options,
                format_func=lambda x: x[1] if x else "اختر...",
                index=None, placeholder="اختر...", key="payment_select_edit",
            )

            if selected:
                receipt_no = selected[0]
                row = payments[payments['رقم الوصل'] == receipt_no].iloc[0]

                with st.expander(f"⚙️ تعديل: {selected[1]}", expanded=True):
                    with st.form("edit_payment_form"):
                        c1, c2 = st.columns(2)
                        e_amount = c1.number_input("المبلغ", min_value=0.0, value=float(row['المبلغ']), step=10.0)
                        e_payer = c2.text_input("اسم الدافع", value=row['الدافع'])
                        e_reason = st.selectbox(
                            "مقابل", H.PAYMENT_FOR,
                            index=H.PAYMENT_FOR.index(row['مقابل']) if row['مقابل'] in H.PAYMENT_FOR else 0
                        )

                        b1, b2 = st.columns(2)
                        save = b1.form_submit_button("💾 حفظ التعديلات", type="primary", use_container_width=True)
                        delete = b2.form_submit_button("🗑️ حذف الدفعة", use_container_width=True)

                        if save:
                            try:
                                cur = conn.cursor()
                                cur.execute('''
                                    UPDATE payments SET amount=%s, payer_name=%s, payment_for=%s
                                    WHERE receipt_number=%s
                                ''', (e_amount, e_payer, e_reason, receipt_no))
                                conn.commit()
                                cur.close()
                                H.refresh_registration_status(conn, int(row['registration_id']))
                                st.success("✅ تم حفظ التعديلات.")
                                st.rerun()
                            except Exception as e:
                                conn.rollback()
                                st.error(f"❌ حدث خطأ أثناء الحفظ: {e}")

                        if delete:
                            try:
                                cur = conn.cursor()
                                cur.execute("DELETE FROM payments WHERE receipt_number=%s", (receipt_no,))
                                conn.commit()
                                cur.close()
                                H.refresh_registration_status(conn, int(row['registration_id']))
                                st.warning("🗑️ تم حذف الدفعة بنجاح! تم تحديث حالة التسجيل والمبلغ المتبقي تلقائياً.")
                                st.rerun()
                            except Exception as e:
                                conn.rollback()
                                st.error(f"❌ حدث خطأ أثناء الحذف: {e}")
