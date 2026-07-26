"""
app.py — نظام إدارة الروضة (Kindergarten Management System)

A professional, easy-to-use front office system for a small kindergarten:
students, parents, teachers, classes, academic years, registrations and
cash payments — with a friendly dashboard and exportable reports.
"""

import io
import pandas as pd
import streamlit as st

from db import init_db, get_connection
from style import CSS
import helpers as H
import auth

import os

LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")

# --------------------------------------------------------------------------
# Setup
# --------------------------------------------------------------------------
st.set_page_config(page_title="روضة مؤسسة شباب البيرة", page_icon=LOGO_PATH, layout="wide",
                   initial_sidebar_state="collapsed")
st.markdown(CSS, unsafe_allow_html=True)

if not auth.check_authentication():
    st.stop()

init_db()
conn = get_connection()


def df(sql, params=()):
    return pd.read_sql_query(sql, conn, params=params)


def section_header(icon, title, subtitle=""):
    st.markdown(f"<div class='section-title'>{icon} {title}</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div class='section-sub'>{subtitle}</div>", unsafe_allow_html=True)


def kpi(col, icon, label, value, bg="#E9F5EC", fg="#219044"):
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon" style="background:{bg}; color:{fg};">{icon}</div>
            <div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-label">{label}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def empty_state(message):
    st.info(message)


def confirm_delete(key, label="أوافق على الحذف نهائياً"):
    return st.checkbox(f"⚠️ {label}", key=key)


