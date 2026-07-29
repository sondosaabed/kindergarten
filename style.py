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
/* SIDEBAR STYLING & COLLAPSED BLEED FIX                            */
/* ---------------------------------------------------------------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--primary-dark) 0%, #022C22 100%);
    direction: RTL;
    border-left: 1px solid rgba(255, 255, 255, 0.08);
    overflow: hidden !important;
}

section[data-testid="stSidebar"][data-collapsed="true"] {
    visibility: hidden !important;
}

section[data-testid="stSidebar"][data-collapsed="true"] * {
    display: none !important;
    opacity: 0 !important;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span:not([data-testid="stIconMaterial"]),
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown {
    color: #FFFFFF;
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
    color: rgba(255, 255, 255, 0.8) !important;
    font-family: 'Cairo', sans-serif !important;
}

.sidebar-stat {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 12px;
    padding: 10px 14px;
    margin-bottom: 10px;
    font-size: 13px;
    color: #FFFFFF !important;
    backdrop-filter: blur(4px);
    font-family: 'Cairo', sans-serif !important;
}

.sidebar-stat b {
    font-size: 17px;
    display: block;
    color: var(--primary-light) !important;
    font-family: 'Cairo', sans-serif !important;
}

section[data-testid="stSidebar"] .stButton > button {
    text-align: right;
    justify-content: flex-start;
    margin-bottom: 8px;
    border-radius: 12px;
    padding: 10px 16px;
    font-weight: 700;
    font-family: 'Cairo', sans-serif !important;
    transition: all 0.2s ease;
    width: 100%;
}

section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    background: #FFFFFF !important;
    color: var(--text-main) !important;
    border: 1px solid #E7E5E4 !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
}

section[data-testid="stSidebar"] .stButton > button[kind="secondary"] * {
    color: var(--text-main) !important;
    font-family: 'Cairo', sans-serif !important;
}

section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
    background: #F5F5F4 !important;
    border-color: #D6D3D1 !important;
    transform: translateY(-1px);
}

section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: var(--primary) !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.35);
}

section[data-testid="stSidebar"] .stButton > button[kind="primary"] * {
    color: #FFFFFF !important;
    font-family: 'Cairo', sans-serif !important;
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

/* KPI Cards */
.kpi-card {
    background: var(--card-bg);
    border-radius: 16px;
    padding: 18px 20px;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--card-border);
    display: flex;
    align-items: center;
    gap: 16px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.kpi-icon {
    width: 52px;
    height: 52px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    flex-shrink: 0;
    background: var(--primary-light);
    color: var(--primary-dark);
}

.kpi-value {
    font-size: 22px;
    font-weight: 800;
    color: var(--text-main);
    line-height: 1.1;
    font-family: 'Cairo', sans-serif !important;
}

.kpi-label {
    font-size: 13px;
    color: var(--text-muted);
    margin-top: 4px;
    font-family: 'Cairo', sans-serif !important;
}

/* Form inputs styling */
div[data-testid="stForm"] {
    background: var(--card-bg);
    border-radius: 16px;
    padding: 22px 24px;
    border: 1px solid var(--card-border);
    box-shadow: var(--shadow-sm);
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
        padding: 14px 16px;
        border-radius: 14px;
        gap: 12px;
    }
    .kpi-icon { width: 44px; height: 44px; font-size: 20px; border-radius: 10px; }
    .kpi-value { font-size: 18px; }
    .kpi-label { font-size: 12px; }

    .stButton > button {
        width: 100%;
        min-height: 44px;
    }
}
</style>
"""