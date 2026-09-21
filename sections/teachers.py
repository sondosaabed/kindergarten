"""
sections/teachers.py — إدارة المعلمات وصرف وتعديل الرواتب
"""

import streamlit as st
import ui
import helpers as H
import teacher_receipt
from datetime import datetime


def render(conn):
    ui.section_header("👩‍🏫", "المعلمات والرواتب", "إدارة بيانات المعلمات وصرف وتعديل الرواتب الشهرية")

    tab_add, tab_view, tab_salary = st.tabs([
        "➕ إضافة معلمة", 
        "📋 قائمة المعلمات", 
        "💵 صرف وتعديل الرواتب"
    ])

    # -------------------------------------------------- TAB 1: ADD TEACHER --
    with tab_add:
        with st.form("add_teacher_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            national_id = c1.text_input("رقم الهوية *").strip()
            full_name = c2.text_input("الاسم الرباعي *").strip()

            c3, c4, c5 = st.columns(3)
            salary = c3.number_input("الراتب الشهري (شيكل) *", min_value=0.0, value=2000.0, step=100.0)
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

    # -------------------------------------------------- TAB 2: VIEW TEACHERS --
    with tab_view:
        teachers = ui.df(conn, "SELECT national_id, full_name, salary, mobile, address, hire_date FROM teachers ORDER BY full_name")
        if teachers.empty:
            ui.empty_state("لا توجد معلمات مسجلات بعد.")
        else:
            st.dataframe(teachers.rename(columns={
                'national_id': 'رقم الهوية',
                'full_name': 'الاسم',
                'salary': 'الراتب الشهري',
                'mobile': 'الجوال',
                'address': 'العنوان',
                'hire_date': 'تاريخ التعيين'
            }), use_container_width=True, hide_index=True)