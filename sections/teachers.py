"""
sections/teachers.py — المعلمون

Add, view, edit and delete teaching staff records. Same reliability/UX
pattern as parents.py: try/except + conn.rollback() around every write,
(id, label) tuple pickers, edit form in an expander.
"""

import streamlit as st

import ui
import helpers as H


def render(conn):
    ui.section_header("👩‍🏫", "المعلمون", "بيانات الكادر التعليمي")

    tab_add, tab_view = st.tabs(["➕ إضافة معلم/ة", "📋 عرض / تعديل / حذف"])

    # -------------------------------------------------- TAB 1: ADD TEACHER --
    with tab_add:
        with st.form("add_teacher_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            national_id = c1.text_input("رقم الهوية *").strip()
            full_name = c2.text_input("الاسم الرباعي *").strip()
            mobile = c3.text_input("رقم الجوال *").strip()
            c4, c5, c6 = st.columns(3)
            salary = c4.number_input("الراتب *", min_value=0.0, value=0.0, step=50.0)
            hire_date = c5.date_input("تاريخ التعيين *")
            experience = c6.number_input("سنوات الخبرة *", min_value=0, step=1)
            c7, c8 = st.columns(2)
            degree = c7.selectbox("المؤهل العلمي *", H.DEGREES)
            specialization = c8.text_input("التخصص")
            address = st.text_input("عنوان السكن *").strip()

            submitted = st.form_submit_button("💾 حفظ بيانات المعلم/ة", type="primary", use_container_width=True)

            if submitted:
                if not national_id or not full_name or not mobile or not address:
                    st.warning("⚠️ يرجى تعبئة جميع الحقول الأساسية (*).")
                else:
                    existing = ui.df(conn, "SELECT 1 FROM teachers WHERE national_id=%s", (national_id,))
                    if not existing.empty:
                        st.error("❌ رقم الهوية مسجل مسبقاً.")
                    else:
                        try:
                            cur = conn.cursor()
                            cur.execute('''
                                INSERT INTO teachers (national_id, full_name, salary, mobile, address,
                                    hire_date, experience_years, degree, specialization)
                                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                            ''', (national_id, full_name, salary, mobile, address, str(hire_date),
                                  experience, degree, specialization))
                            conn.commit()
                            cur.close()
                            st.success(f"✅ تم إضافة المعلم/ة «{full_name}» بنجاح! 🎉")
                            st.rerun()
                        except Exception as e:
                            conn.rollback()
                            st.error(f"❌ حدث خطأ أثناء الحفظ: {e}")

    # ------------------------------------------- TAB 2: VIEW / EDIT / DELETE --
    with tab_view:
        teachers = ui.df(conn, "SELECT * FROM teachers ORDER BY full_name ASC")
        if teachers.empty:
            ui.empty_state("لا يوجد معلمون مسجلون بعد.")
        else:
            st.dataframe(teachers.rename(columns={
                'national_id': 'رقم الهوية', 'full_name': 'الاسم', 'salary': 'الراتب',
                'mobile': 'الجوال', 'hire_date': 'تاريخ التعيين', 'experience_years': 'سنوات الخبرة',
                'degree': 'المؤهل', 'specialization': 'التخصص', 'address': 'العنوان'
            }), use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("##### ✏️ تعديل أو حذف معلم/ة")

            teacher_options = [
                (row['national_id'], f"{row['full_name']} — [هوية: {row['national_id']}]")
                for _, row in teachers.iterrows()
            ]
            selected = st.selectbox(
                "اختر المعلم/ة", options=teacher_options,
                format_func=lambda x: x[1] if x else "اختر...",
                index=None, placeholder="ابحث...", key="teacher_select_edit",
            )

            if selected:
                tid = selected[0]
                row = teachers[teachers['national_id'] == tid].iloc[0]

                with st.expander(f"⚙️ تعديل بيانات: {row['full_name']}", expanded=True):
                    with st.form("edit_teacher_form"):
                        c1, c2, c3 = st.columns(3)
                        e_name = c1.text_input("الاسم", value=row['full_name'])
                        e_salary = c2.number_input("الراتب", value=float(row['salary']))
                        e_mobile = c3.text_input("الجوال", value=row['mobile'])

                        c4, c5 = st.columns(2)
                        e_address = c4.text_input("عنوان السكن", value=row['address'])
                        e_specialization = c5.text_input("التخصص", value=row['specialization'] or "")

                        b1, b2 = st.columns(2)
                        save = b1.form_submit_button("💾 حفظ التعديلات", type="primary", use_container_width=True)
                        delete = b2.form_submit_button("🗑️ حذف", use_container_width=True)

                        if save:
                            try:
                                cur = conn.cursor()
                                cur.execute('''
                                    UPDATE teachers SET full_name=%s, salary=%s, mobile=%s,
                                        address=%s, specialization=%s
                                    WHERE national_id=%s
                                ''', (e_name, e_salary, e_mobile, e_address, e_specialization, tid))
                                conn.commit()
                                cur.close()
                                st.success("✅ تم حفظ التعديلات.")
                                st.rerun()
                            except Exception as e:
                                conn.rollback()
                                st.error(f"❌ حدث خطأ أثناء الحفظ: {e}")

                        if delete:
                            linked_df = ui.df(conn, "SELECT COUNT(*) AS c FROM classes WHERE teacher_id=%s", (tid,))
                            linked = linked_df.iloc[0]['c'] if not linked_df.empty else 0
                            if linked > 0:
                                st.error(f"⚠️ هذا المعلم/ة مسؤول عن {linked} صف. يرجى إعادة تعيين الصف أولاً.")
                            else:
                                try:
                                    cur = conn.cursor()
                                    cur.execute("DELETE FROM teachers WHERE national_id=%s", (tid,))
                                    conn.commit()
                                    cur.close()
                                    st.warning("🗑️ تم حذف المعلم/ة بنجاح!")
                                    st.rerun()
                                except Exception as e:
                                    conn.rollback()
                                    st.error(f"❌ حدث خطأ أثناء الحذف: {e}")
