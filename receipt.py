"""
receipt.py — printable cash receipt with a real "طباعة" button and an
official letterhead (logo + kindergarten name) at the top.

Renders two copies on the same page (School Copy & Payer Copy) separated by a cut line.
"""

import streamlit.components.v1 as components

import ui

RECEIPT_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

    :root {{
        --primary-dark:#163D22;
        --gold:#D7A431;
    }}
    * {{ 
        box-sizing: border-box; 
        font-family: 'Cairo', 'Segoe UI', Tahoma, sans-serif;
    }}
    body {{
        direction: rtl;
        text-align: right;
        margin: 0;
        padding: 10px;
        background: #FAF9F5;
    }}
    .page-container {{
        max-width: 520px;
        margin: 0 auto;
    }}
    .letterhead {{
        display: flex; 
        align-items: center; 
        justify-content: center; 
        gap: 10px;
        margin-bottom: 6px;
    }}
    .letterhead img {{ 
        width: 42px; 
        height: 42px; 
        border-radius: 50%; 
        flex-shrink: 0; 
    }}
    .letterhead-text {{ text-align: center; }}
    .letterhead-text .lh-ar {{ font-size: 14px; font-weight: 800; color: var(--primary-dark); }}
    .letterhead-text .lh-en {{ font-size: 10px; color: #7C8A7E; }}
    
    .receipt-box {{
        background: #FFFDF6;
        border: 2px dashed var(--gold);
        border-radius: 12px;
        padding: 12px 16px;
        font-size: 13px;
        line-height: 1.6;
        position: relative;
    }}
    .receipt-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px dashed var(--gold);
        padding-bottom: 6px;
        margin-bottom: 8px;
    }}
    .receipt-header h3 {{
        margin: 0;
        color: var(--primary-dark);
        font-size: 15px;
    }}
    .copy-badge {{
        background: var(--primary-dark);
        color: #FFFDF6;
        font-size: 11px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 6px;
    }}
    .receipt-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 4px 12px;
    }}
    .receipt-row {{
        display: flex; 
        justify-content: space-between; 
        gap: 6px;
        border-bottom: 1px dotted #e5e0c8; 
        padding: 3px 0;
    }}
    .receipt-row.full-width {{
        grid-column: span 2;
    }}
    .receipt-row span {{ color: #7C8A7E; white-space: nowrap; }}
    .receipt-row b {{ color: #1F2A22; }}
    .receipt-row.balance {{ 
        border-bottom: none; 
        margin-top: 2px; 
        padding-top: 6px; 
        border-top: 1px solid #e5e0c8; 
    }}
    .receipt-row.balance b {{ color: #B4790C; font-size: 14px; }}
    
    .cut-line {{
        display: flex;
        align-items: center;
        text-align: center;
        margin: 12px 0;
        color: #A3AD9E;
        font-size: 11px;
    }}
    .cut-line::before, .cut-line::after {{
        content: '';
        flex: 1;
        border-bottom: 1px dashed #A3AD9E;
    }}
    .cut-line::before {{ margin-left: .5em; }}
    .cut-line::after {{ margin-right: .5em; }}

    .print-btn {{
        display: block;
        width: 100%;
        max-width: 520px;
        margin: 14px auto 0 auto;
        background: var(--primary-dark);
        color: #fff;
        border: none;
        border-radius: 10px;
        padding: 10px 0;
        font-size: 14px;
        font-weight: 700;
        cursor: pointer;
    }}
    .print-btn:hover {{ opacity: .9; }}

    @media print {{
        .print-btn {{ display: none; }}
        body {{ background: #fff; padding: 0; }}
        .page-container {{ max-width: 100%; }}
        @page {{
            size: A4 portrait;
            margin: 8mm;
        }}
    }}
</style>
</head>
<body>
    <div class="page-container">
        <button class="print-btn" onclick="window.print()">🖨️ طباعة النسختين (A4)</button>

        <!-- ==================== COPY 1: SCHOOL ==================== -->
        <div class="receipt-box">
            <div class="letterhead">
                {logo_img_tag}
                <div class="letterhead-text">
                    <div class="lh-ar">روضة مؤسسة شباب البيرة</div>
                    <div class="lh-en">Al-Bireh Youth Foundation Kindergarten</div>
                </div>
            </div>
            <div class="receipt-header">
                <h3>🧾 وصل استلام نقدية</h3>
                <span class="copy-badge">نسخة المدرسة</span>
            </div>
            <div class="receipt-grid">
                <div class="receipt-row"><span>رقم الوصل:</span><b>#{receipt_id}</b></div>
                <div class="receipt-row"><span>التاريخ:</span><b>{date}</b></div>
                <div class="receipt-row full-width"><span>اسم الطالب:</span><b>{student_name}</b></div>
                <div class="receipt-row full-width"><span>وصلنا من السيد/ة:</span><b>{payer}</b></div>
                <div class="receipt-row"><span>مبلغ وقدره:</span><b>{amount} شيكل/دينار</b></div>
                <div class="receipt-row"><span>طريقة الدفع:</span><b>كاش 💵</b></div>
                <div class="receipt-row full-width"><span>مقابل:</span><b>{reason}</b></div>
                <div class="receipt-row full-width balance"><span>المبلغ المتبقي لهذه السنة:</span><b>{remaining} شيكل/دينار</b></div>
            </div>
        </div>

        <!-- ==================== CUT LINE ==================== -->
        <div class="cut-line">✂️ خط القص</div>

        <!-- ==================== COPY 2: PAYER ==================== -->
        <div class="receipt-box">
            <div class="letterhead">
                {logo_img_tag}
                <div class="letterhead-text">
                    <div class="lh-ar">روضة مؤسسة شباب البيرة</div>
                    <div class="lh-en">Al-Bireh Youth Foundation Kindergarten</div>
                </div>
            </div>
            <div class="receipt-header">
                <h3>🧾 وصل استلام نقدية</h3>
                <span class="copy-badge">نسخة ولي الأمر</span>
            </div>
            <div class="receipt-grid">
                <div class="receipt-row"><span>رقم الوصل:</span><b>#{receipt_id}</b></div>
                <div class="receipt-row"><span>التاريخ:</span><b>{date}</b></div>
                <div class="receipt-row full-width"><span>اسم الطالب:</span><b>{student_name}</b></div>
                <div class="receipt-row full-width"><span>وصلنا من السيد/ة:</span><b>{payer}</b></div>
                <div class="receipt-row"><span>مبلغ وقدره:</span><b>{amount} شيكل/دينار</b></div>
                <div class="receipt-row"><span>طريقة الدفع:</span><b>كاش 💵</b></div>
                <div class="receipt-row full-width"><span>مقابل:</span><b>{reason}</b></div>
                <div class="receipt-row full-width balance"><span>المبلغ المتبقي لهذه السنة:</span><b>{remaining} شيكل/دينار</b></div>
            </div>
        </div>
    </div>
</body>
</html>
"""


def render_receipt(receipt_id, date, student_name, payer, amount, reason, remaining, reason_other=""):
    reason_full = f"{reason} ({reason_other})" if reason_other else reason

    logo_b64 = ui._logo_base64()
    logo_img_tag = f'<img src="data:image/png;base64,{logo_b64}" />' if logo_b64 else ""

    html = RECEIPT_TEMPLATE.format(
        logo_img_tag=logo_img_tag,
        receipt_id=receipt_id,
        date=date,
        student_name=student_name,
        payer=payer,
        amount=amount,
        reason=reason_full,
        remaining=remaining,
    )
    # Height updated to 820px to comfortably display both copies in the Streamlit iframe
    components.html(html, height=820, scrolling=True)