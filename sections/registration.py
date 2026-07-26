"""
sections/registration.py — التسجيل المدرسي

Registers a student into a class for a given academic year. Requires at
least one student, one class and one academic year to already exist.
"""

import streamlit as st

import ui
import helpers as H


def render(conn):
    ui.section_header(" 📝 ", "التسجيل المدرسي", "تسجيل طالب في صف لسنة دراسية محددة")

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

    tab_add, tab_view = st.tabs(["➕ تسجيل جديد", "📋 كل التسجيلات"])

    with tab_add:
        student_options = {r.full_name + " — " + r.student_id: r.student_id for r in students_df.itertuples()}
        classes_df['label'] = classes_df['class_type'] + " " + classes_df['section'] + \
                               classes_df['class_name'].fillna('').apply(lambda x: f" ({x})" if x else "")
        class_options = {r.label: r.class_id for r in classes_df.itertuples()}

        with st.form("add_registration_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            student_label = c1.selectbox("الطالب", list(student_options.keys()))
            class_label = c2.selectbox("الصف والشعبة", list(class_options.keys()))
            year_label = c3.selectbox("السنة الدراسية", years_df['year_id'])

            submitted = st.form_submit_button("💾 تسجيل الطالب", type="primary")
            if submitted:
                sid = student_options[student_label]
                cid = class_options[class_label]
                existing = ui.df(conn, "SELECT 1 FROM registrations WHERE student_id=? AND year_id=?", (sid, year_label))
                if not existing.empty:
                    st.error("هذا الطالب مسجل مسبقاً في هذه السنة الدراسية.")
                else:
                    conn.execute('''
                        INSERT INTO registrations (student_id, class_id, year_id, status, registration_date)
                        VALUES (?,?,?,?,?)
                    ''', (sid, cid, year_label, H.STATUS_NEW, H.today_str()))
                    conn.commit()
                    st.success(f"تم تسجيل «{student_label.split(' — ')[0]}» بنجاح! الحالة الحالية: {H.STATUS_NEW}. "
                               "توجّه إلى صفحة «الدفعات المالية» لتحصيل رسوم التسجيل.")
                    st.rerun()

    with tab_view:
        regs = ui.df(conn, """
            SELECT r.registration_id, s.full_name AS "اسم الطالب",
                   (c.class_type || ' ' || c.section) AS "الصف", r.year_id AS "السنة الدراسية",
                   r.status AS "الحالة", r.registration_date AS "تاريخ التسجيل"
            FROM registrations r
            JOIN students s ON s.student_id = r.student_id
            JOIN classes c ON c.class_id = r.class_id
            ORDER BY r.registration_id DESC
        """)
        if regs.empty:
            ui.empty_state("لا توجد تسجيلات بعد.")
        else:
            f1, f2 = st.columns(2)
            year_filter = f1.selectbox("تصفية حسب السنة", ["الكل"] + sorted(regs["السنة الدراسية"].unique().tolist()))
            status_filter = f2.selectbox("تصفية حسب الحالة", ["الكل", H.STATUS_NEW, H.STATUS_ACTIVE])
            shown = regs.copy()
            if year_filter != "الكل":
                shown = shown[shown["السنة الدراسية"] == year_filter]
            if status_filter != "الكل":
                shown = shown[shown["الحالة"] == status_filter]
            st.dataframe(shown, use_container_width=True, hide_index=True)
