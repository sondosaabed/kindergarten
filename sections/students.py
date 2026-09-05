"""
sections/students.py — إدارة الطلاب

Add, search, edit and delete student records. Follows the same
reliability/UX pattern as parents.py: writes are wrapped in try/except
with conn.rollback() on failure (required under Postgres — a failed
statement otherwise leaves the connection in an aborted-transaction
state that breaks every query after it), record pickers use
(id, label) tuples with format_func instead of splitting strings, and
the edit form lives in a collapsible expander.
"""

import pandas as pd
import streamlit as st

import ui
import helpers as H


def render(conn):
    ui.section_header("🎒", "إدارة الطلاب", "إضافة وتعديل ومتابعة بيانات الأطفال")

    tab_add, tab_view = st.tabs(["➕ إضافة طالب جديد", "📋 عرض / تعديل / حذف"])

    parents_df = ui.df(conn, "SELECT father_id, father_name, mother_name FROM parents")
    parent_options = {
        f"{r.father_name} ({r.father_id}) — الأم: {r.mother_name}": r.father_id
        for r in parents_df.itertuples()
    }

    # -------------------------------------------------- TAB 1: ADD STUDENT --
    with tab_add:
        if parents_df.empty:
            ui.empty_state("يجب إضافة ولي أمر واحد على الأقل قبل تسجيل طالب. انتقل إلى صفحة «أولياء الأمور».")
        else:
            with st.form("add_student_form", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                student_id = c1.text_input("رقم هوية الطالب *", key="s_id").strip()
                full_name = c2.text_input("اسم الطالب الرباعي *", key="s_name").strip()
                birth_date = c3.date_input("تاريخ الميلاد *", key="s_bd", min_value=pd.Timestamp("2005-01-01"))

                c4, c5, c6 = st.columns(3)
                birth_place = c4.text_input("مكان الميلاد *", key="s_bp").strip()
                gender = c5.selectbox("الجنس *", H.GENDERS, key="s_gender")
                id_type = c6.selectbox("نوع الهوية *", H.STUDENT_ID_TYPES, key="s_idtype")

                c7, c8 = st.columns(2)
                nat_choice = c7.selectbox("الجنسية *", H.NATIONALITIES, key="s_nat")
                nationality = c7.text_input("حدد الجنسية", key="s_nat_other").strip() if nat_choice == "أخرى" else nat_choice
                father = c8.selectbox("ولي الأمر *", list(parent_options.keys()), key="s_parent")

                medical = st.checkbox("هل يوجد حالة طبية؟", key="s_medical")
                medical_details = st.text_area("تفاصيل الحالة الطبية (اختياري)", key="s_med_details") if medical else ""

                submitted = st.form_submit_button("💾 حفظ بيانات الطالب", type="primary", use_container_width=True)

                if submitted:
                    if not student_id or not full_name or not birth_place:
                        st.warning("⚠️ يرجى تعبئة جميع الحقول الأساسية (*).")
                    else:
                        existing = ui.df(conn, "SELECT 1 FROM students WHERE student_id = %s", (student_id,))
                        if not existing.empty:
                            st.error("❌ رقم هوية الطالب مسجل مسبقاً. يرجى التحقق أو استخدام تبويب التعديل.")
                        else:
                            try:
                                cur = conn.cursor()
                                cur.execute('''
                                    INSERT INTO students
                                    (student_id, full_name, birth_date, birth_place, gender, id_type,
                                     nationality, has_medical_condition, medical_details, father_id, created_at)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ''', (student_id, full_name, str(birth_date), birth_place, gender, id_type,
                                      nationality, 1 if medical else 0, medical_details,
                                      parent_options[father], H.now_str()))
                                conn.commit()
                                cur.close()
                                st.success(f"✅ تم تسجيل الطالب «{full_name}» بنجاح! 🎉")
                                st.rerun()
                            except Exception as e:
                                conn.rollback()
                                st.error(f"❌ حدث خطأ أثناء الحفظ: {e}")

    # ------------------------------------------- TAB 2: VIEW / EDIT / DELETE --
    with tab_view:
        students = ui.df(conn, """
            SELECT s.student_id, s.full_name, s.birth_date, s.gender, s.id_type,
                   s.nationality, s.has_medical_condition, s.medical_details,
                   s.father_id, p.father_name
            FROM students s JOIN parents p ON s.father_id = p.father_id
            ORDER BY s.created_at DESC
        """)
        if students.empty:
            ui.empty_state("لا يوجد طلاب مسجلون بعد.")
        else:
            search = st.text_input("🔍 ابحث بالاسم أو رقم الهوية")
            shown = students.copy()
            if search:
                shown = shown[shown['full_name'].str.contains(search, na=False) |
                               shown['student_id'].str.contains(search, na=False)]
            shown['العمر'] = shown['birth_date'].apply(H.calculate_age)
            display_cols = shown.rename(columns={
                'student_id': 'رقم الهوية', 'full_name': 'الاسم', 'birth_date': 'تاريخ الميلاد',
                'gender': 'الجنس', 'id_type': 'نوع الهوية', 'nationality': 'الجنسية',
                'father_name': 'ولي الأمر'
            })[['رقم الهوية', 'الاسم', 'العمر', 'تاريخ الميلاد', 'الجنس', 'نوع الهوية', 'الجنسية', 'ولي الأمر']]
            st.dataframe(display_cols, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("##### ✏️ تعديل أو حذف طالب")

            student_options = [
                (row['student_id'], f"{row['full_name']} — [هوية: {row['student_id']}]")
                for _, row in students.iterrows()
            ]
            selected = st.selectbox(
                "اختر الطالب", options=student_options,
                format_func=lambda x: x[1] if x else "اختر...",
                index=None, placeholder="ابحث عن طالب...", key="student_select_edit",
            )

            if selected:
                sid = selected[0]
                row = students[students['student_id'] == sid].iloc[0]

                with st.expander(f"⚙️ تعديل بيانات: {row['full_name']}", expanded=True):
                    with st.form("edit_student_form"):
                        c1, c2, c3 = st.columns(3)
                        e_name = c1.text_input("اسم الطالب", value=row['full_name'])
                        e_bd = c2.date_input("تاريخ الميلاد", value=pd.to_datetime(row['birth_date']))
                        e_gender = c3.selectbox("الجنس", H.GENDERS, index=H.GENDERS.index(row['gender']))

                        c4, c5 = st.columns(2)
                        e_idtype = c4.selectbox(
                            "نوع الهوية", H.STUDENT_ID_TYPES,
                            index=H.STUDENT_ID_TYPES.index(row['id_type']) if row['id_type'] in H.STUDENT_ID_TYPES else 0
                        )
                        e_nat = c5.text_input("الجنسية", value=row['nationality'])

                        e_medical = st.checkbox("يوجد حالة طبية", value=bool(row['has_medical_condition']))
                        e_med_details = st.text_area("تفاصيل الحالة الطبية", value=row['medical_details'] or "")

                        b1, b2 = st.columns(2)
                        save = b1.form_submit_button("💾 حفظ التعديلات", type="primary", use_container_width=True)
                        delete = b2.form_submit_button("🗑️ حذف الطالب", use_container_width=True)

                        if save:
                            try:
                                cur = conn.cursor()
                                cur.execute('''
                                    UPDATE students SET full_name=%s, birth_date=%s, gender=%s, id_type=%s,
                                        nationality=%s, has_medical_condition=%s, medical_details=%s
                                    WHERE student_id=%s
                                ''', (e_name, str(e_bd), e_gender, e_idtype, e_nat,
                                      1 if e_medical else 0, e_med_details, sid))
                                conn.commit()
                                cur.close()
                                st.success("✅ تم حفظ التعديلات.")
                                st.rerun()
                            except Exception as e:
                                conn.rollback()
                                st.error(f"❌ حدث خطأ أثناء الحفظ: {e}")

                        if delete:
                            try:
                                cur = conn.cursor()
                                cur.execute("DELETE FROM students WHERE student_id=%s", (sid,))
                                conn.commit()
                                cur.close()
                                st.warning("🗑️ تم حذف الطالب بنجاح!")
                                st.rerun()
                            except Exception as e:
                                conn.rollback()
                                st.error(f"❌ حدث خطأ أثناء الحذف: {e}")
