"""
sidebar.py — Navigation rail with touch-optimized collapse handling.
"""

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

        st.markdown("<div class='nav-stack'>", unsafe_allow_html=True)
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
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 تسجيل الخروج", use_container_width=True, key="nav_logout"):
            auth.logout()

    return st.session_state.current_page