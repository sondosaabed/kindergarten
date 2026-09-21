"""
style.py — Clean, Modern & Responsive CSS for Kindergarten Management System.
Built from scratch with native RTL support, Cairo font, and robust form styling.
"""

CSS = """
<style>
/* -------------------------------------------------------------------------- */
/* 1. Google Fonts Import (Cairo)                                             */
/* -------------------------------------------------------------------------- */
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800;900&display=swap');

:root {
    --brand-primary: #10B981;
    --brand-dark: #064E3B;
    --brand-light: #ECFDF5;
    --bg-main: #F8FAFC;
    --card-bg: #FFFFFF;
    --border-color: #E2E8F0;
    --text-dark: #0F172A;
    --text-muted: #64748B;
}

/* -------------------------------------------------------------------------- */
/* 2. Global Typography & Direction                                          */
/* -------------------------------------------------------------------------- */
html, body, [class*="css"], .stApp {
    font-family: 'Cairo', -apple-system, BlinkMacSystemFont, sans-serif !important;
    direction: rtl !important;
    text-align: right !important;
    background-color: var(--bg-main);
    color: var(--text-dark);
}

*, *::before, *::after {
    font-family: 'Cairo', sans-serif !important;
}

/* -------------------------------------------------------------------------- */
/* 3. Streamlit Standard Headers & Title Realignment                          */
/* -------------------------------------------------------------------------- */
/* Hide anchor links (🔗) next to headers */
div[data-testid="stHeadingWithHeadline"] a,
a.anchor-link {
    display: none !important;
}

div[data-testid="stHeadingWithHeadline"] {
    text-align: right !important;
}

div[data-testid="stHeadingWithHeadline"] > h1,
div[data-testid="stHeadingWithHeadline"] > h2,
div[data-testid="stHeadingWithHeadline"] > h3,
div[data-testid="stHeadingWithHeadline"] > h4 {
    justify-content: flex-start !important;
    text-align: right !important;
    color: var(--brand-dark) !important;
    font-weight: 800 !important;
}

.section-title {
    font-size: 22px !important;
    font-weight: 800 !important;
    color: var(--brand-dark) !important;
    margin-bottom: 4px !important;
    text-align: right !important;
    display: flex;
    align-items: center;
    gap: 8px;
}

.section-sub {
    font-size: 13px !important;
    color: var(--text-muted) !important;
    margin-bottom: 20px !important;
    text-align: right !important;
}

/* -------------------------------------------------------------------------- */
/* 4. Native & Clean Sidebar Styling                                         */
/* -------------------------------------------------------------------------- */
section[data-testid="stSidebar"] {
    background-color: #064E3B !important;
    border-left: 1px solid rgba(255, 255, 255, 0.1) !important;
}

section[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

.brand-box {
    text-align: center !important;
    padding: 10px 0 16px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.15);
    margin-bottom: 16px;
}

.brand-box h2 {
    font-size: 18px !important;
    font-weight: 800 !important;
    margin: 0 !important;
}

.brand-box p {
    font-size: 12px !important;
    opacity: 0.8;
    margin: 2px 0 0 0 !important;
}

.sidebar-stat {
    background: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 10px !important;
    padding: 10px 12px !important;
    font-size: 13px !important;
    margin-bottom: 12px !important;
}

.sidebar-stat b {
    color: #A7F3D0 !important;
    font-size: 16px !important;
}

/* Sidebar Navigation Buttons */
section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important;
    text-align: right !important;
    justify-content: flex-start !important;
    padding: 8px 14px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    min-height: 42px !important;
    width: 100% !important;
}

section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: #10B981 !important;
    border: none !important;
    font-weight: 800 !important;
}

/* -------------------------------------------------------------------------- */
/* 5. Modern Cards & KPI Layout                                              */
/* -------------------------------------------------------------------------- */
.kpi-card {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    padding: 14px 16px;
    display: flex !important;
    flex-direction: row-reverse !important;
    align-items: center !alignment;
    justify-content: space-between !important;
    gap: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.kpi-content {
    display: flex;
    flex-direction: column;
    text-align: right;
    flex: 1;
}

.kpi-value {
    font-size: 18px !important;
    font-weight: 800 !important;
    color: var(--text-dark);
}

.kpi-label {
    font-size: 12px !important;
    color: var(--text-muted);
}

.kpi-icon {
    width: 42px;
    height: 42px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    background: var(--brand-light);
    color: var(--brand-dark);
}

/* -------------------------------------------------------------------------- */
/* 6. Form Styling & Complete Removal of "Press Enter" Tooltips               */
/* -------------------------------------------------------------------------- */
div[data-testid="stForm"] {
    background: var(--card-bg) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 16px !important;
    padding: 24px 20px !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03) !important;
}

div[data-baseweb="input"] {
    border-radius: 10px !important;
}

/* Comprehensive suppression of Streamlit input helper overlays */
div[data-testid="stInputInstruction"],
div[data-testid="InputInstructions"],
div[data-aria-hidden="true"],
.st-emotion-cache-1y4p8pa,
.st-emotion-cache-12w0q1f,
small {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    width: 0 !important;
    opacity: 0 !important;
}

/* Buttons */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 700 !important;
    min-height: 44px !important;
}

.stButton > button[kind="primary"] {
    background-color: var(--brand-primary) !important;
    border-color: var(--brand-primary) !important;
    color: #FFFFFF !important;
}

/* -------------------------------------------------------------------------- */
/* 7. Mobile Layout Tuning                                                    */
/* -------------------------------------------------------------------------- */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem 0.75rem !important;
    }

    div[data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        margin-bottom: 8px !important;
    }

    .section-title { font-size: 18px !important; }
    .section-sub { font-size: 12px !important; }
}

/* Hide Default Streamlit Overlays */
#MainMenu, footer, header, div[data-testid="stToolbar"] {
    visibility: hidden !important;
}
</style>
"""