"""
sections/academic_years.py — السنوات الدراسية

Add, view and delete academic years (e.g. 2025/2026).
"""

import streamlit as st

import ui


def render(conn):
    ui.section_header(" 📅 ", "السنوات الدراسية", "إدارة الأفواج والسنوات")

    tab_add, tab_view = st.tabs(["➕ إضافة سنة دراسية", "📋 عرض / تعديل / حذف"])

    with tab_add:
        with st.form("add_year_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            year_id = c1.text_input("السنة الدراسية", placeholder="مثال: 2025/2026")
            start_date = c2.date_input("بداية السنة")
            end_date = c3.date_input("نهاية السنة")
            cohort_name = st.text_input("اسم الفوج (اختياري)")

            submitted = st.form_submit_button("💾 حفظ السنة الدراسية", type="primary")
            if submitted:
                if not year_id:
                    st.warning("يرجى إدخال السنة الدراسية.")
                else:
                    existing = ui.df(conn, "SELECT 1 FROM academic_years WHERE year_id=%s", (year_id,))
                    if not existing.empty:
                        st.error("هذه السنة الدراسية موجودة مسبقاً.")
                    else:
                        cur = conn.cursor()
                        cur.execute("INSERT INTO academic_years VALUES (%s,%s,%s,%s)",
                                    (year_id, str(start_date), str(end_date), cohort_name))
                        conn.commit()
                        cur.close()
                        st.success("تم حفظ السنة الدراسية بنجاح! 🎉")
                        st.rerun()

    with tab_view:
        years = ui.df(conn, "SELECT * FROM academic_years ORDER BY start_date DESC")
        if years.empty:
            ui.empty_state("لا توجد سنوات دراسية بعد.")
        else:
            st.dataframe(years.rename(columns={
                'year_id': 'السنة الدراسية', 'start_date': 'تاريخ البداية',
                'end_date': 'تاريخ النهاية', 'cohort_name': 'اسم الفوج'
            }), use_container_width=True, hide_index=True)

            st.divider()
            pick = st.selectbox("اختر سنة للحذف", years['year_id'], index=None, placeholder="اختر...")
            if pick:
                linked_df = ui.df(conn, "SELECT COUNT(*) AS c FROM registrations WHERE year_id=%s", (pick,))
                linked = linked_df.iloc[0]['c'] if not linked_df.empty else 0
                if linked > 0:
                    st.error(f"⚠️ يوجد {linked} تسجيل مرتبط بهذه السنة. لا يمكن الحذف.")
                else:
                    if st.button("🗑️ حذف السنة الدراسية"):
                        cur = conn.cursor()
                        cur.execute("DELETE FROM academic_years WHERE year_id=%s", (pick,))
                        conn.commit()
                        cur.close()
                        st.success("تم الحذف.")
                        st.rerun()