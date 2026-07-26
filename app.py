"""
app.py — نظام إدارة الروضة (Kindergarten Management System)

This file only does three things: set up the page, gate it behind login,
and route to the selected section module. All page content lives in
sections/*.py — edit those files independently without touching this one.
"""

import os
import streamlit as st

from db import init_db, get_connection
from style import CSS
import auth
import sidebar

from sections import (
    dashboard, students, parents, teachers,
    classes, academic_years, registration, payments, reports,
)

LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")

# --------------------------------------------------------------------------
# Setup
# --------------------------------------------------------------------------
st.set_page_config(page_title="روضة مؤسسة شباب البيرة", page_icon=LOGO_PATH, layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

if not auth.check_authentication():
    st.stop()

init_db()
conn = get_connection()

# --------------------------------------------------------------------------
# Navigation + routing
# --------------------------------------------------------------------------
ROUTES = {
    "dashboard": dashboard.render,
    "parents": parents.render,
    "students": students.render,
    "teachers": teachers.render,
    "classes": classes.render,
    "years": academic_years.render,
    "registration": registration.render,
    "payments": payments.render,
    "reports": reports.render,
}

current_page = sidebar.render(conn)
ROUTES[current_page](conn)
