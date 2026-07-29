"""
style.py — Central CSS for Streamlit App with Cairo typography, RTL support, and Modern Card Design.
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
    --primary-light: #ECFDF5;
    
    /* Modern Kindergarten Warm Palette */
    --coral-pink: #F43F5E;
    --amber-gold: #F59E0B;
    --soft-sky: #3B82F6;
    
    /* Neutrals & Surfaces */
    --bg: #F8FAFC;
    --card-bg: #FFFFFF;
    --card-border: #E2E8F0;
    --text-main: #0F172A;
    --text-muted: #64748B;
    
    /* Elevation Shadows */
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.08), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
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
/* LOGIN PAGE & CARD CONTAINER STYLING                              */
/* ---------------------------------------------------------------- */

/* Login Logo Centering */
.login-logo {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 12px;
}

.login-logo img {
    border-radius: 50%;
    box-shadow: var(--shadow-sm);
    padding: 6px;
    background: #FFFFFF;
    border: 1px solid var(--card-border);
}

/* Header Text Alignments inside Login Box */
.login-header {
    text-align: center;
    margin-bottom: 24px;
}

.login-header h2 {
    font-size: 24px;
    font-weight: 800 !important;
    color: var(--primary-dark);
    margin: 0 0 4px 0;
}

.login-header p.sub-en {
    font-size: 13px;
    color: var(--text-muted);
    direction: ltr;
    margin: 0 0 12px 0;
    font-weight: 500;
}

.login-badge {
    display: inline-block;
    background: var(--primary-light);
    color: var(--primary-dark);
    font-size: 13px;
    font-weight: 700;
    padding: 4px 14px;
    border-radius: 20px;
    border: 1px solid rgba(16, 185, 129, 0.2);
}

/* Form Container Refinement: Remove double borders */
div[data-testid="stForm"] {
    background: var(--card-bg) !important;
    border-radius: 20px !important;
    padding: 32px 28px !important;
    border: 1px solid var(--card-border) !important;
    box-shadow: var(--shadow-xl) !important;
}

/* Input Fields inside Forms */
div[data-testid="stForm"] div[data-baseweb="input"] {
    border-radius: 12px !important;
    background-color: #F8FAFC !important;
    border: 1px solid #E2E8F0 !important;
    transition: all 0.2s ease-in-out;
}

div[data-testid="stForm"] div[data-baseweb="input"]:focus-within {
    border-color: var(--primary) !important;
    background-color: #FFFFFF !important;
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15) !important;
}

div[data-testid="stForm"] label {
    font-size: 14px !important;
    font-weight: 700 !important;
    color: var(--text-main) !important;
    margin-bottom: 6px !important;
}

/* Submit Button in Form */
div[data-testid="stForm"] .stButton > button {
    background: var(--primary) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 12px !important;
    height: 48px !important;
    font-size: 16px !important;
    font-weight: 800 !important;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25) !important;
    margin-top: 12px !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stForm"] .stButton > button:hover {
    background: var(--primary-dark) !important;
    box-shadow: 0 6px 16px rgba(6, 78, 59, 0.3) !important;
    transform: translateY(-1px);
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

div[data-testid="stHeadingWithHeadline"] a {
    order: 2 !important;
    opacity: 0.3;
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

/* ---------------------------------------------------------------- */
/* MOBILE RESPONSIVENESS                                            */
/* ---------------------------------------------------------------- */
@media (max-width: 768px) {
    div[data-testid="stForm"] {
        padding: 24px 18px !important;
    }
}


/* ---------------------------------------------------------------- */
/* LOGIN FORM CARD ENHANCEMENTS                                     */
/* ---------------------------------------------------------------- */

/* Login Header Text Styling */
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

/* Modern Card Styling for st.form */
div[data-testid="stForm"] {
    background: #FFFFFF !important;
    border-radius: 20px !important;
    padding: 32px 28px !important;
    border: 1px solid #E2E8F0 !important;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01) !important;
}

/* Styled Input Fields */
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

/* Button Refinement */
div[data-testid="stForm"] .stButton > button {
    background: #10B981 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 12px !important;
    height: 46px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25) !important;
    margin-top: 10px !important;
}

div[data-testid="stForm"] .stButton > button:hover {
    background: #064E3B !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(6, 78, 59, 0.25) !important;
}

</style>
"""