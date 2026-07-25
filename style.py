"""style.py — central CSS for the app. Professional layout, warm kindergarten palette."""

CSS = """
<style>
:root{
    --primary:#5B5FEF;
    --primary-dark:#4347C4;
    --pink:#FF8FAB;
    --yellow:#FFC94D;
    --mint:#12B886;
    --bg:#F5F6FB;
    --card:#FFFFFF;
    --text:#2B2A4A;
    --muted:#8A8AA3;
    --border:#ECEDF7;
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
section[data-testid="stSidebar"] .stRadio > label { color:#fff !important; }
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 6px;
    transition: all .15s ease;
    display:flex;
    width:100%;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(255,255,255,0.18);
}

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
</style>
"""
