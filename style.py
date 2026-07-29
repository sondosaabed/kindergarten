"""
style.py — Central CSS for Streamlit App. Professional RTL layout with clean Cairo font everywhere.
"""

CSS = """
<style>
/* ---------------------------------------------------------------- */
/* Google Fonts Import for Cairo Arabic Font                        */
/* ---------------------------------------------------------------- */
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800;900&display=swap');

:root {
    /* Main Brand Colors (Fresh Emerald & Dark Slate) */
    --primary: #10B981;
    --primary-dark: #064E3B;
    --primary-light: #D1FAE5;
    
    /* Modern Kindergarten Warm Palette */
    --coral-pink: #F43F5E;
    --amber-gold: #F59E0B;
    --soft-sky: #3B82F6;
    
    /* Neutrals & Surfaces */
    --bg: #FAFAF9;
    --card-bg: #FFFFFF;
    --card-border: #E7E5E4;
    --text-main: #1C1917;
    --text-muted: #78716C;
    
    /* Elevation Shadows */
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.05);
    --shadow-md: 0 4px 12px -2px rgba(0,0,0,0.08);
    --shadow-lg: 0 10px 25px -5px rgba(0,0,0,0.1);
}

/* ---------------------------------------------------------------- */
/* GLOBAL FONT OVERRIDE — FORCING 'Cairo' EVERYWHERE                */
/* ---------------------------------------------------------------- */
*, *::before, *::after,
html, body, [class*="css"],
p, span, div, a, li, blockquote,
h1, h2, h3, h4, h5, h6, 
label, input, textarea, select, button,
div[data-baseweb="select"], 
.stMarkdown, .stMarkdown p, .section-title, .section-sub {
    font-family: 'Cairo', sans-serif !important;
}

/* Preserve Streamlit Native Material Icons */
[data-testid="stIconMaterial"], 
[class*="material-symbols"], 
i[class*="icon"] {
    font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
}

html, body, [class*="css"] {
    direction: RTL;
    text-align: right;
    color: var(--text-main);
}

.stApp {
    background-color: var(--bg);
}

/* ---------------------------------------------------------------- */
/* STREAMLIT NATIVE HEADINGS FIX (Anchors & Titles Alignment)      */
/* ---------------------------------------------------------------- */
div[data-testid="stHeadingWithHeadline"] {
    direction: rtl !important;
    text-align: right !important;
}

div[data-testid="stHeadingWithHeadline"] > h1,
div[data-testid="stHeadingWithHeadline"] > h2,
div[data-testid="stHeadingWithHeadline"] > h3,
div[data-testid="stHeadingWithHeadline"] > h4,
div[data-testid="stHeadingWithHeadline"] > h5,
div[data-testid="stHeadingWithHeadline"] > h6 {
    display: flex !important;
    flex-direction: row !important;
    justify-content: flex-start !important;
    align-items: center !important;
    gap: 8px !important;
    font-family: 'Cairo', sans-serif !important;
    font-weight: 700 !important;
    color: var(--text-main);
    margin-top: 4px;
    margin-bottom: 8px;
}

/* Hide or push Streamlit anchor link icon out of the way */
div[data-testid="stHeadingWithHeadline"] a {
    order: 2 !important;
    opacity: 0.3;
    transition: opacity 0.2s ease;
}

div[data-testid="stHeadingWithHeadline"]:hover a {
    opacity: 1;
}

/* ---------------------------------------------------------------- */
/* SECTION TITLES & SUBTITLES IN CAIRO                              */
/* ---------------------------------------------------------------- */
.section-title {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    font-size: 26px;
    font-weight: 800 !important;
    font-family: 'Cairo', sans-serif !important;
    color: var(--primary-dark);
    margin-bottom: 4px;
    text-align: center;
}

.section-sub {
    color: var(--text-muted);
    margin-bottom: 24px;
    font-size: 15px;
    font-weight: 600 !important;
    font-family: 'Cairo', sans-serif !important;
    text-align: center;
}

/* ---------------------------------------------------------------- */
/* TABS STYLING FIXES                                               */
/* ---------------------------------------------------------------- */
div[data-testid="stTabs"] {
    direction: rtl !important;
}

div[data-baseweb="tab-list"] {
    gap: 8px;
    background-color: transparent;
    border-bottom: 2px solid var(--card-border);
    justify-content: flex-start;
}

button[data-baseweb="tab"] {
    height: 44px;
    padding: 8px 18px;
    border-radius: 10px 10px 0 0 !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    font-family: 'Cairo', sans-serif !important;
    color: var(--text-muted) !important;
    background-color: transparent !important;
    transition: all 0.2s ease;
}

button[data-baseweb="tab"]:hover {
    color: var(--primary) !important;
    background-color: var(--primary-light) !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--primary-dark) !important;
    border-bottom: 3px solid var(--primary) !important;
    background-color: #FFFFFF !important;
}

/* ---------------------------------------------------------------- */
/* MODERN GLASSMORPHIC SIDEBAR STYLING & COLLAPSE FIX              */
/* ---------------------------------------------------------------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #064E3B 0%, #022C22 100%) !important;
    direction: RTL;
    border-left: 1px solid rgba(255, 255, 255, 0.08) !important;
}

/* Hide sidebar background/shadow when collapsed, but KEEP the expand button functional */
section[data-testid="stSidebar"][data-collapsed="true"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* Force the collapse/expand toggle button to stay visible at all times */
button[data-testid="stSidebarCollapseButton"],
div[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 999999 !important;
}

/* Sidebar Text Color Fixes */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span:not([data-testid="stIconMaterial"]),
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown {
    color: rgba(255, 255, 255, 0.9) !important;
    font-family: 'Cairo', sans-serif !important;
}

.brand-box {
    text-align: center;
    padding: 12px 8px 20px 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.12);
    margin-bottom: 18px;
}

.brand-box h2 {
    margin: 0;
    font-size: 20px;
    font-weight: 800;
    color: #FFFFFF !important;
    letter-spacing: -0.3px;
    font-family: 'Cairo', sans-serif !important;
}

.brand-box p {
    margin: 4px 0 0 0;
    font-size: 13px;
    color: rgba(255, 255, 255, 0.7) !important;
    font-family: 'Cairo', sans-serif !important;
}

/* Sidebar Top Cards & Metrics */
.sidebar-stat,
section[data-testid="stSidebar"] [data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.07) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
    margin-bottom: 10px !important;
    font-size: 13px !important;
    color: #FFFFFF !important;
    backdrop-filter: blur(8px) !important;
    font-family: 'Cairo', sans-serif !important;
}

.sidebar-stat b {
    font-size: 17px;
    display: block;
    color: var(--primary-light) !important;
    font-family: 'Cairo', sans-serif !important;
}

/* Sidebar Navigation Buttons Container */
section[data-testid="stSidebar"] .stButton {
    margin-bottom: 6px !important;
}

/* Inactive Navigation Buttons (Translucent Glass Effect) */
section[data-testid="stSidebar"] .stButton > button,
section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    background: rgba(255, 255, 255, 0.08) !important;
    color: #E2E8F0 !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    text-align: right !important;
    justify-content: flex-start !important;
    padding: 10px 16px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    font-family: 'Cairo', sans-serif !important;
    height: 44px !important;
    width: 100% !important;
    box-shadow: none !important;
    transition: all 0.2s ease-in-out !important;
}

section[data-testid="stSidebar"] .stButton > button[kind="secondary"] * {
    color: #E2E8F0 !important;
    font-family: 'Cairo', sans-serif !important;
}

/* Hover State for Inactive Buttons */
section[data-testid="stSidebar"] .stButton > button:hover,
section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
    background: rgba(255, 255, 255, 0.18) !important;
    color: #FFFFFF !important;
    border-color: rgba(255, 255, 255, 0.3) !important;
    transform: translateX(-3px) !important;
}

section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover * {
    color: #FFFFFF !important;
}

/* Active Navigation Button (Highlight Gradient) */
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 12px !important;
    text-align: right !important;
    justify-content: flex-start !important;
    padding: 10px 16px !important;
    font-weight: 800 !important;
    font-size: 14px !important;
    font-family: 'Cairo', sans-serif !important;
    height: 44px !important;
    width: 100% !important;
    box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35) !important;
    transition: all 0.2s ease-in-out !important;
}

section[data-testid="stSidebar"] .stButton > button[kind="primary"] * {
    color: #FFFFFF !important;
    font-family: 'Cairo', sans-serif !important;
}

section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
    transform: translateX(-3px) !important;
}

section[data-testid="stSidebar"] img {
    max-width: 140px !important;
    height: auto !important;
}

/* ---------------------------------------------------------------- */
/* CONTAINERS, DATAFRAMES & FORM ELEMENTS                           */
/* ---------------------------------------------------------------- */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--card-bg);
    border-radius: 16px !important;
    border: 1px solid var(--card-border) !important;
    box-shadow: var(--shadow-sm);
    padding: 12px;
    margin-bottom: 16px;
}

div[data-testid="stDataFrame"] {
    direction: rtl !important;
    border-radius: 12px;
    border: 1px solid var(--card-border);
}

/* ---------------------------------------------------------------- */
/* UPDATED KPI CARDS SYSTEM (Prevents Overlap and Clipping)         */
/* ---------------------------------------------------------------- */
.kpi-card {
    background: var(--card-bg);
    border-radius: 16px;
    padding: 14px 16px;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--card-border);
    display: flex !important;
    flex-direction: row-reverse !important; /* RTL placement: Icon right, Text left */
    align-items: center !important;
    justify-content: space-between !important;
    gap: 12px !important;
    min-height: 86px;
    height: 100%;
    box-sizing: border-box;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.kpi-content {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
    text-align: right;
    flex: 1;
    min-width: 0;
}

.kpi-value {
    font-size: 20px !important;
    font-weight: 800 !important;
    color: var(--text-main);
    line-height: 1.2;
    font-family: 'Cairo', sans-serif !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
}

.kpi-label {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: var(--text-muted);
    margin-top: 3px;
    line-height: 1.3;
    font-family: 'Cairo', sans-serif !important;
    word-break: break-word;
}

.kpi-icon {
    width: 46px !important;
    height: 46px !important;
    min-width: 46px !important;
    min-height: 46px !important;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    flex-shrink: 0 !important;
    background: var(--primary-light);
    color: var(--primary-dark);
}

/* ---------------------------------------------------------------- */
/* LOGIN FORM & INPUT FIELD STYLING                                 */
/* ---------------------------------------------------------------- */
.login-header {
    text-align: center;
    margin-top: 8px;
    margin-bottom: 20px;
}

.login-header h2 {
    font-size: 22px !important;
    font-weight: 800 !important;
    color: #064E3B !important;
    margin: 0 0 2px 0 !important;
    text-align: center !important;
}

.login-header .subtitle-en {
    font-size: 13px !important;
    color: #64748B !important;
    direction: ltr !important;
    margin: 0 0 12px 0 !important;
    font-weight: 500 !important;
    text-align: center !important;
}

.login-badge-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 6px;
}

.login-badge {
    background-color: #ECFDF5;
    color: #064E3B;
    font-size: 13px;
    font-weight: 700;
    padding: 4px 14px;
    border-radius: 20px;
    border: 1px solid rgba(16, 185, 129, 0.25);
}

div[data-testid="stForm"] {
    background: #FFFFFF !important;
    border-radius: 20px !important;
    padding: 32px 28px !important;
    border: 1px solid #E2E8F0 !important;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01) !important;
}

div[data-testid="stForm"] div[data-baseweb="input"] {
    border-radius: 12px !important;
    background-color: #F8FAFC !important;
    border: 1px solid #CBD5E1 !important;
    transition: all 0.2s ease-in-out;
}

div[data-testid="stForm"] div[data-baseweb="input"]:focus-within {
    border-color: #10B981 !important;
    background-color: #FFFFFF !important;
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15) !important;
}

/* Hide Streamlit form instructions ("Press Enter to submit form") */
div[data-testid="stForm"] [data-aria-hidden="true"],
div[data-testid="stForm"] small,
div[data-testid="InputInstructions"] {
    display: none !important;
}

div[data-testid="stForm"] input::placeholder {
    opacity: 0.6 !important;
}

.stButton > button {
    border-radius: 10px;
    font-weight: 700;
    font-family: 'Cairo', sans-serif !important;
    transition: all 0.2s ease;
}

.stButton > button[kind="primary"] {
    background: var(--primary);
    border-color: var(--primary);
    color: #FFFFFF;
}

.stButton > button[kind="primary"]:hover {
    background: var(--primary-dark);
    border-color: var(--primary-dark);
    box-shadow: var(--shadow-md);
}

/* ---------------------------------------------------------------- */
/* MOBILE RESPONSIVENESS                                            */
/* ---------------------------------------------------------------- */
@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 1rem !important;
    }

    .section-title { font-size: 20px; gap: 8px; }
    .section-sub { font-size: 13px; margin-bottom: 14px; }

    .kpi-card {
        padding: 12px 14px;
        border-radius: 14px;
        gap: 10px !important;
    }
    .kpi-icon { width: 40px !important; height: 40px !important; min-width: 40px !important; font-size: 18px; border-radius: 10px; }
    .kpi-value { font-size: 17px !important; }
    .kpi-label { font-size: 12px !important; }

    .stButton > button {
        width: 100%;
        min-height: 44px;
    }
}

/* Force Streamlit markdown containers and headings to align right */
div[data-testid="stMarkdownContainer"],
div[data-testid="stMarkdownContainer"] > div[data-testid="stHeadingWithHeadline"] {
    text-align: right !important;
}

div[data-testid="stHeadingWithHeadline"] > h1,
div[data-testid="stHeadingWithHeadline"] > h2,
div[data-testid="stHeadingWithHeadline"] > h3,
div[data-testid="stHeadingWithHeadline"] > h4,
div[data-testid="stHeadingWithHeadline"] > h5,
div[data-testid="stHeadingWithHeadline"] > h6 {
    justify-content: flex-start !important; /* In RTL flex mode, flex-start puts the content on the right */
    text-align: right !important;
    width: 100% !important;
}

/* Hide Streamlit default UI overlays & developer widgets */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
div[data-testid="stDecoration"] {display: none;}
div[data-testid="stToolbar"] {visibility: hidden;}
div[data-testid="stStatusWidget"] {display: none !important;}
.stDeployButton {display: none !important;}
</style>
"""