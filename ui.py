"""
ui.py — Shared mobile-safe UI building blocks.
"""

import base64
import os
import pandas as pd
import streamlit as st

LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")


def df(conn, sql, params=()):
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        
        if not rows:
            cur.close()
            return pd.DataFrame()
        
        if isinstance(rows[0], dict):
            data = rows
            cols = list(rows[0].keys())
            cur.close()
            return pd.DataFrame(data, columns=cols)
        else:
            cols = [desc[0] for desc in cur.description] if cur.description else None
            cur.close()
            return pd.DataFrame(rows, columns=cols)
    except Exception as e:
        st.error(f"⚠️ Query error: {e}")
        return pd.DataFrame()


def section_header(icon, title, subtitle=""):
    st.markdown(f"<div class='section-title'>{icon} {title}</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div class='section-sub'>{subtitle}</div>", unsafe_allow_html=True)


def kpi(col, icon, label, value, bg="#E9F5EC", fg="#219044"):
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon" style="background:{bg}; color:{fg};">{icon}</div>
            <div class="kpi-content">
                <div class="kpi-value">{value}</div>
                <div class="kpi-label">{label}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def empty_state(message):
    st.info(message)


def confirm_delete(key, label="أوافق على الحذف نهائياً"):
    return st.checkbox(f"⚠️ {label}", key=key)


@st.cache_data(show_spinner=False)
def _logo_base64():
    if not os.path.exists(LOGO_PATH):
        return None
    with open(LOGO_PATH, "rb") as f:
        return base64.b64encode(f.read()).decode()


def render_logo(width=140, center=True, drop_shadow=True):
    b64 = _logo_base64()
    if not b64:
        return
    shadow = "filter: drop-shadow(0 3px 6px rgba(0,0,0,.15));" if drop_shadow else ""
    align = "display:flex; justify-content:center;" if center else ""
    st.markdown(f"""
    <div style="{align} margin-bottom:6px;">
        <img src="data:image/png;base64,{b64}" style="max-width:{width}px; width:100%; height:auto; border-radius:50%; object-fit:cover; {shadow}" />
    </div>
    """, unsafe_allow_html=True)