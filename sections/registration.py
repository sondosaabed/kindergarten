"""
sections/registration.py — التسجيل المدرسي

Registers a student into a class for a given academic year, and now
also supports reassigning a student to a different class/section or
removing a registration — following the same reliability/UX pattern as
parents.py: try/except + conn.rollback() around every write, (id, label)
tuple pickers, edit form in an expander.
"""

import streamlit as st

import ui
import helpers as H


def render(conn):
    ui.section_header("📝", "التسجيل المدرسي", "تسجيل طالب في صف لسنة دراسية محددة")

    students_df = ui.df(conn, "SELECT student_id, full_name FROM students")
    classes_df = ui.df(conn, "SELECT class_id, class_type, section, class_name FROM classes")
    years_df = ui.df(conn, "SELECT year_id FROM academic_years ORDER BY start_date DESC")

    if students_df.empty or classes_df.empty or years_df.empty:
        missing = []
        if students_df.empty: missing.append("طالب")
        if classes_df.empty: missing.append("صف")
        if years_df.empty: missing.append("سنة دراسية")
        ui.empty_state(f"يجب إضافة كل من: {'، '.join(missing)} قبل إجراء التسجيل.")
        return

    classes_df['label'] = classes_df['class_type'] + " " + classes_df['section'] + \
                           classes_df['class_name'].fillna('').apply(lambda x: f" ({x})" if x else "")

    tab_add, tab_view = st.tabs(["➕ تسجيل جديد", "📋 كل التسجيلات"])

    # -------------------------------------------------- TAB 1: ADD REGISTRATION --
    with tab_add:
        student_options = {r.full_name + " — " + r.student_id: r.student_id for r in students_df.itertuples()}
        class_options = {r.label: r.class_id for r in classes_df.itertuples()}

        with st.form("add_registration_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            student_label = c1.selectbox("الطالب *", list(student_options.keys()))
            class_label = c2.selectbox("الصف والشعبة *", list(class_options.keys()))
            year_label = c3.selectbox("السنة الدراسية *", years_df['year_id'])

            submitted = st.form_submit_button("💾 تسجيل الطالب", type="primary", use_container_width=True)

            if submitted:
                sid = student_options[student_label]
                cid = class_options[class_label]
                existing = ui.df(
                    conn,
                    "SELECT 1 FROM registrations WHERE student_id=%s AND year_id=%s",
                    (sid, year_label)
                )
                if not existing.empty:
                    st.error("❌ هذا الطالب مسجل مسبقاً في هذه السنة الدراسية.")
                else:
                    try:
                        cur = conn.cursor()
                        cur.execute('''
                            INSERT INTO registrations (student_id, class_id, year_id, status, registration_date)
                            VALUES (%s, %s, %s, %s, %s)
                        ''', (sid, cid, year_label, H.STATUS_NEW, H.today_str()))
                        conn.commit()
                        cur.close()
                        st.success(f"✅ تم تسجيل «{student_label.split(' — ')[0]}» بنجاح! الحالة الحالية: {H.STATUS_NEW}. "
                                   "توجّه إلى صفحة «الدفعات المالية» لتحصيل رسوم التسجيل.")
                        st.rerun()
                    except Exception as e:
                        conn.rollback()
                        st.error(f"❌ حدث خطأ أثناء التسجيل: {e}")

    # ------------------------------------------- TAB 2: VIEW / EDIT / DELETE --
    with tab_view:
        regs = ui.df(conn, """
            SELECT r.registration_id, s.full_name AS "اسم الطالب",
                   (c.class_type || ' ' || c.section) AS "الصف", r.year_id AS "السنة الدراسية",
                   r.status AS "الحالة", r.registration_date AS "تاريخ التسجيل", r.class_id,
                   COALESCE((SELECT SUM(p.amount) FROM payments p
                             WHERE p.registration_id = r.registration_id
                               AND p.payment_for IN ('رسوم تسجيل', 'أقساط تعليمية')), 0) AS paid_toward_tuition
            FROM registrations r
            JOIN students s ON s.student_id = r.student_id
            JOIN classes c ON c.class_id = r.class_id
            ORDER BY r.registration_id DESC
        """)
        if regs.empty:
            ui.empty_state("لا توجد تسجيلات بعد.")
        else:
            regs["المبلغ المتبقي"] = (H.ANNUAL_TUITION - regs["paid_toward_tuition"].astype(float)).clip(lower=0)

            f1, f2 = st.columns(2)
            year_filter = f1.selectbox("تصفية حسب السنة", ["الكل"] + sorted(regs["السنة الدراسية"].unique().tolist()))
            status_filter = f2.selectbox("تصفية حسب الحالة", ["الكل", H.STATUS_NEW, H.STATUS_ACTIVE])
            shown = regs.copy()
            if year_filter != "الكل":
                shown = shown[shown["السنة الدراسية"] == year_filter]
            if status_filter != "الكل":
                shown = shown[shown["الحالة"] == status_filter]
            st.dataframe(
                shown.drop(columns=["registration_id", "class_id", "paid_toward_tuition"]),
                use_container_width=True, hide_index=True
            )
            st.caption(f"💡 الرسوم السنوية لكل طالب: {H.format_money(H.ANNUAL_TUITION)} شيكل/دينار (شاملة رسوم التسجيل).")

            st.markdown("---")
            st.markdown("##### ✏️ تعديل (نقل صف) أو حذف تسجيل")

            reg_options = [
                (int(row['registration_id']),
                 f"{row['اسم الطالب']} — {row['الصف']} — {row['السنة الدراسية']} ({row['الحالة']})")
                for _, row in regs.iterrows()
            ]
            selected = st.selectbox(
                "اختر التسجيل", options=reg_options,
                format_func=lambda x: x[1] if x else "اختر...",
                index=None, placeholder="اختر...", key="reg_select_edit",
            )

            if selected:
                rid = selected[0]
                row = regs[regs['registration_id'] == rid].iloc[0]

                with st.expander(f"⚙️ تعديل: {selected[1]}", expanded=True):
                    with st.form("edit_registration_form"):
                        class_label_options = list(class_options.keys())
                        current_label = classes_df.loc[classes_df['class_id'] == row['class_id'], 'label']
                        current_idx = class_label_options.index(current_label.iloc[0]) if not current_label.empty else 0
                        new_class_label = st.selectbox("نقل إلى صف", class_label_options, index=current_idx)

                        b1, b2 = st.columns(2)
                        save = b1.form_submit_button("💾 حفظ نقل الصف", type="primary", use_container_width=True)
                        delete = b2.form_submit_button("🗑️ حذف التسجيل", use_container_width=True)

                        if save:
                            try:
                                cur = conn.cursor()
                                cur.execute("UPDATE registrations SET class_id=%s WHERE registration_id=%s",
                                            (class_options[new_class_label], rid))
                                conn.commit()
                                cur.close()
                                st.success("✅ تم نقل الطالب إلى الصف الجديد.")
                                st.rerun()
                            except Exception as e:
                                conn.rollback()
                                st.error(f"❌ حدث خطأ أثناء الحفظ: {e}")

                        if delete:
                            linked_df = ui.df(conn, "SELECT COUNT(*) AS c FROM payments WHERE registration_id=%s", (rid,))
                            linked = linked_df.iloc[0]['c'] if not linked_df.empty else 0
                            if linked > 0:
                                st.error(f"⚠️ يوجد {linked} دفعة مرتبطة بهذا التسجيل. لا يمكن الحذف قبل إزالتها.")
                            else:
                                try:
                                    cur = conn.cursor()
                                    cur.execute("DELETE FROM registrations WHERE registration_id=%s", (rid,))
                                    conn.commit()
                                    cur.close()
                                    st.warning("🗑️ تم حذف التسجيل بنجاح!")
                                    st.rerun()
                                except Exception as e:
                                    conn.rollback()
                                    st.error(f"❌ حدث خطأ أثناء الحذف: {e}")
