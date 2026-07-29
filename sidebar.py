"""
sidebar.py — the app's navigation rail.
Uses direct cursor execution for scalar stats to avoid pandas type-casting errors.
"""

import streamlit as st
import ui
import helpers as H
import auth

NAV_ITEMS = [
    ("dashboard", "📊", "الرئيسية"),
    ("parents", "👨‍👩‍👧", "أولياء الأمور"),
    ("students", "🎒", "الطلاب"),
    ("teachers", "👩‍🏫", "المعلمون"),
    ("classes", "🏷️", "الصفوف"),
    ("years", "📅", "السنوات الدراسية"),
    ("registration", "📝", "التسجيل"),
    ("payments", "💵", "الدفعات المالية"),
    ("reports", "📈", "التقارير"),
]


def _get_scalar(conn, query, params=()):
    """Executes a scalar query directly using a DB cursor safely."""
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
    """Renders the sidebar and returns the selected page key."""

    if "current_page" not in st.session_state:
        st.session_state.current_page = NAV_ITEMS[0][0]

    with st.sidebar:
        ui.render_logo(width=120)

        st.markdown("""
        <div class="brand-box" style="border-top:none;">
            <h2 style="font-size:18px;">روضة مؤسسة شباب البيرة</h2>
            <p>Al-Bireh Youth Foundation Kindergarten</p>
        </div>
        """, unsafe_allow_html=True)

        # Fetch values using cursor direct fetch
        raw_students = _get_scalar(conn, "SELECT COUNT(*) FROM students")
        try:
            students_count = int(raw_students)
        except (ValueError, TypeError):
            students_count = 0

        raw_revenue = _get_scalar(
            conn,
            "SELECT COALESCE(SUM(amount), 0) FROM payments "
            "WHERE TO_CHAR(payment_date::date, 'YYYY-MM') = TO_CHAR(CURRENT_DATE, 'YYYY-MM')"
        )
        try:
            month_revenue = float(raw_revenue)
        except (ValueError, TypeError):
            month_revenue = 0.0

        st.markdown(f"""
        <div class="sidebar-stat">👦 عدد الطلاب <b>{students_count}</b></div>
        <div class="sidebar-stat">💰 مقبوضات هذا الشهر <b>{H.format_money(month_revenue)}</b></div>
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

        st.markdown(
            "<div style='opacity:.6; font-size:12px; margin-top:20px;'>صُنع بـ ❤️ لأجل روضتنا</div>",
            unsafe_allow_html=True
        )
        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 تسجيل الخروج", use_container_width=True, key="nav_logout"):
            auth.logout()

    return st.session_state.current_page