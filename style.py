"""
style.py — Complete layout & style rebuild for Streamlit Kindergarten System.
Clean, reliable RTL formatting with full mobile support.
"""

CSS = """
<style>
/* -------------------------------------------------------------------------- */
/* 1. GOOGLE ARABIC FONT (CAIRO)                                             */
/* -------------------------------------------------------------------------- */
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"], [class*="st-"], 
p, span, div, a, li, h1, h2, h3, h4, h5, h6, 
label, input, textarea, select, button,
div[data-baseweb="select"] {
    font-family: 'Cairo', sans-serif !important;
}

/* Maintain Streamlit Icon Font Integrity */
[data-testid="stIconMaterial"], 
[class*="material-symbols"], 
i[class*="icon"] {
    font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
}

/* RTL Layout Alignment */
html, body, .stApp {
    direction: rtl;
    text-align: right;
    background-color: #FAFAF9;
    color: #1C1917;
}

/* -------------------------------------------------------------------------- */
/* 2. HEADINGS & HEADER CENTERING FIX                                        */
/* -------------------------------------------------------------------------- */
/* Hide Anchor Links (🔗) that shift headers */
a.anchor-link,
[data-testid="stHeaderActionElements"],
div[data-testid="stHeadingWithHeadline"] a {
    display: none !important;
}

/* Centered Page Titles & Headings */
div[data-testid="stHeadingWithHeadline"] {
    text-align: center !important;
    width: 100% !important;
}

div[data-testid="stHeadingWithHeadline"] > * {
    justify-content: center !important;
    text-align: center !important;
    font-weight: 800 !important;
    color: #064E3B !important;
}

.section-title {
    text-align: center !important;
    font-size: 24px !important;
    font-weight: 800 !important;
    color: #064E3B !important;
    margin-bottom: 4px !important;
}

.section-sub {
    text-align: center !important;
    font-size: 14px !important;
    color: #78716C !important;
    margin-bottom: 20px !important;
    font-weight: 600 !important;
}

/* -------------------------------------------------------------------------- */
/* 3. SIDEBAR STYLING                                                         */
/* -------------------------------------------------------------------------- */
section[data-testid="stSidebar"] {
    direction: rtl !important;
    background-color: #064E3B !important;
}

/* Force Text in Sidebar to White */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] label {
    color: #FFFFFF !important;
}

/* Sidebar Navigation Buttons */
section[data-testid="stSidebar"] .stButton > button {
    border-radius: 10px !important;
    font-weight: 700 !important;
    min-height: 44px !important;
    text-align: right !important;
    justify-content: flex-start !important;
    width: 100% !important;
    margin-bottom: 4px !important;
}

/* -------------------------------------------------------------------------- */
/* 4. FORM CLEANUP & REMOVING "PRESS ENTER TO SUBMIT"                        */
/* -------------------------------------------------------------------------- */
div[data-testid="stForm"] {
    background: #FFFFFF !important;
    border-radius: 14px !important;
    border: 1px solid #E7E5E4 !important;
    padding: 20px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
}

/* Hide Form Input Instructions across all Streamlit versions */
div[data-testid="InputInstructions"],
div[data-testid="stInputInstruction"],
div[data-testid="stForm"] small,
div[data-testid="stForm"] [data-aria-hidden="true"] {
    display: none !important;
    height: 0px !important;
    opacity: 0 !important;
    visibility: hidden !important;
}

/* Input Fields Styling */
div[data-baseweb="input"] {
    border-radius: 8px !important;
    min-height: 44px !important;
}

/* Primary Button Styling */
.stButton > button[kind="primary"] {
    background-color: #10B981 !important;
    border-color: #10B981 !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    min-height: 46px !important;
    border-radius: 10px !important;
}

/* -------------------------------------------------------------------------- */
/* 5. TABS & DATA TABLES                                                      */
/* -------------------------------------------------------------------------- */
div[data-testid="stTabs"] {
    direction: rtl !important;
}

div[data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 2px solid #E7E5E4;
}

button[data-baseweb="tab"] {
    font-weight: 700 !important;
    font-size: 14px !important;
    padding: 10px 16px !important;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #E7E5E4 !important;
    border-radius: 10px !important;
    direction: rtl !important;
}

/* -------------------------------------------------------------------------- */
/* 6. KPI CARDS                                                               */
/* -------------------------------------------------------------------------- */
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E7E5E4;
    border-radius: 12px;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-height: 80px;
    margin-bottom: 10px;
}

.kpi-content {
    display: flex;
    flex-direction: column;
    text-align: right;
}

.kpi-value {
    font-size: 18px;
    font-weight: 800;
    color: #1C1917;
}

.kpi-label {
    font-size: 12px;
    font-weight: 600;
    color: #78716C;
}

.kpi-icon {
    width: 42px;
    height: 42px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    background: #D1FAE5;
    color: #064E3B;
}

/* -------------------------------------------------------------------------- */
/* 7. RESPONSIVE MOBILE TWEAKS                                                */
/* -------------------------------------------------------------------------- */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem 0.5rem !important;
    }

    div[data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        margin-bottom: 10px !important;
    }

    .section-title {
        font-size: 20px !important;
    }
}

/* Hide Default Streamlit Overlays */
#MainMenu, footer, header, 
div[data-testid="stToolbar"], 
div[data-testid="stDecoration"] {
    visibility: hidden !important;
    display: none !important;
}
</style>
"""