"""
sidebar.py — Navigation rail with touch-optimized collapse handling.
"""

import io
import pandas as pd
import streamlit as st
import ui
import auth

NAV_ITEMS = [
    ("dashboard", "📊", "الرئيسية"),
    ("parents", "👨‍👩‍👧", "أولياء الأمور"),
    ("students", "🎒", "الطلاب"),
    ("teachers", "👩‍🏫", "المعلمات"),
    ("classes", "🏷️", "الصفوف"),
    ("years", "📅", "السنوات الدراسية"),
    ("registration", "📝", "التسجيل"),
    ("payments", "💵", "الدفعات المالية"),
    ("salaries", "💸", "رواتب المعلمات"), 
    ("expenses", "📦", "المصروفات والأصول"), 
    ("reports", "📈", "التقارير"),
]


def _get_scalar(conn, query, params=()):
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        res = cur.fetchone()
        cur.close()
        if res is None:
            return 0
        if isinstance(res, dict):
            val = list(res.values())[0]
        elif isinstance(res, (tuple, list)):
            val = res[0]
        else:
            val = res
        return val if val is not None else 0
    except Exception:
        return 0


def render(conn):
    if "current_page" not in st.session_state:
        st.session_state.current_page = NAV_ITEMS[0][0]

    # تنسيق CSS خاص لزيادة تناسق زر التنزيل مع الشريط الجانبي الداكن
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] div.stDownloadButton > button {
        background: rgba(255, 255, 255, 0.08) !important;
        color: #E2E8F0 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        text-align: right !important;
        justify-content: flex-start !important;
        padding: 10px 16px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        font-family: 'Cairo', sans-serif !important;
        height: 44px !important;
        width: 100% !important;
        box-shadow: none !important;
        transition: all 0.2s ease-in-out !important;
    }
    section[data-testid="stSidebar"] div.stDownloadButton > button:hover {
        background: rgba(255, 255, 255, 0.18) !important;
        color: #FFFFFF !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        ui.render_logo(width=130)

        st.markdown("""
        <div class="brand-box">
            <h2>روضة مؤسسة شباب البيرة</h2>
            <p>نظام الإدارة والمالية</p>
        </div>
        """, unsafe_allow_html=True)

        raw_students = _get_scalar(conn, "SELECT COUNT(*) FROM students")
        try:
            students_count = int(raw_students)
        except (ValueError, TypeError):
            students_count = 0

        st.markdown(f"""
        <div class="sidebar-stat">👦 إجمالي الطلاب: <b>{students_count}</b></div>
        """, unsafe_allow_html=True)

        # Render navigation buttons directly without raw HTML div wrappers
        for key, icon, label in NAV_ITEMS:
            is_active = st.session_state.current_page == key
            if st.button(
                f"{icon}  {label}",
                key=f"nav_{key}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.current_page = key
                st.rerun()

        st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
        st.markdown("---")

        # --- Excel Comprehensive Backup Generation (Fixed for RealDictCursor) ---
        try:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                tables = {
                    "الطلاب": "students",
                    "أولياء الأمور": "parents",
                    "المعلمات": "teachers",
                    "التسجيل": "registrations",
                    "الصفوف": "classes",
                    "الدفعات المالية": "payments",
                    "رواتب المعلمات": "teacher_payments",
                    "المصروفات": "expenses",
                    "الأصول": "assets",
                    "السنوات الدراسية": "academic_years",
                }
                
                cur = conn.cursor()
                for sheet_name, table_name in tables.items():
                    try:
                        cur.execute(f"SELECT * FROM {table_name}")
                        rows = cur.fetchall()
                        if rows:
                            df = pd.DataFrame(rows)
                        else:
                            df = pd.DataFrame()
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                    except Exception:
                        continue
                cur.close()
                
            output.seek(0)
            
            st.download_button(
                label="📥 تحميل نسخة Excel شاملة",
                data=output,
                file_name="kindergarten_full_backup.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                help="تحميل كافة جداول النظام في ملف إكسل واحد متعدد التبويبات"
            )
        except Exception:
            pass

        st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 تسجيل الخروج", use_container_width=True, key="nav_logout"):
            auth.logout()

    return st.session_state.current_page