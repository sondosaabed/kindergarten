# """
# auth.py — simple manager login gate.

# Credentials are read from Streamlit secrets (never hard-coded, never
# committed to the repo). On Streamlit Community Cloud, set them under
# your app's "Settings → Secrets". Locally, put them in
# .streamlit/secrets.toml (see .streamlit/secrets.toml.example).

# Expected secrets.toml shape:

#     [auth]
#     username = "manager"
#     password = "choose-a-strong-password"
# """

# import streamlit as st

# import ui


# def _get_credentials():
#     try:
#         return st.secrets["auth"]["username"], st.secrets["auth"]["password"]
#     except (KeyError, FileNotFoundError):
#         return None, None


# def logout():
#     st.session_state["auth_ok"] = False
#     st.rerun()


# def check_authentication():
#     """Returns True if the manager is logged in. Renders the login form
#     and returns False otherwise (caller should st.stop())."""

#     if st.session_state.get("auth_ok"):
#         return True

#     valid_user, valid_pass = _get_credentials()

#     ui.render_logo(width=120)

#     st.markdown("""
#     <div style="max-width:420px; margin: 10px auto 0 auto;">
#         <div class="card" style="text-align:center;">
#             <h2 style="margin:0;">روضة مؤسسة شباب البيرة</h2>
#             <p style="color:#7C8A7E; margin:2px 0 8px 0; font-size:13px;">Al-Bireh Youth Foundation Kindergarten</p>
#             <p style="color:#8A8AA3; margin-top:4px;">تسجيل دخول المديرة / المدير</p>
#         </div>
#     </div>
#     """, unsafe_allow_html=True)

#     if valid_user is None:
#         _, mid, _ = st.columns([1, 2, 1])
#         with mid:
#             st.warning(
#                 "⚠️ لم يتم إعداد بيانات الدخول بعد. يرجى إضافة اسم المستخدم وكلمة المرور "
#                 "ضمن Secrets الخاصة بالتطبيق (راجع ملف .streamlit/secrets.toml.example)."
#             )
#         return False

#     _, mid, _ = st.columns([1, 2, 1])
#     with mid:
#         with st.form("login_form"):
#             username = st.text_input("اسم المستخدم")
#             password = st.text_input("كلمة المرور", type="password")
#             submitted = st.form_submit_button("🔐 تسجيل الدخول", type="primary", use_container_width=True)

#         if submitted:
#             if username == valid_user and password == valid_pass:
#                 st.session_state["auth_ok"] = True
#                 st.rerun()
#             else:
#                 st.error("اسم المستخدم أو كلمة المرور غير صحيحة.")

#     return False


"""
auth.py — simple manager login gate.
Credentials read from Streamlit secrets.
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
    """Returns True if the manager is logged in. Renders unified login screen otherwise."""

    if st.session_state.get("auth_ok"):
        return True

    valid_user, valid_pass = _get_credentials()

    # Center container for the login modal
    _, mid, _ = st.columns([0.2, 0.6, 0.2])

    with mid:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Render logo inside the wrapper
        ui.render_logo(width=300, center=True, drop_shadow=False)

        # Integrated Header
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
            st.markdown('</div>', unsafe_allow_html=True)
            return False

        # Integrated Form
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

        st.markdown('</div>', unsafe_allow_html=True)

    return False