# --------------------------------------------------------------------------
# Sidebar navigation
# --------------------------------------------------------------------------
with st.sidebar:
    _, logo_col, _ = st.columns([1, 2, 1])
    with logo_col:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, use_container_width=True)
    st.markdown("""
    <div class="brand-box" style="border-top:none;">
        <h2 style="font-size:19px;">روضة مؤسسة شباب البيرة</h2>
        <p>Al-Bireh Youth Foundation Kindergarten</p>
    </div>
    """, unsafe_allow_html=True)

    students_count = df("SELECT COUNT(*) c FROM students").iloc[0]['c']
    month_revenue = df(
        "SELECT COALESCE(SUM(amount),0) s FROM payments WHERE strftime('%Y-%m', payment_date) = strftime('%Y-%m','now')"
    ).iloc[0]['s']

    st.markdown(f"""
    <div class="sidebar-stat">👦 عدد الطلاب <b>{students_count}</b></div>
    <div class="sidebar-stat">💰 مقبوضات هذا الشهر <b>{H.format_money(month_revenue)}</b></div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "القائمة الرئيسية",
        [
            "📊 لوحة التحكم",
            "🎒 الطلاب",
            "👨‍👩‍👧 أولياء الأمور",
            "👩‍🏫 المعلمون",
            "🏷️ الصفوف",
            "📅 السنوات الدراسية",
            "📝 التسجيل",
            "💵 الدفعات المالية",
            "📈 التقارير",
        ],
        label_visibility="collapsed",
    )
    st.markdown("<div style='opacity:.6; font-size:12px; margin-top:20px;'>صُنع بـ ❤️ لأجل روضتنا</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        auth.logout()


# ==========================================================================
# 1. DASHBOARD
# ==========================================================================
def page_dashboard():
    section_header("📊", "لوحة التحكم", "نظرة سريعة وشاملة على أداء الروضة")

    total_students = df("SELECT COUNT(*) c FROM students").iloc[0]['c']
    total_teachers = df("SELECT COUNT(*) c FROM teachers").iloc[0]['c']
    total_classes = df("SELECT COUNT(*) c FROM classes").iloc[0]['c']
    total_revenue = df("SELECT COALESCE(SUM(amount),0) s FROM payments").iloc[0]['s']
    pending = df(f"SELECT COUNT(*) c FROM registrations WHERE status = '{H.STATUS_NEW}'").iloc[0]['c']

    c1, c2, c3, c4, c5 = st.columns(5)
    kpi(c1, "🎒", "إجمالي الطلاب", total_students, "#E9F5EC", "#219044")
    kpi(c2, "👩‍🏫", "المعلمون", total_teachers, "#FBF3E3", "#D7A431")
    kpi(c3, "🏷️", "الصفوف", total_classes, "#E9F5EC", "#163D22")
    kpi(c4, "💰", "إجمالي المقبوضات", H.format_money(total_revenue), "#FDECEC", "#E62031")
    kpi(c5, "⏳", "بانتظار رسوم التسجيل", pending, "#FBF3E3", "#B4790C")

    st.write("")
    left, right = st.columns([1.3, 1])

    with left:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("##### 📈 المقبوضات آخر 6 أشهر")
        rev = df("""
            SELECT strftime('%Y-%m', payment_date) AS الشهر, SUM(amount) AS المبلغ
            FROM payments
            GROUP BY الشهر
            ORDER BY الشهر DESC
            LIMIT 6
        """).sort_values("الشهر")
        if rev.empty:
            empty_state("لا توجد مقبوضات مسجلة بعد.")
        else:
            st.bar_chart(rev.set_index("الشهر"))
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("##### 🏷️ توزيع الطلاب على الصفوف")
        dist = df("""
            SELECT (c.class_type || ' ' || c.section) AS الصف, COUNT(r.registration_id) AS العدد
            FROM classes c
            LEFT JOIN registrations r ON r.class_id = c.class_id
                AND r.year_id = (SELECT year_id FROM academic_years ORDER BY start_date DESC LIMIT 1)
            GROUP BY c.class_id
        """)
        if dist.empty:
            empty_state("لا توجد صفوف بعد.")
        else:
            st.bar_chart(dist.set_index("الصف"))
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("##### 🕓 آخر عمليات التسجيل")
    recent = df("""
        SELECT s.full_name AS "اسم الطالب", (c.class_type || ' ' || c.section) AS "الصف",
               r.year_id AS "السنة الدراسية", r.status AS "الحالة"
        FROM registrations r
        JOIN students s ON s.student_id = r.student_id
        JOIN classes c ON c.class_id = r.class_id
        ORDER BY r.registration_id DESC LIMIT 8
    """)
    if recent.empty:
        empty_state("لا توجد تسجيلات بعد.")
    else:
        st.dataframe(recent, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ==========================================================================
# 2. STUDENTS
# ==========================================================================
def page_students():
    section_header("🎒", "إدارة الطلاب", "إضافة وتعديل ومتابعة بيانات الأطفال")

    tab_add, tab_view = st.tabs(["➕ إضافة طالب جديد", "📋 عرض / تعديل / حذف"])

    parents_df = df("SELECT father_id, father_name, mother_name FROM parents")
    parent_options = {
        f"{r.father_name} ({r.father_id}) — الأم: {r.mother_name}": r.father_id
        for r in parents_df.itertuples()
    }

    with tab_add:
        if parents_df.empty:
            empty_state("يجب إضافة ولي أمر واحد على الأقل قبل تسجيل طالب. انتقل إلى صفحة «أولياء الأمور».")
        else:
            with st.form("add_student_form", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                student_id = c1.text_input("رقم هوية الطالب", key="s_id")
                full_name = c2.text_input("اسم الطالب الرباعي", key="s_name")
                birth_date = c3.date_input("تاريخ الميلاد", key="s_bd", min_value=pd.Timestamp("2005-01-01"))

                c4, c5, c6 = st.columns(3)
                birth_place = c4.text_input("مكان الميلاد", key="s_bp")
                gender = c5.selectbox("الجنس", H.GENDERS, key="s_gender")
                id_type = c6.selectbox("نوع الهوية", H.STUDENT_ID_TYPES, key="s_idtype")

                c7, c8 = st.columns(2)
                nat_choice = c7.selectbox("الجنسية", H.NATIONALITIES, key="s_nat")
                nationality = c7.text_input("حدد الجنسية", key="s_nat_other") if nat_choice == "أخرى" else nat_choice
                father = c8.selectbox("ولي الأمر", list(parent_options.keys()), key="s_parent")

                medical = st.checkbox("هل يوجد حالة طبية؟", key="s_medical")
                medical_details = st.text_area("تفاصيل الحالة الطبية (اختياري)", key="s_med_details") if medical else ""

                submitted = st.form_submit_button("💾 حفظ بيانات الطالب", type="primary")
                if submitted:
                    if not student_id or not full_name or not birth_place:
                        st.warning("يرجى تعبئة جميع الحقول الأساسية (*).")
                    else:
                        existing = df("SELECT 1 FROM students WHERE student_id = ?", (student_id,))
                        if not existing.empty:
                            st.error("رقم هوية الطالب مسجل مسبقاً. يرجى التحقق أو استخدام تبويب التعديل.")
                        else:
                            conn.execute('''
                                INSERT INTO students
                                (student_id, full_name, birth_date, birth_place, gender, id_type,
                                 nationality, has_medical_condition, medical_details, father_id, created_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (student_id, full_name, str(birth_date), birth_place, gender, id_type,
                                  nationality, 1 if medical else 0, medical_details,
                                  parent_options[father], H.now_str()))
                            conn.commit()
                            st.success(f"تم تسجيل الطالب «{full_name}» بنجاح! 🎉")
                            st.rerun()

    with tab_view:
        students = df("""
            SELECT s.student_id, s.full_name, s.birth_date, s.gender, s.id_type,
                   s.nationality, s.has_medical_condition, s.medical_details,
                   s.father_id, p.father_name
            FROM students s JOIN parents p ON s.father_id = p.father_id
            ORDER BY s.created_at DESC
        """)
        if students.empty:
            empty_state("لا يوجد طلاب مسجلون بعد.")
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

            st.divider()
            st.markdown("##### ✏️ تعديل أو حذف طالب")
            pick = st.selectbox("اختر الطالب", students['full_name'] + " — " + students['student_id'],
                                 index=None, placeholder="ابحث عن طالب...")
            if pick:
                sid = pick.split(" — ")[-1]
                row = students[students['student_id'] == sid].iloc[0]
                with st.form("edit_student_form"):
                    c1, c2, c3 = st.columns(3)
                    e_name = c1.text_input("اسم الطالب", value=row['full_name'])
                    e_bd = c2.date_input("تاريخ الميلاد", value=pd.to_datetime(row['birth_date']))
                    e_gender = c3.selectbox("الجنس", H.GENDERS, index=H.GENDERS.index(row['gender']))

                    c4, c5 = st.columns(2)
                    e_idtype = c4.selectbox("نوع الهوية", H.STUDENT_ID_TYPES,
                                             index=H.STUDENT_ID_TYPES.index(row['id_type']) if row['id_type'] in H.STUDENT_ID_TYPES else 0)
                    e_nat = c5.text_input("الجنسية", value=row['nationality'])

                    e_medical = st.checkbox("يوجد حالة طبية", value=bool(row['has_medical_condition']))
                    e_med_details = st.text_area("تفاصيل الحالة الطبية", value=row['medical_details'] or "")

                    b1, b2 = st.columns(2)
                    save = b1.form_submit_button("💾 حفظ التعديلات", type="primary")
                    delete = b2.form_submit_button("🗑️ حذف الطالب")

                    if save:
                        conn.execute('''
                            UPDATE students SET full_name=?, birth_date=?, gender=?, id_type=?,
                                nationality=?, has_medical_condition=?, medical_details=?
                            WHERE student_id=?
                        ''', (e_name, str(e_bd), e_gender, e_idtype, e_nat,
                              1 if e_medical else 0, e_med_details, sid))
                        conn.commit()
                        st.success("تم حفظ التعديلات.")
                        st.rerun()

                    if delete:
                        conn.execute("DELETE FROM students WHERE student_id=?", (sid,))
                        conn.commit()
                        st.success("تم حذف الطالب.")
                        st.rerun()


# ==========================================================================
# 3. PARENTS
# ==========================================================================
def page_parents():
    section_header("👨‍👩‍👧", "أولياء الأمور", "بيانات الأب والأم والتواصل")

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
                    existing = df("SELECT 1 FROM parents WHERE father_id = ?", (father_id,))
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
        parents = df("SELECT * FROM parents ORDER BY created_at DESC")
        if parents.empty:
            empty_state("لا يوجد أولياء أمور مسجلون بعد.")
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
                linked_students = df("SELECT COUNT(*) c FROM students WHERE father_id=?", (fid,)).iloc[0]['c']

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


# ==========================================================================
# 4. TEACHERS
# ==========================================================================
def page_teachers():
    section_header("👩‍🏫", "المعلمون", "بيانات الكادر التعليمي")

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
                    existing = df("SELECT 1 FROM teachers WHERE national_id=?", (national_id,))
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
        teachers = df("SELECT * FROM teachers")
        if teachers.empty:
            empty_state("لا يوجد معلمون مسجلون بعد.")
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
                        linked = df("SELECT COUNT(*) c FROM classes WHERE teacher_id=?", (tid,)).iloc[0]['c']
                        if linked > 0:
                            st.error(f"⚠️ هذا المعلم/ة مسؤول عن {linked} صف. يرجى إعادة تعيين الصف أولاً.")
                        else:
                            conn.execute("DELETE FROM teachers WHERE national_id=?", (tid,))
                            conn.commit()
                            st.success("تم الحذف.")
                            st.rerun()


# ==========================================================================
# 5. CLASSES
# ==========================================================================
def page_classes():
    section_header("🏷️", "الصفوف", "تنظيم الشعب وتعيين المعلمات")

    tab_add, tab_view = st.tabs(["➕ إضافة صف", "📋 عرض / تعديل / حذف"])

    teachers_df = df("SELECT national_id, full_name FROM teachers")
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
                existing = df("SELECT 1 FROM classes WHERE class_type=? AND section=?", (class_type, section))
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
        classes = df("""
            SELECT c.class_id, c.class_type, c.section, c.class_name, t.full_name AS teacher_name,
                   c.teacher_id
            FROM classes c LEFT JOIN teachers t ON c.teacher_id = t.national_id
        """)
        if classes.empty:
            empty_state("لا توجد صفوف بعد.")
        else:
            counts = df("""
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
                        linked = df("SELECT COUNT(*) c FROM registrations WHERE class_id=?", (int(row['class_id']),)).iloc[0]['c']
                        if linked > 0:
                            st.error(f"⚠️ يوجد {linked} تسجيل مرتبط بهذا الصف. لا يمكن الحذف.")
                        else:
                            conn.execute("DELETE FROM classes WHERE class_id=?", (int(row['class_id']),))
                            conn.commit()
                            st.success("تم الحذف.")
                            st.rerun()


# ==========================================================================
# 6. ACADEMIC YEARS
# ==========================================================================
def page_years():
    section_header("📅", "السنوات الدراسية", "إدارة الأفواج والسنوات")

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
                    existing = df("SELECT 1 FROM academic_years WHERE year_id=?", (year_id,))
                    if not existing.empty:
                        st.error("هذه السنة الدراسية موجودة مسبقاً.")
                    else:
                        conn.execute("INSERT INTO academic_years VALUES (?,?,?,?)",
                                     (year_id, str(start_date), str(end_date), cohort_name))
                        conn.commit()
                        st.success("تم حفظ السنة الدراسية بنجاح! 🎉")
                        st.rerun()

    with tab_view:
        years = df("SELECT * FROM academic_years ORDER BY start_date DESC")
        if years.empty:
            empty_state("لا توجد سنوات دراسية بعد.")
        else:
            st.dataframe(years.rename(columns={
                'year_id': 'السنة الدراسية', 'start_date': 'تاريخ البداية',
                'end_date': 'تاريخ النهاية', 'cohort_name': 'اسم الفوج'
            }), use_container_width=True, hide_index=True)

            st.divider()
            pick = st.selectbox("اختر سنة للحذف", years['year_id'], index=None, placeholder="اختر...")
            if pick:
                linked = df("SELECT COUNT(*) c FROM registrations WHERE year_id=?", (pick,)).iloc[0]['c']
                if linked > 0:
                    st.error(f"⚠️ يوجد {linked} تسجيل مرتبط بهذه السنة. لا يمكن الحذف.")
                else:
                    if st.button("🗑️ حذف السنة الدراسية"):
                        conn.execute("DELETE FROM academic_years WHERE year_id=?", (pick,))
                        conn.commit()
                        st.success("تم الحذف.")
                        st.rerun()


# ==========================================================================
# 7. REGISTRATION
# ==========================================================================
def page_registration():
    section_header("📝", "التسجيل المدرسي", "تسجيل طالب في صف لسنة دراسية محددة")

    students_df = df("SELECT student_id, full_name FROM students")
    classes_df = df("SELECT class_id, class_type, section, class_name FROM classes")
    years_df = df("SELECT year_id FROM academic_years ORDER BY start_date DESC")

    if students_df.empty or classes_df.empty or years_df.empty:
        missing = []
        if students_df.empty: missing.append("طالب")
        if classes_df.empty: missing.append("صف")
        if years_df.empty: missing.append("سنة دراسية")
        empty_state(f"يجب إضافة كل من: {'، '.join(missing)} قبل إجراء التسجيل.")
        return

    tab_add, tab_view = st.tabs(["➕ تسجيل جديد", "📋 كل التسجيلات"])

    with tab_add:
        student_options = {r.full_name + " — " + r.student_id: r.student_id for r in students_df.itertuples()}
        classes_df['label'] = classes_df['class_type'] + " " + classes_df['section'] + \
                               classes_df['class_name'].fillna('').apply(lambda x: f" ({x})" if x else "")
        class_options = {r.label: r.class_id for r in classes_df.itertuples()}

        with st.form("add_registration_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            student_label = c1.selectbox("الطالب", list(student_options.keys()))
            class_label = c2.selectbox("الصف والشعبة", list(class_options.keys()))
            year_label = c3.selectbox("السنة الدراسية", years_df['year_id'])

            submitted = st.form_submit_button("💾 تسجيل الطالب", type="primary")
            if submitted:
                sid = student_options[student_label]
                cid = class_options[class_label]
                existing = df("SELECT 1 FROM registrations WHERE student_id=? AND year_id=?", (sid, year_label))
                if not existing.empty:
                    st.error("هذا الطالب مسجل مسبقاً في هذه السنة الدراسية.")
                else:
                    conn.execute('''
                        INSERT INTO registrations (student_id, class_id, year_id, status, registration_date)
                        VALUES (?,?,?,?,?)
                    ''', (sid, cid, year_label, H.STATUS_NEW, H.today_str()))
                    conn.commit()
                    st.success(f"تم تسجيل «{student_label.split(' — ')[0]}» بنجاح! الحالة الحالية: {H.STATUS_NEW}. "
                               "توجّه إلى صفحة «الدفعات المالية» لتحصيل رسوم التسجيل.")
                    st.rerun()

    with tab_view:
        regs = df("""
            SELECT r.registration_id, s.full_name AS "اسم الطالب",
                   (c.class_type || ' ' || c.section) AS "الصف", r.year_id AS "السنة الدراسية",
                   r.status AS "الحالة", r.registration_date AS "تاريخ التسجيل"
            FROM registrations r
            JOIN students s ON s.student_id = r.student_id
            JOIN classes c ON c.class_id = r.class_id
            ORDER BY r.registration_id DESC
        """)
        if regs.empty:
            empty_state("لا توجد تسجيلات بعد.")
        else:
            f1, f2 = st.columns(2)
            year_filter = f1.selectbox("تصفية حسب السنة", ["الكل"] + sorted(regs["السنة الدراسية"].unique().tolist()))
            status_filter = f2.selectbox("تصفية حسب الحالة", ["الكل", H.STATUS_NEW, H.STATUS_ACTIVE])
            shown = regs.copy()
            if year_filter != "الكل":
                shown = shown[shown["السنة الدراسية"] == year_filter]
            if status_filter != "الكل":
                shown = shown[shown["الحالة"] == status_filter]
            st.dataframe(shown, use_container_width=True, hide_index=True)


# ==========================================================================
# 8. PAYMENTS
# ==========================================================================
def page_payments():
    section_header("💵", "الدفعات المالية", "تسجيل دفعة نقدية وطباعة وصل استلام")

    active_regs = df("""
        SELECT r.registration_id, s.full_name AS student_name, p.father_name,
               (c.class_type || ' ' || c.section) AS class_label, r.year_id, r.status
        FROM registrations r
        JOIN students s ON s.student_id = r.student_id
        JOIN classes c ON c.class_id = r.class_id
        JOIN parents p ON p.father_id = s.father_id
        ORDER BY r.registration_id DESC
    """)

    if active_regs.empty:
        empty_state("لا يوجد طلاب مسجلون بعد. قم بتسجيل طالب أولاً من صفحة «التسجيل».")
        return

    tab_add, tab_view = st.tabs(["➕ تسجيل دفعة كاش", "📋 سجل الدفعات"])

    with tab_add:
        active_regs['label'] = (active_regs['student_name'] + "  |  " + active_regs['class_label'] +
                                 "  |  " + active_regs['year_id'] + "  (" + active_regs['status'] + ")")
        reg_dict = dict(zip(active_regs['label'], active_regs['registration_id']))
        selected_label = st.selectbox("اختر الطالب والتسجيل", list(reg_dict.keys()))
        selected_row = active_regs[active_regs['label'] == selected_label].iloc[0]

        with st.form("add_payment_form"):
            c1, c2 = st.columns(2)
            amount = c1.number_input("المبلغ المدفوع (كاش)", min_value=1.0, value=100.0, step=10.0)
            payer = c2.text_input("اسم الدافع (ولي الأمر)", value=selected_row['father_name'])

            c3, c4 = st.columns(2)
            reason = c3.selectbox("مقابل", H.PAYMENT_FOR)
            reason_other = c4.text_input("تفاصيل أخرى") if reason == "آخر" else ""

            submitted = st.form_submit_button("🧾 حفظ الدفعة وطباعة الوصل", type="primary")

        if submitted:
            reg_id = int(selected_row['registration_id'])
            today = H.today_str()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO payments (registration_id, amount, payment_date, payment_method,
                    payer_name, payment_for, payment_for_other)
                VALUES (?, ?, ?, 'كاش', ?, ?, ?)
            ''', (reg_id, amount, today, payer, reason, reason_other))
            conn.commit()
            receipt_id = cur.lastrowid
            new_status = H.refresh_registration_status(conn, reg_id)

            st.success(f"تم حفظ الدفعة بنجاح! رقم الوصل: #{receipt_id} — حالة التسجيل الآن: {new_status}")

            st.markdown(f"""
            <div class="receipt-box">
                <h3>🧾 وصل استلام نقدية — روضة مؤسسة شباب البيرة</h3>
                <div class="receipt-row"><span>رقم الوصل</span><b>#{receipt_id}</b></div>
                <div class="receipt-row"><span>التاريخ</span><b>{today}</b></div>
                <div class="receipt-row"><span>اسم الطالب</span><b>{selected_row['student_name']}</b></div>
                <div class="receipt-row"><span>وصلنا من السيد/ة</span><b>{payer}</b></div>
                <div class="receipt-row"><span>مبلغ وقدره</span><b>{H.format_money(amount)} شيكل/دينار</b></div>
                <div class="receipt-row"><span>مقابل</span><b>{reason} {f'({reason_other})' if reason_other else ''}</b></div>
                <div class="receipt-row"><span>طريقة الدفع</span><b>كاش 💵</b></div>
            </div>
            """, unsafe_allow_html=True)
            st.caption("💡 يمكنك طباعة هذه الصفحة مباشرة عبر أمر الطباعة في متصفحك (Ctrl/Cmd + P).")

    with tab_view:
        payments = df("""
            SELECT p.receipt_number AS "رقم الوصل", s.full_name AS "اسم الطالب",
                   p.amount AS "المبلغ", p.payment_date AS "التاريخ",
                   p.payer_name AS "الدافع", p.payment_for AS "مقابل"
            FROM payments p
            JOIN registrations r ON p.registration_id = r.registration_id
            JOIN students s ON r.student_id = s.student_id
            ORDER BY p.receipt_number DESC
        """)
        if payments.empty:
            empty_state("لا توجد دفعات مسجلة بعد.")
        else:
            search = st.text_input("🔍 ابحث باسم الطالب أو الدافع")
            shown = payments.copy()
            if search:
                shown = shown[shown["اسم الطالب"].str.contains(search, na=False) |
                               shown["الدافع"].str.contains(search, na=False)]
            st.dataframe(shown, use_container_width=True, hide_index=True)
            st.metric("💰 مجموع الدفعات المعروضة", H.format_money(shown["المبلغ"].sum()))


# ==========================================================================
# 9. REPORTS
# ==========================================================================
def page_reports():
    section_header("📈", "التقارير والتصدير", "استخراج بيانات مفلترة إلى Excel")

    report_type = st.radio(
        "اختر نوع التقرير",
        ["سجل المقبوضات المالية", "قائمة الطلاب وأولياء الأمور", "قائمة التسجيلات"],
        horizontal=True,
    )

    if report_type == "سجل المقبوضات المالية":
        c1, c2, c3 = st.columns(3)
        date_from = c1.date_input("من تاريخ", value=None)
        date_to = c2.date_input("إلى تاريخ", value=None)
        reason_filter = c3.selectbox("مقابل", ["الكل"] + H.PAYMENT_FOR)

        query = """
            SELECT p.receipt_number AS 'رقم الوصل', s.full_name AS 'اسم الطالب',
                   p.amount AS 'المبلغ', p.payment_date AS 'تاريخ الدفع',
                   p.payer_name AS 'اسم الدافع', p.payment_for AS 'مقابل'
            FROM payments p
            JOIN registrations r ON p.registration_id = r.registration_id
            JOIN students s ON r.student_id = s.student_id
            WHERE 1=1
        """
        params = []
        if date_from:
            query += " AND p.payment_date >= ?"
            params.append(str(date_from))
        if date_to:
            query += " AND p.payment_date <= ?"
            params.append(str(date_to))
        if reason_filter != "الكل":
            query += " AND p.payment_for = ?"
            params.append(reason_filter)
        query += " ORDER BY p.payment_date DESC"
        result = df(query, tuple(params))

        if not result.empty:
            st.metric("💰 إجمالي المبلغ", H.format_money(result['المبلغ'].sum()))

    elif report_type == "قائمة الطلاب وأولياء الأمور":
        classes_for_filter = df("SELECT DISTINCT class_type, section FROM classes")
        result = df("""
            SELECT s.student_id AS 'رقم هوية الطالب', s.full_name AS 'اسم الطالب',
                   s.birth_date AS 'تاريخ الميلاد', s.gender AS 'الجنس',
                   p.father_name AS 'اسم الأب', p.father_mobile AS 'جوال الأب',
                   p.mother_name AS 'اسم الأم', p.address AS 'العنوان'
            FROM students s JOIN parents p ON s.father_id = p.father_id
        """)

    else:  # registrations
        year_filter = st.selectbox("تصفية حسب السنة", ["الكل"] + df("SELECT year_id FROM academic_years")['year_id'].tolist())
        query = """
            SELECT s.full_name AS 'اسم الطالب', (c.class_type || ' ' || c.section) AS 'الصف',
                   r.year_id AS 'السنة الدراسية', r.status AS 'الحالة', r.registration_date AS 'تاريخ التسجيل'
            FROM registrations r
            JOIN students s ON s.student_id = r.student_id
            JOIN classes c ON c.class_id = r.class_id
            WHERE 1=1
        """
        params = []
        if year_filter != "الكل":
            query += " AND r.year_id = ?"
            params.append(year_filter)
        result = df(query, tuple(params))

    st.dataframe(result, use_container_width=True, hide_index=True)

    def to_excel(d):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            d.to_excel(writer, index=False, sheet_name='Report')
        return output.getvalue()

    if not result.empty:
        st.download_button(
            "📥 تحميل التقرير كملف Excel",
            data=to_excel(result),
            file_name=f"report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        empty_state("لا توجد بيانات مطابقة للفلاتر المحددة.")


# --------------------------------------------------------------------------
# Router
# --------------------------------------------------------------------------
ROUTES = {
    "📊 لوحة التحكم": page_dashboard,
    "🎒 الطلاب": page_students,
    "👨‍👩‍👧 أولياء الأمور": page_parents,
    "👩‍🏫 المعلمون": page_teachers,
    "🏷️ الصفوف": page_classes,
    "📅 السنوات الدراسية": page_years,
    "📝 التسجيل": page_registration,
    "💵 الدفعات المالية": page_payments,
    "📈 التقارير": page_reports,
}

ROUTES[page]()
