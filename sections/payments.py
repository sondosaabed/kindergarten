"""
sections/payments.py — الدفعات المالية

Records a cash payment against a registration, updates the registration's
status automatically, and offers a one-click printable receipt (see
receipt.py) instead of relying on the browser's Ctrl/Cmd+P.
"""

import streamlit as st

import ui
import helpers as H
import receipt


def render(conn):
    ui.section_header(" 💵 ", "الدفعات المالية", "تسجيل دفعة نقدية وطباعة وصل استلام")

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

    with tab_add:
        active_regs['label'] = (active_regs['student_name'] + "  |  " + active_regs['class_label'] +
                                 "  |  " + active_regs['year_id'] + "  (" + active_regs['status'] + ")")
        reg_dict = dict(zip(active_regs['label'], active_regs['registration_id']))
        selected_label = st.selectbox("اختر الطالب والتسجيل", list(reg_dict.keys()))
        selected_row = active_regs[active_regs['label'] == selected_label].iloc[0]

        with st.form("add_payment_form"):
            c1, c2 = st.columns(2)
            amount = c1.number_input("المبلغ المدفوع (كاش)", min_value=1.0, value=100.0, step=10.0)
            payer = c2.text_input("اسم الدافع (ولي الأمر)", value=selected_row['father_name'])

            c3, c4 = st.columns(2)
            reason = c3.selectbox("مقابل", H.PAYMENT_FOR)
            reason_other = c4.text_input("تفاصيل أخرى") if reason == "آخر" else ""

            submitted = st.form_submit_button("🧾 حفظ الدفعة وطباعة الوصل", type="primary")

        if submitted:
            reg_id = int(selected_row['registration_id'])
            today = H.today_str()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO payments (registration_id, amount, payment_date, payment_method,
                    payer_name, payment_for, payment_for_other)
                VALUES (?, ?, ?, 'كاش', ?, ?, ?)
            ''', (reg_id, amount, today, payer, reason, reason_other))
            conn.commit()
            receipt_id = cur.lastrowid
            new_status = H.refresh_registration_status(conn, reg_id)

            st.success(f"تم حفظ الدفعة بنجاح! رقم الوصل: #{receipt_id} — حالة التسجيل الآن: {new_status}")

            receipt.render_receipt(
                receipt_id=receipt_id,
                date=today,
                student_name=selected_row['student_name'],
                payer=payer,
                amount=H.format_money(amount),
                reason=reason,
                reason_other=reason_other,
            )

    with tab_view:
        payments = ui.df(conn, """
            SELECT p.receipt_number AS "رقم الوصل", s.full_name AS "اسم الطالب",
                   p.amount AS "المبلغ", p.payment_date AS "التاريخ",
                   p.payer_name AS "الدافع", p.payment_for AS "مقابل"
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
            st.dataframe(shown, use_container_width=True, hide_index=True)
            st.metric("💰 مجموع الدفعات المعروضة", H.format_money(shown["المبلغ"].sum()))
