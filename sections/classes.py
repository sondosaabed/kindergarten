"""
sections/classes.py — الصفوف

Add, view, edit and delete classes (class_type + section), and assign
the responsible teacher.
"""

import pandas as pd
import streamlit as st

import ui
import helpers as H


def render(conn):
    ui.section_header("🏷️", "الصفوف", "تنظيم الشعب وتعيين المعلمات")

    tab_add, tab_view = st.tabs(["➕ إضافة صف", "📋 عرض / تعديل / حذف"])

    teachers_df = ui.df(conn, "SELECT national_id, full_name FROM teachers")
    teacher_options = {"— بدون تعيين —": None}
    teacher_options.update({r.full_name: r.national_id for r in teachers_df.itertuples()})

    with tab_add:
        with st.form("add_class_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            class_type = c1.selectbox("نوع الصف", H.CLASS_TYPES)
            section = c2.selectbox("الشعبة", H.SECTIONS)
            class_name = c3.text_input("اسم الصف (اختياري)", placeholder="مثال: صف الورود")
            teacher_label = st.selectbox("المعلم/ة المسؤول/ة", list(teacher_options.keys()))

            submitted = st.form_submit_button("💾 حفظ الصف", type="primary")
            if submitted:
                existing = ui.df(conn, "SELECT 1 FROM classes WHERE class_type=? AND section=?", (class_type, section))
                if not existing.empty:
                    st.error("هذا الصف (النوع + الشعبة) موجود مسبقاً.")
                else:
                    conn.execute('''
                        INSERT INTO classes (class_type, section, class_name, teacher_id)
                        VALUES (?,?,?,?)
                    ''', (class_type, section, class_name, teacher_options[teacher_label]))
                    conn.commit()
                    st.success("تم إضافة الصف بنجاح! 🎉")
                    st.rerun()

    with tab_view:
        classes = ui.df(conn, """
            SELECT c.class_id, c.class_type, c.section, c.class_name, t.full_name AS teacher_name,
                   c.teacher_id
            FROM classes c LEFT JOIN teachers t ON c.teacher_id = t.national_id
        """)
        if classes.empty:
            ui.empty_state("لا توجد صفوف بعد.")
        else:
            counts = ui.df(conn, """
                SELECT class_id, COUNT(*) AS n FROM registrations
                WHERE year_id = (SELECT year_id FROM academic_years ORDER BY start_date DESC LIMIT 1)
                GROUP BY class_id
            """)
            classes = classes.merge(counts, on='class_id', how='left').fillna({'n': 0})
            st.dataframe(classes.rename(columns={
                'class_type': 'النوع', 'section': 'الشعبة', 'class_name': 'الاسم',
                'teacher_name': 'المعلم/ة المسؤول/ة', 'n': 'عدد الطلاب (السنة الحالية)'
            })[['النوع', 'الشعبة', 'الاسم', 'المعلم/ة المسؤول/ة', 'عدد الطلاب (السنة الحالية)']],
                use_container_width=True, hide_index=True)

            st.divider()
            st.markdown("##### ✏️ تعديل أو حذف صف")
            classes['label'] = classes['class_type'] + " " + classes['section'] + \
                                classes['class_name'].fillna('').apply(lambda x: f" ({x})" if x else "")
            pick = st.selectbox("اختر الصف", classes['label'], index=None, placeholder="اختر...")
            if pick:
                row = classes[classes['label'] == pick].iloc[0]
                with st.form("edit_class_form"):
                    e_name = st.text_input("اسم الصف", value=row['class_name'] or "")
                    current_teacher = row['teacher_name'] if pd.notna(row['teacher_name']) else "— بدون تعيين —"
                    idx = list(teacher_options.keys()).index(current_teacher) if current_teacher in teacher_options else 0
                    e_teacher = st.selectbox("المعلم/ة المسؤول/ة", list(teacher_options.keys()), index=idx)

                    b1, b2 = st.columns(2)
                    save = b1.form_submit_button("💾 حفظ", type="primary")
                    delete = b2.form_submit_button("🗑️ حذف الصف")

                    if save:
                        conn.execute("UPDATE classes SET class_name=?, teacher_id=? WHERE class_id=?",
                                     (e_name, teacher_options[e_teacher], int(row['class_id'])))
                        conn.commit()
                        st.success("تم الحفظ.")
                        st.rerun()
                    if delete:
                        linked = ui.df(conn, "SELECT COUNT(*) c FROM registrations WHERE class_id=?", (int(row['class_id']),)).iloc[0]['c']
                        if linked > 0:
                            st.error(f"⚠️ يوجد {linked} تسجيل مرتبط بهذا الصف. لا يمكن الحذف.")
                        else:
                            conn.execute("DELETE FROM classes WHERE class_id=?", (int(row['class_id']),))
                            conn.commit()
                            st.success("تم الحذف.")
                            st.rerun()
