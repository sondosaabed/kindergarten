"""
sections/teachers.py — المعلمون

Add, view, edit and delete teaching staff records.
"""

import streamlit as st

import ui
import helpers as H


def render(conn):
    ui.section_header(" 👩‍🏫 ", "المعلمات", "بيانات الكادر التعليمي")

    tab_add, tab_view = st.tabs(["➕ إضافة معلم/ة", "📋 عرض / تعديل / حذف"])

    with tab_add:
        with st.form("add_teacher_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            national_id = c1.text_input("رقم الهوية")
            full_name = c2.text_input("الاسم الرباعي")
            mobile = c3.text_input("رقم الجوال")
            c4, c5, c6 = st.columns(3)
            salary = c4.number_input("الراتب", min_value=0.0, value=0.0, step=50.0)
            hire_date = c5.date_input("تاريخ التعيين")
            experience = c6.number_input("سنوات الخبرة", min_value=0, step=1)
            c7, c8 = st.columns(2)
            degree = c7.selectbox("المؤهل العلمي", H.DEGREES)
            specialization = c8.text_input("التخصص")
            address = st.text_input("عنوان السكن")

            submitted = st.form_submit_button("💾 حفظ بيانات المعلم/ة", type="primary")
            if submitted:
                if not national_id or not full_name or not mobile or not address:
                    st.warning("يرجى تعبئة جميع الحقول الأساسية (*).")
                else:
                    existing = ui.df(conn, "SELECT 1 FROM teachers WHERE national_id=?", (national_id,))
                    if not existing.empty:
                        st.error("رقم الهوية مسجل مسبقاً.")
                    else:
                        conn.execute('''
                            INSERT INTO teachers (national_id, full_name, salary, mobile, address,
                                hire_date, experience_years, degree, specialization)
                            VALUES (?,?,?,?,?,?,?,?,?)
                        ''', (national_id, full_name, salary, mobile, address, str(hire_date),
                              experience, degree, specialization))
                        conn.commit()
                        st.success(f"تم إضافة المعلم/ة «{full_name}» بنجاح! 🎉")
                        st.rerun()

    with tab_view:
        teachers = ui.df(conn, "SELECT * FROM teachers")
        if teachers.empty:
            ui.empty_state("لا يوجد معلمون مسجلون بعد.")
        else:
            st.dataframe(teachers.rename(columns={
                'national_id': 'رقم الهوية', 'full_name': 'الاسم', 'salary': 'الراتب',
                'mobile': 'الجوال', 'hire_date': 'تاريخ التعيين', 'experience_years': 'سنوات الخبرة',
                'degree': 'المؤهل', 'specialization': 'التخصص', 'address': 'العنوان'
            }), use_container_width=True, hide_index=True)

            st.divider()
            st.markdown("##### ✏️ تعديل أو حذف معلم/ة")
            pick = st.selectbox("اختر المعلم/ة", teachers['full_name'] + " — " + teachers['national_id'],
                                 index=None, placeholder="ابحث...")
            if pick:
                tid = pick.split(" — ")[-1]
                row = teachers[teachers['national_id'] == tid].iloc[0]
                with st.form("edit_teacher_form"):
                    c1, c2, c3 = st.columns(3)
                    e_name = c1.text_input("الاسم", value=row['full_name'])
                    e_salary = c2.number_input("الراتب", value=float(row['salary']))
                    e_mobile = c3.text_input("الجوال", value=row['mobile'])

                    b1, b2 = st.columns(2)
                    save = b1.form_submit_button("💾 حفظ التعديلات", type="primary")
                    delete = b2.form_submit_button("🗑️ حذف")

                    if save:
                        conn.execute("UPDATE teachers SET full_name=?, salary=?, mobile=? WHERE national_id=?",
                                     (e_name, e_salary, e_mobile, tid))
                        conn.commit()
                        st.success("تم حفظ التعديلات.")
                        st.rerun()
                    if delete:
                        linked = ui.df(conn, "SELECT COUNT(*) c FROM classes WHERE teacher_id=?", (tid,)).iloc[0]['c']
                        if linked > 0:
                            st.error(f"⚠️ هذا المعلم/ة مسؤول عن {linked} صف. يرجى إعادة تعيين الصف أولاً.")
                        else:
                            conn.execute("DELETE FROM teachers WHERE national_id=?", (tid,))
                            conn.commit()
                            st.success("تم الحذف.")
                            st.rerun()
