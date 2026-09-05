"""
sections/academic_years.py — السنوات الدراسية

Add, view and delete academic years (e.g. 2025/2026). Same
reliability/UX pattern as parents.py: try/except + conn.rollback()
around every write, and clear confirm messaging before deletes that
have linked registrations.
"""

import streamlit as st

import ui


def render(conn):
    ui.section_header("📅", "السنوات الدراسية", "إدارة الأفواج والسنوات")

    tab_add, tab_view = st.tabs(["➕ إضافة سنة دراسية", "📋 عرض / تعديل / حذف"])

    # -------------------------------------------------- TAB 1: ADD YEAR --
    with tab_add:
        with st.form("add_year_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            year_id = c1.text_input("السنة الدراسية *", placeholder="مثال: 2025/2026").strip()
            start_date = c2.date_input("بداية السنة *")
            end_date = c3.date_input("نهاية السنة *")
            cohort_name = st.text_input("اسم الفوج (اختياري)").strip()

            submitted = st.form_submit_button("💾 حفظ السنة الدراسية", type="primary", use_container_width=True)

            if submitted:
                if not year_id:
                    st.warning("⚠️ يرجى إدخال السنة الدراسية.")
                else:
                    existing = ui.df(conn, "SELECT 1 FROM academic_years WHERE year_id=%s", (year_id,))
                    if not existing.empty:
                        st.error("❌ هذه السنة الدراسية موجودة مسبقاً.")
                    else:
                        try:
                            cur = conn.cursor()
                            cur.execute("INSERT INTO academic_years VALUES (%s,%s,%s,%s)",
                                        (year_id, str(start_date), str(end_date), cohort_name))
                            conn.commit()
                            cur.close()
                            st.success("✅ تم حفظ السنة الدراسية بنجاح! 🎉")
                            st.rerun()
                        except Exception as e:
                            conn.rollback()
                            st.error(f"❌ حدث خطأ أثناء الحفظ: {e}")

    # ------------------------------------------- TAB 2: VIEW / EDIT / DELETE --
    with tab_view:
        years = ui.df(conn, "SELECT * FROM academic_years ORDER BY start_date DESC")
        if years.empty:
            ui.empty_state("لا توجد سنوات دراسية بعد.")
        else:
            st.dataframe(years.rename(columns={
                'year_id': 'السنة الدراسية', 'start_date': 'تاريخ البداية',
                'end_date': 'تاريخ النهاية', 'cohort_name': 'اسم الفوج'
            }), use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("##### ✏️ تعديل أو حذف سنة دراسية")

            year_options = [(row['year_id'], f"{row['year_id']} — {row['cohort_name'] or 'بدون اسم فوج'}")
                            for _, row in years.iterrows()]
            selected = st.selectbox(
                "اختر السنة الدراسية", options=year_options,
                format_func=lambda x: x[1] if x else "اختر...",
                index=None, placeholder="اختر...", key="year_select_edit",
            )

            if selected:
                yid = selected[0]
                row = years[years['year_id'] == yid].iloc[0]

                with st.expander(f"⚙️ تعديل بيانات: {yid}", expanded=True):
                    with st.form("edit_year_form"):
                        e_cohort = st.text_input("اسم الفوج", value=row['cohort_name'] or "")

                        b1, b2 = st.columns(2)
                        save = b1.form_submit_button("💾 حفظ", type="primary", use_container_width=True)
                        delete = b2.form_submit_button("🗑️ حذف السنة الدراسية", use_container_width=True)

                        if save:
                            try:
                                cur = conn.cursor()
                                cur.execute("UPDATE academic_years SET cohort_name=%s WHERE year_id=%s",
                                            (e_cohort, yid))
                                conn.commit()
                                cur.close()
                                st.success("✅ تم الحفظ.")
                                st.rerun()
                            except Exception as e:
                                conn.rollback()
                                st.error(f"❌ حدث خطأ أثناء الحفظ: {e}")

                        if delete:
                            linked_df = ui.df(conn, "SELECT COUNT(*) AS c FROM registrations WHERE year_id=%s", (yid,))
                            linked = linked_df.iloc[0]['c'] if not linked_df.empty else 0
                            if linked > 0:
                                st.error(f"⚠️ يوجد {linked} تسجيل مرتبط بهذه السنة. لا يمكن الحذف.")
                            else:
                                try:
                                    cur = conn.cursor()
                                    cur.execute("DELETE FROM academic_years WHERE year_id=%s", (yid,))
                                    conn.commit()
                                    cur.close()
                                    st.warning("🗑️ تم حذف السنة الدراسية بنجاح!")
                                    st.rerun()
                                except Exception as e:
                                    conn.rollback()
                                    st.error(f"❌ حدث خطأ أثناء الحذف: {e}")
