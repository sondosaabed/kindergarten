"""
sidebar.py — the app's navigation rail.

Replaces the old st.radio menu with a stack of full-width buttons.
The active page is rendered with type="primary" (brand-colored) and every
other page with the default/secondary look, which reads as a proper
"selected tab" without any fragile custom CSS targeting individual
buttons by position.
"""

import streamlit as st

import ui
import helpers as H
import auth

NAV_ITEMS = [
    ("dashboard", "📊", "لوحة التحكم"),
    ("students", "🎒", "الطلاب"),
    ("parents", "👨‍👩‍👧", "أولياء الأمور"),
    ("teachers", "👩‍🏫", "المعلمون"),
    ("classes", "🏷️", "الصفوف"),
    ("years", "📅", "السنوات الدراسية"),
    ("registration", "📝", "التسجيل"),
    ("payments", "💵", "الدفعات المالية"),
    ("reports", "📈", "التقارير"),
]


def render(conn):
    """Renders the sidebar and returns the selected page key."""

    if "current_page" not in st.session_state:
        st.session_state.current_page = NAV_ITEMS[0][0]

    with st.sidebar:
        ui.render_logo(width=104)

        st.markdown("""
        <div class="brand-box" style="border-top:none;">
            <h2 style="font-size:18px;">روضة مؤسسة شباب البيرة</h2>
            <p>Al-Bireh Youth Foundation Kindergarten</p>
        </div>
        """, unsafe_allow_html=True)

        students_count = ui.df(conn, "SELECT COUNT(*) c FROM students").iloc[0]['c']
        month_revenue = ui.df(conn,
            "SELECT COALESCE(SUM(amount),0) s FROM payments WHERE strftime('%Y-%m', payment_date) = strftime('%Y-%m','now')"
        ).iloc[0]['s']

        st.markdown(f"""
        <div class="sidebar-stat">👦 عدد الطلاب <b>{students_count}</b></div>
        <div class="sidebar-stat">💰 مقبوضات هذا الشهر <b>{H.format_money(month_revenue)}</b></div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='nav-stack'>", unsafe_allow_html=True)
        for key, icon, label in NAV_ITEMS:
            is_active = st.session_state.current_page == key
            if st.button(f"{icon}  {label}", key=f"nav_{key}",
                         use_container_width=True,
                         type="primary" if is_active else "secondary"):
                st.session_state.current_page = key
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='opacity:.6; font-size:12px; margin-top:20px;'>صُنع بـ ❤️ لأجل روضتنا</div>",
                     unsafe_allow_html=True)
        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 تسجيل الخروج", use_container_width=True, key="nav_logout"):
            auth.logout()

    return st.session_state.current_page
