"""style.py — central CSS for the app. Professional layout, warm kindergarten palette."""

CSS = """
<style>
:root{
    --primary:#219044;
    --primary-dark:#163D22;
    --pink:#E62031;
    --yellow:#D7A431;
    --mint:#219044;
    --bg:#FAF9F5;
    --card:#FFFFFF;
    --text:#1F2A22;
    --muted:#7C8A7E;
    --border:#EAF0E9;
}

html, body, [class*="css"] {
    direction: RTL;
    text-align: right;
    font-family: 'Segoe UI', 'Tahoma', sans-serif;
}

.stApp { background: var(--bg); }

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--primary) 0%, var(--primary-dark) 100%);
    direction: RTL;
}
section[data-testid="stSidebar"] * { color: #FFFFFF !important; }

/* Nav buttons (replaces the old radio menu) */
section[data-testid="stSidebar"] .nav-stack{ margin-bottom: 4px; }
section[data-testid="stSidebar"] .stButton>button{
    text-align: right;
    justify-content: flex-start;
    margin-bottom: 6px;
    transition: all .15s ease;
}
section[data-testid="stSidebar"] .stButton>button[kind="secondary"]{
    background: rgba(255,255,255,0.08);
    color: #fff !important;
    border: 1px solid rgba(255,255,255,0.14);
    font-weight: 600;
}
section[data-testid="stSidebar"] .stButton>button[kind="secondary"]:hover{
    background: rgba(255,255,255,0.20);
    border-color: rgba(255,255,255,0.3);
}
section[data-testid="stSidebar"] .stButton>button[kind="primary"]{
    background: #FFFFFF;
    color: var(--primary-dark) !important;
    border: none;
    font-weight: 800;
    box-shadow: 0 3px 10px rgba(0,0,0,.18);
}
section[data-testid="stSidebar"] .stButton>button[kind="primary"] * { color: var(--primary-dark) !important; }

.brand-box{
    text-align:center;
    padding: 6px 0 18px 0;
    border-bottom: 1px solid rgba(255,255,255,.18);
    margin-bottom: 14px;
}
.brand-box h2{ margin:0; font-size:22px; }
.brand-box p{ margin:2px 0 0 0; font-size:12.5px; opacity:.85; }

.sidebar-stat{
    background: rgba(255,255,255,.10);
    border-radius: 10px;
    padding: 8px 12px;
    margin-bottom: 8px;
    font-size: 13px;
}
.sidebar-stat b{ font-size:16px; display:block; }

h1, h2, h3 { color: var(--text); }

.section-title{
    display:flex; align-items:center; gap:10px;
    font-size:26px; font-weight:800; color:var(--text);
    margin-bottom: 2px;
}
.section-sub{ color: var(--muted); margin-bottom: 18px; font-size: 14px;}

/* KPI cards */
.kpi-card{
    background: var(--card);
    border-radius: 16px;
    padding: 18px 20px;
    box-shadow: 0 4px 14px rgba(60,60,130,.08);
    border: 1px solid var(--border);
    display:flex; align-items:center; gap:14px;
}
.kpi-icon{
    width:46px; height:46px; border-radius:12px;
    display:flex; align-items:center; justify-content:center;
    font-size:22px; flex-shrink:0;
}
.kpi-value{ font-size:22px; font-weight:800; color:var(--text); line-height:1.2;}
.kpi-label{ font-size:13px; color:var(--muted); }

.card{
    background: var(--card);
    border-radius: 16px;
    padding: 20px 22px;
    box-shadow: 0 4px 14px rgba(60,60,130,.06);
    border: 1px solid var(--border);
    margin-bottom: 16px;
}

.badge{
    display:inline-block; padding:4px 12px; border-radius:20px;
    font-size:12.5px; font-weight:700;
}

.receipt-box{
    background: #FFFDF6;
    border: 2px dashed var(--yellow);
    border-radius: 14px;
    padding: 22px 26px;
    font-size: 15px;
    line-height: 2;
}
.receipt-box h3{ margin-top:0; color: var(--primary-dark); }
.receipt-row{ display:flex; justify-content:space-between; border-bottom:1px dotted #e5e0c8; padding:4px 0; }

.required::after{ content:" *"; color:#E5484D; }

div[data-testid="stMetricValue"]{ color: var(--primary-dark); }

.stButton>button{
    border-radius: 10px;
    font-weight:600;
}
.stButton>button[kind="primary"]{
    background: var(--primary);
    border-color: var(--primary);
}

div[data-testid="stForm"]{
    background: var(--card);
    border-radius:16px;
    padding: 18px 20px 6px 20px;
    border: 1px solid var(--border);
}

/* ---------------------------------------------------------------- */
/* Mobile responsiveness                                            */
/* ---------------------------------------------------------------- */
@media (max-width: 768px) {
    .block-container{
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 1.2rem !important;
    }

    .section-title{ font-size: 21px; gap:8px; }
    .section-sub{ font-size: 13px; margin-bottom: 12px; }

    .kpi-card{
        padding: 12px 14px;
        border-radius: 12px;
        gap: 10px;
    }
    .kpi-icon{ width:38px; height:38px; font-size:18px; border-radius:10px; }
    .kpi-value{ font-size: 18px; }
    .kpi-label{ font-size: 12px; }

    .card{ padding: 14px 14px; border-radius: 12px; }

    div[data-testid="stForm"]{ padding: 14px 14px 2px 14px; border-radius: 12px; }

    .receipt-box{ padding: 16px 16px; font-size: 13.5px; }
    .receipt-row{ flex-direction: row; flex-wrap: wrap; gap: 2px; }

    .brand-box h2{ font-size: 17px; }
    .brand-box p{ font-size: 11px; }
    .sidebar-stat{ font-size: 12px; padding: 7px 10px; }
    .sidebar-stat b{ font-size: 14px; }

    /* Bigger, full-width, easy-to-tap buttons */
    .stButton>button,
    div[data-testid="stFormSubmitButton"] button{
        width: 100%;
        min-height: 46px;
        font-size: 15px;
    }

    /* Inputs: comfortable tap height, no iOS zoom-in on focus */
    input, textarea, select,
    div[data-baseweb="select"] > div{
        font-size: 16px !important;
        min-height: 42px;
    }

    section[data-testid="stSidebar"] .stButton>button{
        padding: 12px 14px;
        font-size: 14.5px;
    }

    h1 { font-size: 24px !important; }
    h2 { font-size: 20px !important; }
    h3 { font-size: 17px !important; }

    /* Let wide tables scroll horizontally instead of squeezing/breaking */
    div[data-testid="stDataFrame"]{
        overflow-x: auto;
    }
}

@media (max-width: 480px) {
    .kpi-value{ font-size: 16px; }
    .section-title{ font-size: 19px; }
    div[data-testid="column"]{
        min-width: 100% !important;
    }
}
</style>
"""
