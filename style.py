"""style.py — Central CSS for Streamlit App. Professional RTL layout with a warm, modern palette."""

CSS = """
<style>
/* ---------------------------------------------------------------- */
/* Google Fonts Import for Clean Arabic / RTL Typography            */
/* ---------------------------------------------------------------- */
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Vazirmatn:wght@400;500;700&display=swap');

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
/* GLOBAL FONT & RTL OVERRIDE                                       */
/* Target all text elements EXCEPT Streamlit Icon Containers        */
/* ---------------------------------------------------------------- */
html, body, [class*="css"],
p, span:not([data-testid="stIconMaterial"]):not([class*="material"]), 
h1, h2, h3, h4, h5, h6, 
label, input, textarea, select, button,
div[data-baseweb="select"], .stMarkdown {
    font-family: 'Cairo', 'Vazirmatn', 'Segoe UI', -apple-system, BlinkMacSystemFont, 
                 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 
                 'Noto Color Emoji', sans-serif !important;
}

/* Ensure Streamlit Native Material Icons retain their icon font */
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
/* Sidebar Styling                                                 */
/* ---------------------------------------------------------------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--primary-dark) 0%, #022C22 100%);
    direction: RTL;
    border-left: 1px solid rgba(255, 255, 255, 0.08);
}

/* Target general sidebar text without overriding button contents */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span:not([data-testid="stIconMaterial"]),
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown {
    color: #FFFFFF;
}

/* Sidebar Brand Header */
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
}

.brand-box p {
    margin: 4px 0 0 0;
    font-size: 13px;
    color: rgba(255, 255, 255, 0.8) !important;
}

/* Sidebar Stats & Info Badges */
.sidebar-stat {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 12px;
    padding: 10px 14px;
    margin-bottom: 10px;
    font-size: 13px;
    color: #FFFFFF !important;
    backdrop-filter: blur(4px);
}

.sidebar-stat b {
    font-size: 17px;
    display: block;
    color: var(--primary-light) !important;
}

/* Sidebar Navigation Buttons */
section[data-testid="stSidebar"] .stButton > button {
    text-align: right;
    justify-content: flex-start;
    margin-bottom: 8px;
    border-radius: 12px;
    padding: 10px 16px;
    font-weight: 700;
    transition: all 0.2s ease;
    width: 100%;
}

/* Inactive/Secondary Sidebar Buttons (Dark Text on White Background) */
section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    background: #FFFFFF !important;
    color: var(--text-main) !important;
    border: 1px solid #E7E5E4 !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
}

section[data-testid="stSidebar"] .stButton > button[kind="secondary"] * {
    color: var(--text-main) !important;
}

section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
    background: #F5F5F4 !important;
    border-color: #D6D3D1 !important;
    transform: translateY(-1px);
}

/* Active/Primary Sidebar Button */
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: var(--primary) !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.35);
}

section[data-testid="stSidebar"] .stButton > button[kind="primary"] * {
    color: #FFFFFF !important;
}

/* ---------------------------------------------------------------- */
/* Content Headings & Titles                                        */
/* ---------------------------------------------------------------- */
h1, h2, h3, h4 {
    color: var(--text-main);
    font-weight: 700;
}

.section-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 24px;
    font-weight: 800;
    color: var(--text-main);
    margin-bottom: 4px;
}

.section-sub {
    color: var(--text-muted);
    margin-bottom: 20px;
    font-size: 14px;
}

/* ---------------------------------------------------------------- */
/* Containers & Card Components                                     */
/* ---------------------------------------------------------------- */
.card {
    background: var(--card-bg);
    border-radius: 16px;
    padding: 22px 24px;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--card-border);
    margin-bottom: 20px;
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.card:hover {
    box-shadow: var(--shadow-md);
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
    font-size: 24px;
    font-weight: 800;
    color: var(--text-main);
    line-height: 1.1;
}

.kpi-label {
    font-size: 13px;
    color: var(--text-muted);
    margin-top: 2px;
}

/* Standard Badges */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    background: var(--primary-light);
    color: var(--primary-dark);
}

/* Receipt Display Component */
.receipt-box {
    background: #FFFBEB;
    border: 2px dashed var(--amber-gold);
    border-radius: 16px;
    padding: 24px;
    font-size: 15px;
    line-height: 2;
    box-shadow: var(--shadow-sm);
}

.receipt-box h3 {
    margin-top: 0;
    color: var(--primary-dark);
    font-weight: 800;
}

.receipt-row {
    display: flex;
    justify-content: space-between;
    border-bottom: 1px dotted #FDE68A;
    padding: 6px 0;
}

/* Form Styles */
div[data-testid="stForm"] {
    background: var(--card-bg);
    border-radius: 16px;
    padding: 22px 24px;
    border: 1px solid var(--card-border);
    box-shadow: var(--shadow-sm);
}

.required::after {
    content: " *";
    color: var(--coral-pink);
}

/* Streamlit Main Body Overrides */
div[data-testid="stMetricValue"] {
    color: var(--primary-dark);
    font-weight: 800;
}

.stButton > button {
    border-radius: 10px;
    font-weight: 600;
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
/* Mobile Responsiveness                                            */
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
    .kpi-value { font-size: 20px; }
    .kpi-label { font-size: 12px; }

    .card { padding: 16px; border-radius: 14px; }
    div[data-testid="stForm"] { padding: 16px; border-radius: 14px; }

    .receipt-box { padding: 18px; font-size: 14px; }

    /* Touch-friendly input heights & buttons for mobile */
    .stButton > button,
    div[data-testid="stFormSubmitButton"] button {
        width: 100%;
        min-height: 48px;
        font-size: 15px;
    }

    input, textarea, select,
    div[data-baseweb="select"] > div {
        font-size: 16px !important;
        min-height: 44px;
    }

    section[data-testid="stSidebar"] .stButton > button {
        padding: 12px 16px;
        font-size: 14px;
    }

    div[data-testid="stDataFrame"] {
        overflow-x: auto;
    }
}

@media (max-width: 480px) {
    .kpi-value { font-size: 18px; }
    .section-title { font-size: 18px; }
    div[data-testid="column"] {
        min-width: 100% !important;
    }
}
</style>
"""