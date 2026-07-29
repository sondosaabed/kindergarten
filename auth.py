"""
auth.py — simple manager login gate.
"""

import streamlit as st
import ui


def _get_credentials():
    try:
        return st.secrets["auth"]["username"], st.secrets["auth"]["password"]
    except (KeyError, FileNotFoundError):
        return None, None


def logout():
    st.session_state["auth_ok"] = False
    st.rerun()


def check_authentication():
    """Returns True if the manager is logged in. Renders the login screen
    and returns False otherwise (caller should st.stop())."""

    if st.session_state.get("auth_ok"):
        return True

    valid_user, valid_pass = _get_credentials()

    # Center column ratio
    _, mid, _ = st.columns([1, 1.2, 1])

    with mid:
        # Single Form Container (Acts as the Card)
        with st.form("login_form", clear_on_submit=False):
            # Render Logo
            ui.render_logo(width=110, center=True, drop_shadow=False)

            # Header HTML inside the form card
            st.markdown("""
            <div class="login-header">
                <h2>روضة مؤسسة شباب البيرة</h2>
                <p class="subtitle-en">Al-Bireh Youth Foundation Kindergarten</p>
                <div class="login-badge-wrapper">
                    <span class="login-badge">تسجيل دخول المديرة / المدير 🔐</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if valid_user is None:
                st.warning(
                    "⚠️ لم يتم إعداد بيانات الدخول بعد. يرجى إضافة اسم المستخدم وكلمة المرور "
                    "ضمن Secrets الخاصة بالتطبيق (راجع ملف .streamlit/secrets.toml.example)."
                )
                return False

            # Inputs
            username = st.text_input("اسم المستخدم", placeholder="أدخل اسم المستخدم")
            password = st.text_input("كلمة المرور", type="password", placeholder="أدخل كلمة المرور")
            
            # Form Submit Button
            submitted = st.form_submit_button("تسجيل الدخول", type="primary", use_container_width=True)

            if submitted:
                if username == valid_user and password == valid_pass:
                    st.session_state["auth_ok"] = True
                    st.rerun()
                else:
                    st.error("اسم المستخدم أو كلمة المرور غير صحيحة.")

    return False