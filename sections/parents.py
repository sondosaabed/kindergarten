"""
sections/parents.py — أولياء الأمور

Add, search, edit and delete parent (father/mother) records.
"""

import streamlit as st

import ui
import helpers as H


def render(conn):
    ui.section_header("👨‍👩‍👧", "أولياء الأمور", "بيانات الأب والأم والتواصل")

    tab_add, tab_view = st.tabs(["➕ إضافة ولي أمر جديد", "📋 عرض / تعديل / حذف"])

    with tab_add:
        with st.form("add_parent_form", clear_on_submit=True):
            st.markdown("###### بيانات الأب")
            c1, c2, c3 = st.columns(3)
            father_id = c1.text_input("رقم هوية الأب")
            father_name = c2.text_input("اسم الأب الرباعي")
            father_mobile = c3.text_input("جوال الأب")
            c4, c5, c6 = st.columns(3)
            father_job = c4.text_input("عمل الأب")
            father_id_type = c5.selectbox("نوع هوية الأب", H.PARENT_ID_TYPES)
            father_work_phone = c6.text_input("رقم عمل الأب (إن وجد)")

            st.markdown("###### بيانات الأم")
            c7, c8, c9 = st.columns(3)
            mother_id = c7.text_input("رقم هوية الأم")
            mother_name = c8.text_input("اسم الأم الرباعي")
            mother_mobile = c9.text_input("جوال الأم")
            c10, c11, c12 = st.columns(3)
            mother_job_status = c10.selectbox("عمل الأم", H.MOTHER_JOB_STATUS)
            mother_work_type = c11.text_input("طبيعة عمل الأم") if mother_job_status == "تعمل" else ""
            mother_id_type = c12.selectbox("نوع هوية الأم", H.PARENT_ID_TYPES)
            mother_work_phone = st.text_input("رقم عمل الأم (إن وجد)")

            st.markdown("###### بيانات إضافية")
            c13, c14 = st.columns(2)
            address = c13.text_input("عنوان السكن")
            landline = c14.text_input("رقم الهاتف الأرضي")
            c15, c16 = st.columns(2)
            residency = c15.selectbox("الحالة", H.RESIDENCY_STATUS)
            marital = c16.selectbox("الحالة الاجتماعية", H.MARITAL_STATUS)
            c17, c18 = st.columns(2)
            emerg_name = c17.text_input("اسم جهة الاتصال للطوارئ")
            emerg_phone = c18.text_input("رقم جهة الاتصال للطوارئ")

            submitted = st.form_submit_button("💾 حفظ بيانات ولي الأمر", type="primary")
            if submitted:
                required = [father_id, father_name, father_mobile, father_job, mother_id,
                            mother_name, mother_mobile, address, residency, marital,
                            emerg_name, emerg_phone]
                if not all(required):
                    st.warning("يرجى تعبئة جميع الحقول الأساسية (*).")
                else:
                    existing = ui.df(conn, "SELECT 1 FROM parents WHERE father_id = ?", (father_id,))
                    if not existing.empty:
                        st.error("رقم هوية الأب مسجل مسبقاً.")
                    else:
                        conn.execute('''
                            INSERT INTO parents
                            (father_id, mother_id, father_name, mother_name, father_job, mother_job,
                             mother_work_type, father_id_type, mother_id_type, address, landline,
                             status_refugee, father_work_phone, mother_work_phone, father_mobile,
                             mother_mobile, emergency_contact_name, emergency_contact_phone,
                             marital_status, created_at)
                            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                        ''', (father_id, mother_id, father_name, mother_name, father_job, mother_job_status,
                              mother_work_type, father_id_type, mother_id_type, address, landline,
                              residency, father_work_phone, mother_work_phone, father_mobile,
                              mother_mobile, emerg_name, emerg_phone, marital, H.now_str()))
                        conn.commit()
                        st.success(f"تم حفظ بيانات ولي الأمر «{father_name}» بنجاح! 🎉")
                        st.rerun()

    with tab_view:
        parents = ui.df(conn, "SELECT * FROM parents ORDER BY created_at DESC")
        if parents.empty:
            ui.empty_state("لا يوجد أولياء أمور مسجلون بعد.")
        else:
            search = st.text_input("🔍 ابحث بالاسم أو رقم الهوية", key="p_search")
            shown = parents.copy()
            if search:
                shown = shown[shown['father_name'].str.contains(search, na=False) |
                               shown['mother_name'].str.contains(search, na=False) |
                               shown['father_id'].str.contains(search, na=False)]
            st.dataframe(shown.rename(columns={
                'father_id': 'هوية الأب', 'father_name': 'اسم الأب', 'mother_name': 'اسم الأم',
                'father_mobile': 'جوال الأب', 'mother_mobile': 'جوال الأم', 'address': 'العنوان',
                'marital_status': 'الحالة الاجتماعية'
            })[['هوية الأب', 'اسم الأب', 'اسم الأم', 'جوال الأب', 'جوال الأم', 'العنوان', 'الحالة الاجتماعية']],
                use_container_width=True, hide_index=True)

            st.divider()
            st.markdown("##### ✏️ تعديل أو حذف ولي أمر")
            pick = st.selectbox("اختر ولي الأمر", parents['father_name'] + " — " + parents['father_id'],
                                 index=None, placeholder="ابحث...")
            if pick:
                fid = pick.split(" — ")[-1]
                row = parents[parents['father_id'] == fid].iloc[0]
                linked_students = ui.df(conn, "SELECT COUNT(*) c FROM students WHERE father_id=?", (fid,)).iloc[0]['c']

                with st.form("edit_parent_form"):
                    c1, c2 = st.columns(2)
                    e_fname = c1.text_input("اسم الأب", value=row['father_name'])
                    e_mname = c2.text_input("اسم الأم", value=row['mother_name'])
                    c3, c4 = st.columns(2)
                    e_fmobile = c3.text_input("جوال الأب", value=row['father_mobile'])
                    e_mmobile = c4.text_input("جوال الأم", value=row['mother_mobile'])
                    e_address = st.text_input("العنوان", value=row['address'])

                    b1, b2 = st.columns(2)
                    save = b1.form_submit_button("💾 حفظ التعديلات", type="primary")
                    delete = b2.form_submit_button("🗑️ حذف ولي الأمر")

                    if save:
                        conn.execute('''
                            UPDATE parents SET father_name=?, mother_name=?, father_mobile=?,
                                mother_mobile=?, address=? WHERE father_id=?
                        ''', (e_fname, e_mname, e_fmobile, e_mmobile, e_address, fid))
                        conn.commit()
                        st.success("تم حفظ التعديلات.")
                        st.rerun()

                    if delete:
                        if linked_students > 0:
                            st.error(f"⚠️ لا يمكن الحذف مباشرة: يوجد {linked_students} طالب مرتبط بولي الأمر هذا. "
                                      "احذف أو انقل الطلاب أولاً.")
                        else:
                            conn.execute("DELETE FROM parents WHERE father_id=?", (fid,))
                            conn.commit()
                            st.success("تم حذف ولي الأمر.")
                            st.rerun()

                if linked_students > 0:
                    st.caption(f"👶 عدد الأبناء المسجلين لولي الأمر هذا: {linked_students}")
