"""
sections/parents.py — إدارة بيانات أولياء الأمور (إضافة / عرض / تعديل / حذف)
"""

import streamlit as st
import ui
import helpers as H


def render(conn):
    ui.section_header("👨‍👩‍👧", "أولياء الأمور", "بيانات الأب والأم والتواصل")

    tab_add, tab_view = st.tabs(["➕ إضافة ولي أمر جديد", "📝 عرض / تعديل / حذف"])

    # -------------------------------------------------- TAB 1: ADD PARENT --
    with tab_add:
        st.markdown("##### 📝 أدخل بيانات ولي الأمر الجديد")

        with st.form("add_parent_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                father_id = st.text_input("رقم هوية الأب *", key="f_id").strip()
                father_id_type = st.selectbox("نوع هوية الأب", H.PARENT_ID_TYPES, key="f_id_type")
                father_name = st.text_input("اسم الأب رباعي *", key="f_name").strip()
                father_mobile = st.text_input("جوال الأب *", key="f_mob").strip()
                father_job = st.text_input("مهنة الأب", key="f_job").strip()

            with col2:
                mother_id = st.text_input("رقم هوية الأم *", key="m_id").strip()
                mother_id_type = st.selectbox("نوع هوية الأم", H.PARENT_ID_TYPES, key="m_id_type")
                mother_name = st.text_input("اسم الأم رباعي *", key="m_name").strip()
                mother_mobile = st.text_input("جوال الأم", key="m_mob").strip()
                mother_job = st.selectbox("عمل الأم", H.MOTHER_JOB_STATUS, key="m_job")

            st.markdown("---")
            c3, c4 = st.columns(2)
            with c3:
                marital_status = st.selectbox("الحالة الاجتماعية", H.MARITAL_STATUS, key="m_status")
            with c4:
                address = st.text_input("العنوان السكني التفصيلي", key="p_address").strip()

            submitted = st.form_submit_button("💾 حفظ ولي الأمر", type="primary", use_container_width=True)

            if submitted:
                if not father_id or not father_name or not father_mobile or not mother_id or not mother_name:
                    st.error("⚠️ يرجى تعبئة الحقول المطلوبة (*)")
                else:
                    try:
                        cur = conn.cursor()
                        cur.execute("""
                            INSERT INTO parents (
                                father_id, father_id_type, father_name, father_mobile, father_job,
                                mother_id, mother_id_type, mother_name, mother_mobile, mother_job,
                                marital_status, address
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            father_id, father_id_type, father_name, father_mobile, father_job,
                            mother_id, mother_id_type, mother_name, mother_mobile, mother_job,
                            marital_status, address
                        ))
                        conn.commit()
                        cur.close()
                        st.success(f"✅ تم حفظ ولي الأمر ({father_name}) بنجاح!")
                        st.rerun()
                    except Exception as e:
                        conn.rollback()
                        st.error(f"❌ حدث خطأ أثناء الحفظ (قد يكون رقم الهوية مسجلاً مسبقاً): {e}")

    # ------------------------------------------- TAB 2: VIEW / EDIT / DELETE --
    with tab_view:
        search_term = st.text_input("🔍 ابحث بالاسم أو رقم الهوية", placeholder="اكتب اسم الأب، الأم، أو رقم الهوية...").strip()

        # Query parents with proper Arabic aliases
        query = """
            SELECT 
                father_id AS "هوية الأب",
                father_name AS "اسم الأب",
                mother_name AS "اسم الأم",
                father_mobile AS "جوال الأب",
                mother_mobile AS "جوال الأم",
                address AS "العنوان",
                marital_status AS "الحالة الاجتماعية",
                father_job AS "مهنة الأب",
                mother_id AS "هوية الأم"
            FROM parents
        """
        params = []
        if search_term:
            query += """ WHERE 
                father_name LIKE %s OR 
                mother_name LIKE %s OR 
                father_id LIKE %s OR 
                mother_id LIKE %s
            """
            term = f"%{search_term}%"
            params = [term, term, term, term]

        query += " ORDER BY father_name ASC"

        df_parents = ui.df(conn, query, tuple(params))

        if df_parents.empty:
            ui.empty_state("لا توجد بيانات أولياء أمور مسجلة بعد.")
        else:
            st.dataframe(df_parents, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("##### ✏️ تعديل أو حذف ولي أمر")

        # Fetch parents directly for selectbox
        cur = conn.cursor()
        cur.execute("SELECT father_id, father_name, mother_name FROM parents ORDER BY father_name ASC")
        all_parents = cur.fetchall()
        cur.close()

        if all_parents:
            # Parse row entries depending on DB cursor format
            parent_options = []
            for p in all_parents:
                if isinstance(p, dict):
                    fid, fname, mname = p['father_id'], p['father_name'], p['mother_name']
                else:
                    fid, fname, mname = p[0], p[1], p[2]
                parent_options.append((fid, f"{fname} (أم: {mname}) - [هوية: {fid}]"))

            selected_parent = st.selectbox(
                "اختر ولي الأمر",
                options=parent_options,
                format_func=lambda x: x[1] if x else "اختر...",
                key="parent_select_edit"
            )

            if selected_parent:
                selected_fid = selected_parent[0]

                # Fetch selected parent's existing details
                cur = conn.cursor()
                cur.execute("SELECT * FROM parents WHERE father_id = %s", (selected_fid,))
                p_data = cur.fetchone()
                cur.close()

                if p_data:
                    # Normalize p_data dictionary vs tuple access
                    def g(key, idx):
                        if isinstance(p_data, dict):
                            return p_data.get(key, "")
                        return p_data[idx] if idx < len(p_data) else ""

                    with st.expander(f"⚙️ تعديل بيانات: {g('father_name', 2)}", expanded=True):
                        with st.form("edit_parent_form"):
                            col1, col2 = st.columns(2)
                            with col1:
                                ef_name = st.text_input("اسم الأب", value=g('father_name', 2))
                                ef_mob = st.text_input("جوال الأب", value=g('father_mobile', 3))
                                ef_job = st.text_input("مهنة الأب", value=g('father_job', 4))
                            with col2:
                                em_name = st.text_input("اسم الأم", value=g('mother_name', 7))
                                em_mob = st.text_input("جوال الأم", value=g('mother_mobile', 8))
                                e_addr = st.text_input("العنوان", value=g('address', 11))

                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                save_edit = st.form_submit_button("💾 حفظ التعديلات", type="primary", use_container_width=True)
                            with col_btn2:
                                delete_parent = st.form_submit_button("🗑️ حذف ولي الأمر", use_container_width=True)

                            if save_edit:
                                cur = conn.cursor()
                                cur.execute("""
                                    UPDATE parents SET 
                                        father_name = %s, father_mobile = %s, father_job = %s,
                                        mother_name = %s, mother_mobile = %s, address = %s
                                    WHERE father_id = %s
                                """, (ef_name, ef_mob, ef_job, em_name, em_mob, e_addr, selected_fid))
                                conn.commit()
                                cur.close()
                                st.success("✅ تم تحديث بيانات ولي الأمر بنجاح!")
                                st.rerun()

                            if delete_parent:
                                cur = conn.cursor()
                                cur.execute("DELETE FROM parents WHERE father_id = %s", (selected_fid,))
                                conn.commit()
                                cur.close()
                                st.warning("🗑️ تم حذف ولي الأمر بنجاح!")
                                st.rerun()