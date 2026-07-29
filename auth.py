"""
auth.py — simple manager login gate.

Credentials are read from Streamlit secrets (never hard-coded, never
committed to the repo). On Streamlit Community Cloud, set them under
your app's "Settings → Secrets". Locally, put them in
.streamlit/secrets.toml (see .streamlit/secrets.toml.example).

Expected secrets.toml shape:

    [auth]
    username = "manager"
    password = "choose-a-strong-password"

NOTE ON LAYOUT: everything below (logo, header text, form) is rendered
*inside one* `with st.container(border=True):` block. That's on purpose —
opening an HTML <div> in one st.markdown() call and closing it in another
does NOT actually wrap the Streamlit widgets rendered in between (each
st.* call becomes its own sibling element in the DOM, not a child of that
div). st.container(border=True) is a real parent element, so this is the
only way the logo/header/form actually end up inside one visual card
instead of floating next to an empty box.
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

    # Centered column keeps the card from stretching full-width on desktop;
    # it naturally collapses to full width on mobile.
    _, mid, _ = st.columns([1, 1.3, 1])

    with mid:
        with st.container(border=True):
            # invisible marker so style.py's CSS can target *this specific*
            # bordered container (see the :has(.login-marker) rules)
            st.markdown('<span class="login-marker" style="display:none;"></span>',
                        unsafe_allow_html=True)

            ui.render_logo(width=130, center=True, drop_shadow=False)

            st.markdown("""
            <div class="login-header">
                <h2>روضة مؤسسة شباب البيرة</h2>
                <p class="subtitle-en">Al-Bireh Youth Foundation Kindergarten</p>
                <p class="subtitle-ar">تسجيل دخول المديرة / المدير</p>
            </div>
            """, unsafe_allow_html=True)

            if valid_user is None:
                st.warning(
                    "⚠️ لم يتم إعداد بيانات الدخول بعد. يرجى إضافة اسم المستخدم وكلمة المرور "
                    "ضمن Secrets الخاصة بالتطبيق (راجع ملف .streamlit/secrets.toml.example)."
                )
                return False

            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("اسم المستخدم", placeholder="أدخل اسم المستخدم")
                password = st.text_input("كلمة المرور", type="password", placeholder="أدخل كلمة المرور")
                submitted = st.form_submit_button("🔐 تسجيل الدخول", type="primary", use_container_width=True)

                if submitted:
                    if username == valid_user and password == valid_pass:
                        st.session_state["auth_ok"] = True
                        st.rerun()
                    else:
                        st.error("اسم المستخدم أو كلمة المرور غير صحيحة.")

    return False
