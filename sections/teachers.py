"""
sections/teachers.py — إدارة ملفات وبينات المعلمات
"""

import streamlit as st
import pandas as pd
import ui


def render(conn):
    ui.section_header("👩‍🏫", "المعلمون", "إدارة بيانات وملفات المعلمات في الروضة")

    tab_add, tab_view = st.tabs(["➕ إضافة معلمة", "📋 قائمة المعلمات والتعديل"])

    with tab_add:
        with st.form("add_teacher_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            national_id = c1.text_input("رقم الهوية *").strip()
            full_name = c2.text_input("الاسم الرباعي *").strip()

            c3, c4, c5 = st.columns(3)
            salary = c3.number_input("الراتب الشهري الافتراضي (شيكل) *", min_value=0.0, value=2000.0, step=100.0)
            mobile = c4.text_input("رقم الجوال").strip()
            hire_date = c5.date_input("تاريخ التعيين")

            address = st.text_input("العنوان السكني").strip()

            submitted = st.form_submit_button("💾 حفظ المعلمة", type="primary", use_container_width=True)

            if submitted:
                if not national_id or not full_name:
                    st.error("⚠️ يرجى إدخال رقم الهوية والاسم الرباعي.")
                else:
                    try:
                        cur = conn.cursor()
                        cur.execute("""
                            INSERT INTO teachers (national_id, full_name, salary, mobile, address, hire_date)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (national_id, full_name, salary, mobile, address, str(hire_date)))
                        conn.commit()
                        cur.close()
                        st.success(f"✅ تم إضافة المعلمة ({full_name}) بنجاح!")
                        st.rerun()
                    except Exception as e:
                        conn.rollback()
                        st.error(f"❌ حدث خطأ أثناء الحفظ: {e}")

    with tab_view:
        teachers = ui.df(conn, "SELECT * FROM teachers ORDER BY full_name")
        
        if teachers.empty:
            ui.empty_state("لا توجد معلمات مسجلات بعد.")
        else:
            st.dataframe(teachers.rename(columns={
                'national_id': 'رقم الهوية',
                'full_name': 'الاسم',
                'salary': 'الراتب الافتراضي',
                'mobile': 'الجوال',
                'address': 'العنوان',
                'hire_date': 'تاريخ التعيين'
            }), use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("##### ✏️ تعديل بيانات معلمة")

            t_options = [(r['national_id'], f"{r['full_name']} ({r['national_id']})") for _, r in teachers.iterrows()]
            selected_t = st.selectbox(
                "اختر المعلمة للتعديل", 
                options=t_options, 
                format_func=lambda x: x[1] if x else "اختر...", 
                index=None,
                placeholder="اختر معلمة..."
            )

            if selected_t:
                t_id = selected_t[0]
                t_row = teachers[teachers['national_id'] == t_id].iloc[0]

                with st.form("edit_teacher_form"):
                    e_nid = st.text_input("رقم الهوية", value=t_row['national_id'])
                    
                    ec1, ec2 = st.columns(2)
                    e_name = ec1.text_input("الاسم الرباعي", value=t_row['full_name'])
                    e_salary = ec2.number_input("الراتب الشهري الافتراضي (شيكل)", min_value=0.0, value=float(t_row['salary'] or 0), step=100.0)

                    ec3, ec4 = st.columns(2)
                    e_mobile = ec3.text_input("رقم الجوال", value=t_row['mobile'] or "")
                    
                    try:
                        curr_hire = pd.to_datetime(t_row['hire_date']).date() if t_row['hire_date'] else pd.Timestamp.today().date()
                    except Exception:
                        curr_hire = pd.Timestamp.today().date()
                    e_hire = ec4.date_input("تاريخ التعيين", value=curr_hire)

                    ec5, ec6 = st.columns(2)
                    e_exp = ec5.number_input("سنوات الخبرة", min_value=0, value=int(t_row['experience_years'] or 0))
                    e_degree = ec6.text_input("الدرجة العلمية", value=t_row['degree'] or "")

                    e_spec = st.text_input("التخصص", value=t_row['specialization'] or "")
                    e_address = st.text_input("العنوان", value=t_row['address'] or "")

                    b1, b2 = st.columns(2)
                    save_t = b1.form_submit_button("💾 حفظ التعديلات", type="primary", use_container_width=True)
                    del_t = b2.form_submit_button("🗑️ حذف المعلمة", use_container_width=True)

                    if save_t:
                        try:
                            cur = conn.cursor()
                            cur.execute("""
                                UPDATE teachers 
                                SET national_id=%s, full_name=%s, salary=%s, mobile=%s, address=%s, hire_date=%s, experience_years=%s, degree=%s, specialization=%s
                                WHERE national_id=%s
                            """, (e_nid, e_name, e_salary, e_mobile, e_address, str(e_hire), e_exp, e_degree, e_spec, t_id))
                            conn.commit()
                            cur.close()
                            st.success("✅ تم تحديث بيانات المعلمة بنجاح.")
                            st.rerun()
                        except Exception as e:
                            conn.rollback()
                            st.error(f"❌ حدث خطأ أثناء التحديث: {e}")

                    if del_t:
                        try:
                            cur = conn.cursor()
                            cur.execute("DELETE FROM teachers WHERE national_id=%s", (t_id,))
                            conn.commit()
                            cur.close()
                            st.warning("🗑️ تم حذف المعلمة بنجاح.")
                            st.rerun()
                        except Exception as e:
                            conn.rollback()
                            st.error(f"❌ حدث خطأ أثناء الحذف: {e}")